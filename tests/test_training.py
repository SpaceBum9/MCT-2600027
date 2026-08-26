from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from training.engine import (
    CurriculumError,
    _evaluate_role,
    build_checkpoint,
    load_curriculum,
    train_agents,
    verify_checkpoint,
)
from train_mct_agents import _verify


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "training" / "curriculum.json"


def _rehash_checkpoint(checkpoint: dict) -> None:
    unsigned = {
        key: value
        for key, value in checkpoint.items()
        if key not in {"trace_id", "checkpoint_sha256"}
    }
    digest = hashlib.sha256(
        json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    checkpoint["trace_id"] = digest
    checkpoint["checkpoint_sha256"] = digest


class TrainingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.curriculum = load_curriculum(CURRICULUM)

    def test_curriculum_is_bound_to_mct_and_garas_roles(self) -> None:
        self.assertEqual(self.curriculum.project_identifier, "MCT-2600027")
        self.assertEqual(
            tuple(role for role in ("learner", "challenger", "guide", "auditor")),
            tuple(self.curriculum.scenarios[0].requirements),
        )
        self.assertEqual(len(self.curriculum.scenarios), 8)

    def test_training_converges_without_vendor_or_weight_claims(self) -> None:
        result = train_agents(self.curriculum)
        self.assertTrue(result["converged"])
        self.assertEqual(result["epochs_completed"], 1)
        self.assertTrue(result["promotion_gate"]["passed"])
        self.assertFalse(result["promotion_gate"]["auditor_veto"])
        self.assertTrue(all(agent["stage"] == "ready" for agent in result["agents"]))
        self.assertTrue(all(agent["final_score"] == 1.0 for agent in result["agents"]))

    def test_prohibited_behavior_is_removed_during_training(self) -> None:
        result = train_agents(
            self.curriculum,
            initial_policies={"learner": ["execute_without_authorization"]},
        )
        learner = next(agent for agent in result["agents"] if agent["role"] == "learner")
        self.assertIn(
            "execute_without_authorization",
            learner["removed_prohibited_behaviors"],
        )
        self.assertNotIn("execute_without_authorization", learner["final_rules"])
        self.assertTrue(learner["safety_pass"])

    def test_unknown_behavior_fails_closed(self) -> None:
        with self.assertRaises(CurriculumError):
            train_agents(
                self.curriculum,
                initial_policies={"guide": ["invented_live_capability"]},
            )

    def test_checkpoint_hash_and_parent_are_verified(self) -> None:
        result = train_agents(self.curriculum)
        checkpoint = build_checkpoint(
            self.curriculum,
            result,
            timestamp="2026-08-23T19:00:00Z",
            parent_trace_id="parent-sha256",
            parent_human_id="MCT-2600027-TR-20260823-1812Z",
        )
        valid, errors = verify_checkpoint(checkpoint, self.curriculum)
        self.assertTrue(valid, errors)
        self.assertEqual(checkpoint["parent_trace_id"], "parent-sha256")
        self.assertEqual(checkpoint["trace_id"], checkpoint["checkpoint_sha256"])
        self.assertFalse(checkpoint["model_weights_modified"])
        self.assertFalse(checkpoint["vendor_calls"])
        self.assertFalse(checkpoint["external_state_verified"])

    def test_checkpoint_tampering_is_detected(self) -> None:
        checkpoint = build_checkpoint(
            self.curriculum,
            train_agents(self.curriculum),
            timestamp="2026-08-23T19:00:00Z",
            parent_trace_id="parent-sha256",
        )
        tampered = copy.deepcopy(checkpoint)
        tampered["result"]["agents"][0]["stage"] = "draft"
        valid, errors = verify_checkpoint(tampered, self.curriculum)
        self.assertFalse(valid)
        self.assertIn("checkpoint digest mismatch", errors)

    def test_malformed_promotion_gate_fails_without_crashing(self) -> None:
        checkpoint = build_checkpoint(
            self.curriculum,
            train_agents(self.curriculum),
            timestamp="2026-08-23T19:00:00Z",
            parent_trace_id="parent-sha256",
        )
        malformed = copy.deepcopy(checkpoint)
        malformed["result"]["promotion_gate"] = "ready"
        valid, errors = verify_checkpoint(malformed, self.curriculum)
        self.assertFalse(valid)
        self.assertIn("promotion gate is missing", errors)

    def test_rehashed_checkpoint_without_scenario_evidence_is_rejected(self) -> None:
        checkpoint = build_checkpoint(
            self.curriculum,
            train_agents(self.curriculum),
            timestamp="2026-08-23T19:00:00Z",
            parent_trace_id="parent-sha256",
        )
        stripped = copy.deepcopy(checkpoint)
        for agent in stripped["result"]["agents"]:
            agent["scenario_results"] = []
            agent["scenarios_passed"] = 0
            agent["scenarios_total"] = 0
        _rehash_checkpoint(stripped)

        valid, errors = verify_checkpoint(stripped, self.curriculum)

        self.assertFalse(valid)
        self.assertTrue(
            any("scenario_results does not match" in error for error in errors),
            errors,
        )

    def test_rehashed_unsafe_evaluation_cannot_keep_passing_gate(self) -> None:
        checkpoint = build_checkpoint(
            self.curriculum,
            train_agents(self.curriculum),
            timestamp="2026-08-23T19:00:00Z",
            parent_trace_id="parent-sha256",
        )
        forged = copy.deepcopy(checkpoint)
        learner = forged["result"]["agents"][0]
        learner["final_rules"].append("execute_without_authorization")
        evaluation = _evaluate_role(
            "learner",
            set(learner["final_rules"]),
            self.curriculum,
        )
        for checkpoint_field, evaluation_field in {
            "stage": "stage",
            "final_score": "average_score",
            "scenarios_passed": "scenarios_passed",
            "scenarios_total": "scenarios_total",
            "safety_pass": "safety_pass",
            "scenario_results": "scenario_results",
        }.items():
            learner[checkpoint_field] = evaluation[evaluation_field]
        _rehash_checkpoint(forged)

        valid, errors = verify_checkpoint(forged, self.curriculum)

        self.assertFalse(valid)
        self.assertIn(
            "agent learner recomputed evaluation is not ready and safe",
            errors,
        )
        self.assertIn(
            "promotion gate does not match recomputed evaluations",
            errors,
        )

    def test_rehashed_checkpoint_without_lineage_is_rejected(self) -> None:
        checkpoint = build_checkpoint(
            self.curriculum,
            train_agents(self.curriculum),
            timestamp="2026-08-23T19:00:00Z",
            parent_trace_id="parent-sha256",
        )
        stripped = copy.deepcopy(checkpoint)
        for field in ("parent_trace_id", "timestamp", "human_id"):
            stripped.pop(field)
        _rehash_checkpoint(stripped)

        valid, errors = verify_checkpoint(stripped, self.curriculum)

        self.assertFalse(valid)
        self.assertIn("parent_trace_id is missing", errors)
        self.assertIn("checkpoint timestamp is invalid", errors)
        self.assertIn(
            "checkpoint human_id does not match project and timestamp",
            errors,
        )

    def test_non_object_checkpoint_returns_structured_invalid_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            path.write_text("[]", encoding="utf-8")
            self.assertEqual(_verify(path, CURRICULUM), 2)


if __name__ == "__main__":
    unittest.main()
