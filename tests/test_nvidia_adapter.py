from __future__ import annotations

import unittest

from integrations.nvidia_adapter import (
    CapabilityStatus,
    EvidenceContext,
    NvidiaCapabilityAdapter,
)


class NvidiaCapabilityAdapterTests(unittest.TestCase):
    def test_missing_backends_are_not_fabricated(self) -> None:
        adapter = NvidiaCapabilityAdapter(environ={})
        caps = adapter.capabilities()
        self.assertTrue(caps)
        self.assertTrue(
            all(item["status"] == CapabilityStatus.NOT_FOUND.value for item in caps.values())
        )
        self.assertFalse(adapter.health()["execution_authorized"])
        self.assertFalse(adapter.health()["quorum_member"])

    def test_endpoint_without_key_is_not_configured(self) -> None:
        adapter = NvidiaCapabilityAdapter(
            environ={"NVIDIA_NEMO_EVALUATOR_URL": "https://example.invalid/evaluator"}
        )
        cap = adapter.discover()["evaluator"]
        self.assertEqual(cap.status, CapabilityStatus.INSTALLED_NOT_CONFIGURED)
        self.assertIsNone(cap.reachable)

    def test_endpoint_and_key_without_probe_remain_unknown(self) -> None:
        adapter = NvidiaCapabilityAdapter(
            environ={
                "NVIDIA_NEMO_EVALUATOR_URL": "https://example.invalid/evaluator",
                "NVIDIA_API_KEY": "secret",
            }
        )
        cap = adapter.discover()["evaluator"]
        self.assertEqual(cap.status, CapabilityStatus.UNKNOWN)
        self.assertIsNone(cap.reachable)

    def test_probe_can_mark_backend_available(self) -> None:
        adapter = NvidiaCapabilityAdapter(
            environ={
                "NVIDIA_NEMO_EVALUATOR_URL": "https://example.invalid/evaluator",
                "NVIDIA_API_KEY": "secret",
            },
            health_probe=lambda endpoint, headers: True,
        )
        cap = adapter.discover()["evaluator"]
        self.assertEqual(cap.status, CapabilityStatus.AVAILABLE)
        self.assertTrue(cap.reachable)

    def test_unavailable_evaluator_fails_closed(self) -> None:
        adapter = NvidiaCapabilityAdapter(environ={})
        result = adapter.evaluate(
            {"claim": "merge is safe"},
            context=EvidenceContext(
                trace_id="trace-1",
                proposal_id="proposal-1",
                head_sha="deadbeef",
            ),
        )
        self.assertFalse(result["ok"])
        self.assertIsNone(result["vote"])
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(result["proposal_id"], "proposal-1")
        self.assertEqual(result["head_sha"], "deadbeef")

    def test_unavailable_guard_defaults_to_deny(self) -> None:
        adapter = NvidiaCapabilityAdapter(environ={})
        result = adapter.guard({"action": "merge"})
        self.assertFalse(result["ok"])
        self.assertEqual(result["decision"], "deny")
        self.assertFalse(result["execution_authorized"])

    def test_transport_output_is_evidence_not_authorization(self) -> None:
        def transport(backend, operation, payload, headers):
            self.assertEqual(backend, "evaluator")
            self.assertEqual(operation, "evaluate")
            self.assertIn("Authorization", headers)
            return {"grounding": 0.98, "decision": "pass"}

        adapter = NvidiaCapabilityAdapter(
            environ={
                "NVIDIA_NEMO_EVALUATOR_URL": "https://example.invalid/evaluator",
                "NVIDIA_API_KEY": "secret",
                "NVIDIA_NEMO_EVALUATOR_VERSION": "test",
            },
            health_probe=lambda endpoint, headers: True,
            transport=transport,
        )
        result = adapter.evaluate(
            {"statement": "evidence"},
            context=EvidenceContext(proposal_id="p", head_sha="abc"),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"]["grounding"], 0.98)
        self.assertIsNone(result["vote"])
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(result["proposal_id"], "p")
        self.assertEqual(result["head_sha"], "abc")
        self.assertIsNotNone(result["input_hash"])
        self.assertIsNotNone(result["output_hash"])

    def test_guard_transport_cannot_smuggle_execution_authority(self) -> None:
        adapter = NvidiaCapabilityAdapter(
            environ={
                "NVIDIA_NEMOTRON_POLICY_URL": "https://example.invalid/policy",
                "NVIDIA_API_KEY": "secret",
            },
            health_probe=lambda endpoint, headers: True,
            transport=lambda backend, operation, payload, headers: {
                "decision": "allow",
                "execution_authorized": True,
                "vote": "ja",
            },
        )
        result = adapter.guard({"action": "review"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["decision"], "allow")
        self.assertIsNone(result["vote"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["merge_authorized"])


if __name__ == "__main__":
    unittest.main()
