"""Fail-closed NVIDIA capability adapter for MCT/GARAS.

The adapter treats NVIDIA services as evidence providers, never as quorum members
or execution authorities. Availability is discovered from explicit runtime
configuration and optional health probes. Missing/unreachable services fail
closed and never fabricate results.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Mapping


class CapabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    INSTALLED_NOT_CONFIGURED = "INSTALLED_NOT_CONFIGURED"
    UNREACHABLE = "UNREACHABLE"
    NOT_FOUND = "NOT_FOUND"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Capability:
    component: str
    catalog_skill: str
    installed: bool
    reachable: bool | None
    version: str | None
    endpoint: str | None
    auth_required: bool
    write_capability: bool
    execution_capability: bool
    evidence_source: str
    status: CapabilityStatus


@dataclass(frozen=True)
class EvidenceContext:
    trace_id: str | None = None
    proposal_id: str | None = None
    head_sha: str | None = None


HealthProbe = Callable[[str, Mapping[str, str]], bool | None]
Transport = Callable[[str, str, Mapping[str, Any], Mapping[str, str]], Mapping[str, Any]]


class NvidiaCapabilityAdapter:
    """MCT-facing NVIDIA evidence adapter.

    Important invariants:
    - NVIDIA is not a Brain/quorum member.
    - NVIDIA output never authorizes merge or execution.
    - Network calls only happen through injected probe/transport functions.
    - Missing or ambiguous backend state fails closed.
    """

    BACKENDS: Mapping[str, Mapping[str, Any]] = {
        "evaluator": {
            "catalog_skill": "nemo-evaluator-plugin",
            "endpoint_env": "NVIDIA_NEMO_EVALUATOR_URL",
            "version_env": "NVIDIA_NEMO_EVALUATOR_VERSION",
            "auth_required": True,
            "write_capability": False,
            "execution_capability": False,
        },
        "retriever": {
            "catalog_skill": "nemo-retriever",
            "endpoint_env": "NVIDIA_NEMO_RETRIEVER_URL",
            "version_env": "NVIDIA_NEMO_RETRIEVER_VERSION",
            "auth_required": True,
            "write_capability": False,
            "execution_capability": False,
        },
        "policy": {
            "catalog_skill": "nemotron-policy-generator",
            "endpoint_env": "NVIDIA_NEMOTRON_POLICY_URL",
            "version_env": "NVIDIA_NEMOTRON_POLICY_VERSION",
            "auth_required": True,
            "write_capability": False,
            "execution_capability": False,
        },
        "relay": {
            "catalog_skill": "nemo-relay-get-started",
            "endpoint_env": "NVIDIA_NEMO_RELAY_URL",
            "version_env": "NVIDIA_NEMO_RELAY_VERSION",
            "auth_required": True,
            "write_capability": False,
            "execution_capability": False,
        },
        "nim": {
            "catalog_skill": "NIM runtime",
            "endpoint_env": "NVIDIA_NIM_BASE_URL",
            "version_env": "NVIDIA_NIM_VERSION",
            "auth_required": True,
            "write_capability": False,
            "execution_capability": False,
        },
    }

    OPERATION_BACKEND = {
        "evaluate": "evaluator",
        "retrieve": "retriever",
        "guard": "policy",
        "infer": "nim",
    }

    def __init__(
        self,
        *,
        environ: Mapping[str, str] | None = None,
        health_probe: HealthProbe | None = None,
        transport: Transport | None = None,
    ) -> None:
        self._env = dict(os.environ if environ is None else environ)
        self._health_probe = health_probe
        self._transport = transport

    def _auth_headers(self) -> dict[str, str]:
        key = self._env.get("NVIDIA_API_KEY") or self._env.get("NGC_API_KEY")
        if not key:
            return {}
        return {"Authorization": f"Bearer {key}"}

    def discover(self) -> dict[str, Capability]:
        """Return a machine-readable capability matrix without guessing."""
        headers = self._auth_headers()
        matrix: dict[str, Capability] = {}
        for component, spec in self.BACKENDS.items():
            endpoint = self._env.get(spec["endpoint_env"])
            version = self._env.get(spec["version_env"])
            auth_required = bool(spec["auth_required"])
            auth_ready = bool(headers) or not auth_required

            if not endpoint:
                status = CapabilityStatus.NOT_FOUND
                reachable: bool | None = None
                source = f"catalog:{spec['catalog_skill']};runtime:endpoint-missing"
            elif not auth_ready:
                status = CapabilityStatus.INSTALLED_NOT_CONFIGURED
                reachable = None
                source = f"env:{spec['endpoint_env']};auth:missing"
            elif self._health_probe is None:
                status = CapabilityStatus.UNKNOWN
                reachable = None
                source = f"env:{spec['endpoint_env']};probe:not-configured"
            else:
                try:
                    probe_result = self._health_probe(endpoint, headers)
                except Exception:
                    probe_result = False
                if probe_result is True:
                    status = CapabilityStatus.AVAILABLE
                    reachable = True
                elif probe_result is False:
                    status = CapabilityStatus.UNREACHABLE
                    reachable = False
                else:
                    status = CapabilityStatus.UNKNOWN
                    reachable = None
                source = f"env:{spec['endpoint_env']};probe:injected"

            matrix[component] = Capability(
                component=component,
                catalog_skill=str(spec["catalog_skill"]),
                installed=endpoint is not None,
                reachable=reachable,
                version=version,
                endpoint=endpoint,
                auth_required=auth_required,
                write_capability=bool(spec["write_capability"]),
                execution_capability=bool(spec["execution_capability"]),
                evidence_source=source,
                status=status,
            )
        return matrix

    def capabilities(self) -> dict[str, dict[str, Any]]:
        return {
            name: {**asdict(cap), "status": cap.status.value}
            for name, cap in self.discover().items()
        }

    def health(self) -> dict[str, Any]:
        matrix = self.discover()
        return {
            "available": sorted(
                name for name, cap in matrix.items()
                if cap.status is CapabilityStatus.AVAILABLE
            ),
            "blocked": {
                name: cap.status.value
                for name, cap in matrix.items()
                if cap.status is not CapabilityStatus.AVAILABLE
            },
            "execution_authorized": False,
            "quorum_member": False,
        }

    @staticmethod
    def _hash(value: Any) -> str:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )

    def _blocked_result(
        self,
        operation: str,
        backend: str,
        payload: Mapping[str, Any],
        context: EvidenceContext,
        status: CapabilityStatus,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "provider": "NVIDIA",
            "backend": backend,
            "operation": operation,
            "status": status.value,
            "ok": False,
            "timestamp": self._timestamp(),
            "input_hash": self._hash(payload),
            "output_hash": None,
            "trace_id": context.trace_id,
            "proposal_id": context.proposal_id,
            "head_sha": context.head_sha,
            "quorum_member": False,
            "vote": None,
            "merge_authorized": False,
            "execution_authorized": False,
            "output": None,
        }
        if operation == "guard":
            result["decision"] = "deny"
            result["reason"] = "nvidia_guard_backend_not_available"
        return result

    def _invoke(
        self,
        operation: str,
        payload: Mapping[str, Any],
        *,
        context: EvidenceContext | None = None,
    ) -> dict[str, Any]:
        context = context or EvidenceContext()
        backend = self.OPERATION_BACKEND[operation]
        capability = self.discover()[backend]
        if capability.status is not CapabilityStatus.AVAILABLE:
            return self._blocked_result(
                operation, backend, payload, context, capability.status
            )
        if self._transport is None:
            return self._blocked_result(
                operation, backend, payload, context, CapabilityStatus.UNKNOWN
            )

        headers = self._auth_headers()
        try:
            output = dict(self._transport(backend, operation, payload, headers))
        except Exception as exc:
            blocked = self._blocked_result(
                operation, backend, payload, context, CapabilityStatus.UNREACHABLE
            )
            blocked["error_type"] = type(exc).__name__
            return blocked

        result = {
            "provider": "NVIDIA",
            "backend": backend,
            "catalog_skill": capability.catalog_skill,
            "version": capability.version,
            "operation": operation,
            "status": CapabilityStatus.AVAILABLE.value,
            "ok": True,
            "timestamp": self._timestamp(),
            "input_hash": self._hash(payload),
            "output_hash": self._hash(output),
            "trace_id": context.trace_id,
            "proposal_id": context.proposal_id,
            "head_sha": context.head_sha,
            "quorum_member": False,
            "vote": None,
            "merge_authorized": False,
            "execution_authorized": False,
            "output": output,
        }
        if operation == "guard":
            raw_decision = str(output.get("decision", "")).lower()
            result["decision"] = "allow" if raw_decision == "allow" else "deny"
            if result["decision"] != "allow":
                result["reason"] = output.get("reason", "policy_denied")
        return result

    def infer(
        self,
        payload: Mapping[str, Any],
        *,
        context: EvidenceContext | None = None,
    ) -> dict[str, Any]:
        return self._invoke("infer", payload, context=context)

    def evaluate(
        self,
        payload: Mapping[str, Any],
        *,
        context: EvidenceContext | None = None,
    ) -> dict[str, Any]:
        return self._invoke("evaluate", payload, context=context)

    def retrieve(
        self,
        payload: Mapping[str, Any],
        *,
        context: EvidenceContext | None = None,
    ) -> dict[str, Any]:
        return self._invoke("retrieve", payload, context=context)

    def guard(
        self,
        payload: Mapping[str, Any],
        *,
        context: EvidenceContext | None = None,
    ) -> dict[str, Any]:
        return self._invoke("guard", payload, context=context)
