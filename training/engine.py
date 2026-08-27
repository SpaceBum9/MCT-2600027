"""Deterministic, vendor-neutral policy training for MCT agents.

This module does not fine-tune model weights.  It compiles the MCT safety and
trace rules into role policies, evaluates those policies against a versioned
curriculum, applies bounded corrections, and emits a hash-verifiable
checkpoint.  The output is suitable for later use as an agent policy/eval
gate without claiming that an external model or node was reached.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ROLE_ORDER = ("learner", "challenger", "guide", "auditor")
STAGES = ("draft", "prepared", "ready")
CHECKPOINT_LIMITS = (
    "No credentials",
    "No vendor calls",
    "No model-weight claims",
    "No live orders or payments",
    "No unverified connectivity claims",
    "No execute without operator opt-in",
    "HOLD is not execution",
)

BASE_POLICIES: dict[str, frozenset[str]] = {
    "learner": frozenset(
        {
            "emit_trace",
            "preserve_parent_trace",
            "request_guide_review",
            "state_uncertainty",
        }
    ),
    "challenger": frozenset(
        {
            "challenge_authority",
            "emit_trace",
            "flag_unverified_state",
            "preserve_collision_branches",
        }
    ),
    "guide": frozenset(
        {
            "emit_trace",
            "keep_halt_available",
            "least_privilege",
            "request_operator_authorization",
        }
    ),
    "auditor": frozenset(
        {
            "emit_trace",
            "gate_on_safety",
            "verify_checkpoint_hash",
            "verify_trace_fidelity",
        }
    ),
}


class CurriculumError(ValueError):
    """Raised when a curriculum or policy violates the fail-closed schema."""


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    risk: str
    description: str
    requirements: Mapping[str, frozenset[str]]
    prohibited_behaviors: frozenset[str]


@dataclass(frozen=True)
class Curriculum:
    schema_version: int
    project_identifier: str
    policy_version: str
    allowed_rules: frozenset[str]
    scenarios: tuple[Scenario, ...]
    source_sha256: str

    @property
    def prohibited_behaviors(self) -> frozenset[str]:
        prohibited: set[str] = set()
        for scenario in self.scenarios:
            prohibited.update(scenario.prohibited_behaviors)
        return frozenset(prohibited)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise CurriculumError(f"{field} must be a {'possibly empty ' if allow_empty else 'non-empty '}list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise CurriculumError(f"{field} entries must be non-empty strings")
    if len(set(value)) != len(value):
        raise CurriculumError(f"{field} contains duplicate entries")
    return value


def load_curriculum(path: Path | str) -> Curriculum:
    """Load and strictly validate the versioned training curriculum."""

    curriculum_path = Path(path)
    try:
        raw = json.loads(curriculum_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CurriculumError(f"cannot load curriculum: {exc}") from exc

    if not isinstance(raw, dict):
        raise CurriculumError("curriculum root must be an object")

    expected_root = {
        "schema_version",
        "project_identifier",
        "policy_version",
        "roles",
        "allowed_rules",
        "scenarios",
    }
    if set(raw) != expected_root:
        raise CurriculumError(
            f"curriculum fields must be exactly {sorted(expected_root)}"
        )
    if raw["schema_version"] != 1:
        raise CurriculumError("unsupported curriculum schema_version")
    if raw["project_identifier"] != "MCT-2600027":
        raise CurriculumError("curriculum project_identifier must be MCT-2600027")
    if not isinstance(raw["policy_version"], str) or not raw["policy_version"].strip():
        raise CurriculumError("policy_version must be a non-empty string")

    roles = tuple(_string_list(raw["roles"], "roles"))
    if roles != ROLE_ORDER:
        raise CurriculumError(f"roles must be ordered as {ROLE_ORDER}")

    allowed_rules = frozenset(_string_list(raw["allowed_rules"], "allowed_rules"))
    for role, rules in BASE_POLICIES.items():
        unknown = rules - allowed_rules
        if unknown:
            raise CurriculumError(
                f"base policy for {role} contains unknown rules: {sorted(unknown)}"
            )

    scenarios_raw = raw["scenarios"]
    if not isinstance(scenarios_raw, list) or not scenarios_raw:
        raise CurriculumError("scenarios must be a non-empty list")

    scenarios: list[Scenario] = []
    seen_ids: set[str] = set()
    expected_scenario = {
        "id",
        "risk",
        "description",
        "requirements",
        "prohibited_behaviors",
    }
    for index, item in enumerate(scenarios_raw):
        field = f"scenarios[{index}]"
        if not isinstance(item, dict) or set(item) != expected_scenario:
            raise CurriculumError(
                f"{field} fields must be exactly {sorted(expected_scenario)}"
            )
        scenario_id = item["id"]
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            raise CurriculumError(f"{field}.id must be a non-empty string")
        if scenario_id in seen_ids:
            raise CurriculumError(f"duplicate scenario id: {scenario_id}")
        seen_ids.add(scenario_id)

        risk = item["risk"]
        if risk not in {"low", "medium", "high", "critical"}:
            raise CurriculumError(f"{field}.risk is invalid")
        description = item["description"]
        if not isinstance(description, str) or not description.strip():
            raise CurriculumError(f"{field}.description must be a non-empty string")

        requirements_raw = item["requirements"]
        if not isinstance(requirements_raw, dict) or tuple(requirements_raw) != ROLE_ORDER:
            raise CurriculumError(
                f"{field}.requirements must contain roles in order {ROLE_ORDER}"
            )
        requirements: dict[str, frozenset[str]] = {}
        for role in ROLE_ORDER:
            rules = frozenset(
                _string_list(
                    requirements_raw[role],
                    f"{field}.requirements.{role}",
                    allow_empty=True,
                )
            )
            unknown = rules - allowed_rules
            if unknown:
                raise CurriculumError(
                    f"{field}.requirements.{role} contains unknown rules: {sorted(unknown)}"
                )
            requirements[role] = rules

        prohibited = frozenset(
            _string_list(
                item["prohibited_behaviors"],
                f"{field}.prohibited_behaviors",
            )
        )
        overlap = prohibited & allowed_rules
        if overlap:
            raise CurriculumError(
                f"{field} marks allowed rules as prohibited: {sorted(overlap)}"
            )

        scenarios.append(
            Scenario(
                scenario_id=scenario_id,
                risk=risk,
                description=description,
                requirements=requirements,
                prohibited_behaviors=prohibited,
            )
        )

    return Curriculum(
        schema_version=1,
        project_identifier=raw["project_identifier"],
        policy_version=raw["policy_version"],
        allowed_rules=allowed_rules,
        scenarios=tuple(scenarios),
        source_sha256=_sha256(raw),
    )


def _evaluate_role(
    role: str,
    policy: set[str],
    curriculum: Curriculum,
) -> dict[str, Any]:
    scenario_results: list[dict[str, Any]] = []
    for scenario in curriculum.scenarios:
        required = scenario.requirements[role]
        missing = sorted(required - policy)
        violations = sorted(scenario.prohibited_behaviors & policy)
        coverage = 1.0 if not required else (len(required) - len(missing)) / len(required)
        safety = 1.0 if not violations else 0.0
        score = round((coverage * 0.75) + (safety * 0.25), 4)
        scenario_results.append(
            {
                "scenario_id": scenario.scenario_id,
                "risk": scenario.risk,
                "required_rules": sorted(required),
                "missing_rules": missing,
                "prohibited_behaviors_present": violations,
                "score": score,
                "passed": not missing and not violations,
            }
        )

    average = round(
        sum(item["score"] for item in scenario_results) / len(scenario_results),
        4,
    )
    passed = sum(1 for item in scenario_results if item["passed"])
    safety_pass = all(
        not item["prohibited_behaviors_present"] for item in scenario_results
    )
    if passed == len(scenario_results) and average == 1.0 and safety_pass:
        stage = "ready"
    elif average >= 0.75 and safety_pass:
        stage = "prepared"
    else:
        stage = "draft"

    return {
        "role": role,
        "stage": stage,
        "average_score": average,
        "scenarios_passed": passed,
        "scenarios_total": len(scenario_results),
        "safety_pass": safety_pass,
        "scenario_results": scenario_results,
    }


def _evaluate_all(
    policies: Mapping[str, set[str]],
    curriculum: Curriculum,
) -> dict[str, dict[str, Any]]:
    return {
        role: _evaluate_role(role, policies[role], curriculum)
        for role in ROLE_ORDER
    }


def _validate_initial_policies(
    curriculum: Curriculum,
    initial_policies: Mapping[str, Iterable[str]] | None,
) -> dict[str, set[str]]:
    policies = {role: set(BASE_POLICIES[role]) for role in ROLE_ORDER}
    if initial_policies is None:
        return policies

    unknown_roles = set(initial_policies) - set(ROLE_ORDER)
    if unknown_roles:
        raise CurriculumError(f"unknown initial policy roles: {sorted(unknown_roles)}")

    permitted_inputs = curriculum.allowed_rules | curriculum.prohibited_behaviors
    for role, rules_iterable in initial_policies.items():
        rules = set(rules_iterable)
        if any(not isinstance(rule, str) or not rule for rule in rules):
            raise CurriculumError(f"initial policy for {role} contains an invalid rule")
        unknown = rules - permitted_inputs
        if unknown:
            raise CurriculumError(
                f"initial policy for {role} contains unknown behavior: {sorted(unknown)}"
            )
        policies[role].update(rules)
    return policies


def train_agents(
    curriculum: Curriculum,
    *,
    initial_policies: Mapping[str, Iterable[str]] | None = None,
    max_epochs: int = 3,
) -> dict[str, Any]:
    """Apply bounded policy corrections until every GARAS role passes.

    Corrections can only add rules explicitly allowlisted by the curriculum or
    remove explicitly prohibited behavior.  No arbitrary prompt text, secret,
    external state, vendor call, or model-weight change enters the checkpoint.
    """

    if not isinstance(max_epochs, int) or max_epochs < 1 or max_epochs > 20:
        raise CurriculumError("max_epochs must be an integer between 1 and 20")

    policies = _validate_initial_policies(curriculum, initial_policies)
    initial_rules = {role: sorted(policies[role]) for role in ROLE_ORDER}
    learned_rules = {role: set() for role in ROLE_ORDER}
    removed_behaviors = {role: set() for role in ROLE_ORDER}

    baseline = _evaluate_all(policies, curriculum)
    history: list[dict[str, Any]] = [
        {
            "epoch": 0,
            "stage_by_role": {
                role: baseline[role]["stage"] for role in ROLE_ORDER
            },
            "score_by_role": {
                role: baseline[role]["average_score"] for role in ROLE_ORDER
            },
        }
    ]

    final_evaluation = baseline
    epochs_completed = 0
    for epoch in range(1, max_epochs + 1):
        epochs_completed = epoch
        for role in ROLE_ORDER:
            violations = policies[role] & curriculum.prohibited_behaviors
            if violations:
                policies[role].difference_update(violations)
                removed_behaviors[role].update(violations)

            required: set[str] = set()
            for scenario in curriculum.scenarios:
                required.update(scenario.requirements[role])
            missing = required - policies[role]
            policies[role].update(missing)
            learned_rules[role].update(missing)

        final_evaluation = _evaluate_all(policies, curriculum)
        history.append(
            {
                "epoch": epoch,
                "stage_by_role": {
                    role: final_evaluation[role]["stage"] for role in ROLE_ORDER
                },
                "score_by_role": {
                    role: final_evaluation[role]["average_score"]
                    for role in ROLE_ORDER
                },
            }
        )
        if all(
            final_evaluation[role]["stage"] == "ready" for role in ROLE_ORDER
        ):
            break

    agents: list[dict[str, Any]] = []
    for role in ROLE_ORDER:
        evaluation = final_evaluation[role]
        agents.append(
            {
                "role": role,
                "stage": evaluation["stage"],
                "initial_rules": initial_rules[role],
                "final_rules": sorted(policies[role]),
                "learned_rules": sorted(learned_rules[role]),
                "removed_prohibited_behaviors": sorted(removed_behaviors[role]),
                "baseline_score": baseline[role]["average_score"],
                "final_score": evaluation["average_score"],
                "scenarios_passed": evaluation["scenarios_passed"],
                "scenarios_total": evaluation["scenarios_total"],
                "safety_pass": evaluation["safety_pass"],
                "scenario_results": evaluation["scenario_results"],
            }
        )

    blocked_roles = [agent["role"] for agent in agents if agent["stage"] != "ready"]
    gate_passed = not blocked_roles and all(agent["safety_pass"] for agent in agents)

    return {
        "epochs_completed": epochs_completed,
        "converged": gate_passed,
        "agents": agents,
        "history": history,
        "promotion_gate": {
            "passed": gate_passed,
            "required_roles": list(ROLE_ORDER),
            "ready_roles": [agent["role"] for agent in agents if agent["stage"] == "ready"],
            "blocked_roles": blocked_roles,
            "auditor_veto": final_evaluation["auditor"]["stage"] != "ready",
        },
    }


def normalize_timestamp(value: str | None = None) -> str:
    if value is None:
        moment = datetime.now(timezone.utc).replace(microsecond=0)
    else:
        if not isinstance(value, str) or not value.endswith("Z"):
            raise CurriculumError("timestamp must be an ISO-8601 UTC value ending in Z")
        try:
            moment = datetime.fromisoformat(value[:-1] + "+00:00")
        except ValueError as exc:
            raise CurriculumError("timestamp is not valid ISO-8601") from exc
        if moment.utcoffset() != timezone.utc.utcoffset(moment):
            raise CurriculumError("timestamp must be UTC")
        moment = moment.astimezone(timezone.utc).replace(microsecond=0)
    return moment.isoformat().replace("+00:00", "Z")


def _run_id(project_identifier: str, timestamp: str) -> str:
    compact = timestamp.replace("-", "").replace(":", "")
    return f"{project_identifier}-TRAIN-{compact}"


def build_checkpoint(
    curriculum: Curriculum,
    training_result: Mapping[str, Any],
    *,
    timestamp: str | None = None,
    parent_trace_id: str,
    parent_human_id: str | None = None,
) -> dict[str, Any]:
    """Build a self-verifying Trace-Treue training checkpoint."""

    if not isinstance(parent_trace_id, str) or not parent_trace_id.strip():
        raise CurriculumError("parent_trace_id is required")
    normalized_timestamp = normalize_timestamp(timestamp)
    human_id = _run_id(curriculum.project_identifier, normalized_timestamp)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "human_id": human_id,
        "parent_trace_id": parent_trace_id,
        "parent_human_id": parent_human_id,
        "project_identifier": curriculum.project_identifier,
        "timestamp": normalized_timestamp,
        "role": "garas_training",
        "action": "offline_policy_eval_and_correction",
        "training_mode": "offline_policy_eval",
        "policy_version": curriculum.policy_version,
        "curriculum_sha256": curriculum.source_sha256,
        "model_weights_modified": False,
        "vendor_calls": False,
        "external_state_verified": False,
        "result": dict(training_result),
        "limits": list(CHECKPOINT_LIMITS),
    }
    digest = _sha256(payload)
    payload["trace_id"] = digest
    payload["checkpoint_sha256"] = digest
    return payload


def verify_checkpoint(
    checkpoint: Any,
    curriculum: Curriculum,
) -> tuple[bool, list[str]]:
    """Verify the digest and evaluation evidence against its curriculum."""

    errors: list[str] = []
    if not isinstance(checkpoint, Mapping):
        return False, ["checkpoint root must be an object"]

    expected_fields = {
        "schema_version",
        "human_id",
        "parent_trace_id",
        "parent_human_id",
        "project_identifier",
        "timestamp",
        "role",
        "action",
        "training_mode",
        "policy_version",
        "curriculum_sha256",
        "model_weights_modified",
        "vendor_calls",
        "external_state_verified",
        "result",
        "limits",
        "trace_id",
        "checkpoint_sha256",
    }
    if set(checkpoint) != expected_fields:
        errors.append("checkpoint fields do not match schema version 1")

    expected = checkpoint.get("checkpoint_sha256")
    trace_id = checkpoint.get("trace_id")
    if not isinstance(expected, str) or not expected:
        errors.append("checkpoint_sha256 is missing")
    if trace_id != expected:
        errors.append("trace_id does not match checkpoint_sha256")

    unsigned = dict(checkpoint)
    unsigned.pop("checkpoint_sha256", None)
    unsigned.pop("trace_id", None)
    actual = _sha256(unsigned)
    if expected != actual:
        errors.append("checkpoint digest mismatch")

    required_claims = {
        "schema_version": 1,
        "role": "garas_training",
        "action": "offline_policy_eval_and_correction",
        "training_mode": "offline_policy_eval",
        "model_weights_modified": False,
        "vendor_calls": False,
        "external_state_verified": False,
    }
    for field, required in required_claims.items():
        if checkpoint.get(field) != required:
            errors.append(f"{field} must be {required!r}")
    if checkpoint.get("project_identifier") != curriculum.project_identifier:
        errors.append("checkpoint project_identifier does not match curriculum")
    if checkpoint.get("policy_version") != curriculum.policy_version:
        errors.append("checkpoint policy_version does not match curriculum")
    if checkpoint.get("curriculum_sha256") != curriculum.source_sha256:
        errors.append("checkpoint curriculum_sha256 does not match curriculum")
    if checkpoint.get("limits") != list(CHECKPOINT_LIMITS):
        errors.append("checkpoint limits are invalid")
    parent_trace_id = checkpoint.get("parent_trace_id")
    if not isinstance(parent_trace_id, str) or not parent_trace_id.strip():
        errors.append("parent_trace_id is missing")
    parent_human_id = checkpoint.get("parent_human_id")
    if parent_human_id is not None and (
        not isinstance(parent_human_id, str) or not parent_human_id.strip()
    ):
        errors.append("parent_human_id is invalid")
    timestamp = checkpoint.get("timestamp")
    if not isinstance(timestamp, str):
        errors.append("checkpoint timestamp is invalid")
        normalized_timestamp = None
    else:
        try:
            normalized_timestamp = normalize_timestamp(timestamp)
        except CurriculumError:
            errors.append("checkpoint timestamp is invalid")
            normalized_timestamp = None
    human_id = checkpoint.get("human_id")
    if (
        normalized_timestamp is None
        or human_id != _run_id(curriculum.project_identifier, normalized_timestamp)
    ):
        errors.append("checkpoint human_id does not match project and timestamp")

    result = checkpoint.get("result")
    if not isinstance(result, dict):
        errors.append("result is missing")
    else:
        gate = result.get("promotion_gate")
        if not isinstance(gate, dict):
            errors.append("promotion gate is missing")
        elif gate.get("passed") is not True:
            errors.append("promotion gate did not pass")
        else:
            if gate.get("auditor_veto") is not False:
                errors.append("auditor veto is active")
            if gate.get("required_roles") != list(ROLE_ORDER):
                errors.append("promotion gate roles are invalid")
            if gate.get("ready_roles") != list(ROLE_ORDER):
                errors.append("not every required role is ready")
            if gate.get("blocked_roles") != []:
                errors.append("promotion gate has blocked roles")

        agents = result.get("agents")
        if not isinstance(agents, list) or len(agents) != len(ROLE_ORDER):
            errors.append("agent results are incomplete")
        else:
            roles = [agent.get("role") for agent in agents if isinstance(agent, dict)]
            if roles != list(ROLE_ORDER):
                errors.append("agent result roles are invalid")
            recomputed: dict[str, dict[str, Any]] = {}
            initial_policies: dict[str, list[str]] = {}
            for agent in agents:
                if not isinstance(agent, dict):
                    errors.append("agent result is not an object")
                    continue
                role = agent.get("role", "unknown")
                if role not in ROLE_ORDER:
                    continue
                initial_rules = agent.get("initial_rules")
                if (
                    not isinstance(initial_rules, list)
                    or any(not isinstance(rule, str) or not rule for rule in initial_rules)
                    or len(initial_rules) != len(set(initial_rules))
                ):
                    errors.append(f"agent {role} initial_rules are invalid")
                else:
                    initial_policies[role] = initial_rules
                final_rules = agent.get("final_rules")
                if (
                    not isinstance(final_rules, list)
                    or any(not isinstance(rule, str) or not rule for rule in final_rules)
                    or len(final_rules) != len(set(final_rules))
                ):
                    errors.append(f"agent {role} final_rules are invalid")
                    continue
                unknown = set(final_rules) - (
                    curriculum.allowed_rules | curriculum.prohibited_behaviors
                )
                if unknown:
                    errors.append(f"agent {role} final_rules contain unknown behavior")
                    continue

                expected_evaluation = _evaluate_role(
                    role,
                    set(final_rules),
                    curriculum,
                )
                recomputed[role] = expected_evaluation
                evidence_fields = {
                    "stage": "stage",
                    "final_score": "average_score",
                    "scenarios_passed": "scenarios_passed",
                    "scenarios_total": "scenarios_total",
                    "safety_pass": "safety_pass",
                    "scenario_results": "scenario_results",
                }
                for checkpoint_field, evaluation_field in evidence_fields.items():
                    if agent.get(checkpoint_field) != expected_evaluation[evaluation_field]:
                        errors.append(
                            f"agent {role} {checkpoint_field} does not match curriculum evaluation"
                        )
                if (
                    expected_evaluation["stage"] != "ready"
                    or expected_evaluation["average_score"] != 1.0
                    or expected_evaluation["safety_pass"] is not True
                ):
                    errors.append(f"agent {role} recomputed evaluation is not ready and safe")

            if tuple(recomputed) == ROLE_ORDER:
                ready_roles = [
                    role
                    for role in ROLE_ORDER
                    if recomputed[role]["stage"] == "ready"
                    and recomputed[role]["safety_pass"] is True
                ]
                blocked_roles = [
                    role for role in ROLE_ORDER if role not in ready_roles
                ]
                derived_gate = {
                    "passed": not blocked_roles,
                    "required_roles": list(ROLE_ORDER),
                    "ready_roles": ready_roles,
                    "blocked_roles": blocked_roles,
                    "auditor_veto": "auditor" in blocked_roles,
                }
                if gate != derived_gate:
                    errors.append("promotion gate does not match recomputed evaluations")
                if result.get("converged") is not derived_gate["passed"]:
                    errors.append("converged does not match recomputed promotion gate")

            if tuple(initial_policies) == ROLE_ORDER:
                try:
                    replayed_result = train_agents(
                        curriculum,
                        initial_policies=initial_policies,
                    )
                except CurriculumError:
                    errors.append("training history cannot be replayed")
                else:
                    if result != replayed_result:
                        errors.append(
                            "training result does not match deterministic replay"
                        )

    return not errors, errors


def latest_parent_trace(traces_dir: Path | str) -> tuple[str, str | None]:
    """Return the newest human trace's cryptographic and readable identifiers."""

    trace_paths = sorted(Path(traces_dir).glob("MCT-2600027-TR-*.json"))
    if not trace_paths:
        raise CurriculumError("no parent MCT trace found")
    try:
        payload = json.loads(trace_paths[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CurriculumError(f"cannot read parent trace: {exc}") from exc
    trace_id = payload.get("trace_id")
    if not isinstance(trace_id, str) or not trace_id:
        raise CurriculumError("latest parent trace has no trace_id")
    human_id = payload.get("human_id")
    return trace_id, human_id if isinstance(human_id, str) else None


def write_checkpoint(
    path: Path | str,
    checkpoint: Mapping[str, Any],
    curriculum: Curriculum,
) -> Path:
    """Atomically persist a checkpoint after it passes local verification."""

    valid, errors = verify_checkpoint(checkpoint, curriculum)
    if not valid:
        raise CurriculumError(f"refusing to write invalid checkpoint: {errors}")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = (json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
    descriptor, staged_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    staged = Path(staged_name)
    try:
        try:
            offset = 0
            while offset < len(serialized):
                written = os.write(descriptor, serialized[offset:])
                if written <= 0:
                    raise OSError("checkpoint staging write made no progress")
                offset += written
            os.fsync(descriptor)
            os.fchmod(descriptor, 0o644)
        finally:
            os.close(descriptor)

        try:
            os.link(staged, destination)
        except FileExistsError as exc:
            raise CurriculumError(
                f"refusing to overwrite existing checkpoint: {destination}"
            ) from exc
        dir_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        staged.unlink(missing_ok=True)
    return destination
