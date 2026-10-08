from __future__ import annotations

import copy
import json
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from core.orchestrator import Orchestrator
from integrations.nvidia_adapter import NvidiaCapabilityAdapter


POLICY = Path(__file__).resolve().parents[1] / "skills" / "default-mode.json"
ENDPOINT = "https://example.invalid/evaluator"
TEST_ENV = {
    "NVIDIA_NEMO_EVALUATOR_URL": ENDPOINT,
    "NVIDIA_API_KEY": "test-only-key",
}


class OrchestratorNvidiaTests(unittest.TestCase):
    def setUp(self) -> None:
        # No inherited endpoint or credential may enter this integration test.
        self.environment = patch.dict(os.environ, TEST_ENV, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.policy_bytes = POLICY.read_bytes()
        self.policy = json.loads(self.policy_bytes)
        self.assertTrue(self.policy["live_rail"])
        self.assertTrue(self.policy["LIVE_RAIL"])
        self.assertEqual(self.policy["default"], "denied")
        self.assertFalse(self.policy["execute"])
        self.assertTrue(self.policy["hold"])
        self.assertFalse(self.policy["vendor_live"])

    def held_orchestrator(self, adapter=None):
        orchestrator = Orchestrator(nvidia_adapter=adapter)
        orchestrator.zero.hold(reason="integration-test")
        self.assertEqual(orchestrator.border.get_state()["state"], "HOLDING")
        return orchestrator

    def snapshot(self, orchestrator):
        # Capture real runtime state independently of status()/NVIDIA health.
        return copy.deepcopy({
            "border": orchestrator.border.get_state(),
            "records": orchestrator.trace_store.all_records(),
            "collisions": orchestrator.trace_store.list_collisions(),
            "open_collisions": orchestrator.collision_handler.list_open_collisions(),
            "quarantine": orchestrator.collision_handler.list_quarantine(),
            "treue": orchestrator.treue.summary(),
            "environment": dict(os.environ),
        })

    def assert_unchanged(self, orchestrator, before):
        self.assertEqual(self.snapshot(orchestrator), before)
        self.assertEqual(POLICY.read_bytes(), self.policy_bytes)
        self.assertEqual(json.loads(POLICY.read_bytes()), self.policy)

    def assert_health_boundary(self, health):
        self.assertFalse(health["execution_authorized"])
        self.assertFalse(health["quorum_member"])

    def test_default_configured_endpoint_has_no_implicit_probe(self):
        orchestrator = self.held_orchestrator()
        before = self.snapshot(orchestrator)
        status = orchestrator.status()
        self.assertEqual(status["nvidia"]["available"], [])
        self.assertEqual(status["nvidia"]["blocked"]["evaluator"], "UNKNOWN")
        self.assertEqual(status["border"], before["border"])
        self.assert_health_boundary(status["nvidia"])
        self.assert_unchanged(orchestrator, before)

    def test_injected_probe_is_visible_without_transport_or_state_changes(self):
        probe = Mock(return_value=True)
        transport = Mock(side_effect=AssertionError("status must not invoke transport"))
        adapter = NvidiaCapabilityAdapter(
            environ=TEST_ENV, health_probe=probe, transport=transport,
        )
        orchestrator = self.held_orchestrator(adapter)
        self.assertIs(orchestrator.nvidia, adapter)
        before = self.snapshot(orchestrator)
        first = orchestrator.status()
        second = orchestrator.status()
        self.assertEqual(first, second)
        self.assertEqual(first["nvidia"]["available"], ["evaluator"])
        self.assertNotIn("evaluator", first["nvidia"]["blocked"])
        self.assertEqual(probe.call_count, 2)
        probe.assert_called_with(ENDPOINT, {"Authorization": "Bearer test-only-key"})
        transport.assert_not_called()
        self.assert_health_boundary(first["nvidia"])
        self.assert_unchanged(orchestrator, before)

    def test_probe_failures_and_ambiguity_preserve_hold_and_policy(self):
        for outcome, expected in [(False, "UNREACHABLE"), (None, "UNKNOWN"),
                                  (RuntimeError("offline"), "UNREACHABLE")]:
            with self.subTest(expected=expected, outcome=repr(outcome)):
                probe = Mock(side_effect=outcome) if isinstance(outcome, Exception) else Mock(return_value=outcome)
                transport = Mock(side_effect=AssertionError("blocked backend"))
                adapter = NvidiaCapabilityAdapter(
                    environ=TEST_ENV, health_probe=probe, transport=transport,
                )
                orchestrator = self.held_orchestrator(adapter)
                before = self.snapshot(orchestrator)
                health = orchestrator.status()["nvidia"]
                self.assertEqual(health["available"], [])
                self.assertEqual(health["blocked"]["evaluator"], expected)
                self.assert_health_boundary(health)
                result = orchestrator.nvidia.evaluate({"claim": "test"})
                self.assertFalse(result["ok"])
                transport.assert_not_called()
                self.assert_unchanged(orchestrator, before)

    def test_injected_transport_returns_evidence_without_authority(self):
        probe = Mock(return_value=True)
        transport = Mock(return_value={
            "score": 0.9, "vote": "ja", "execution_authorized": True,
        })
        orchestrator = self.held_orchestrator(NvidiaCapabilityAdapter(
            environ=TEST_ENV, health_probe=probe, transport=transport,
        ))
        before = self.snapshot(orchestrator)
        self.assertEqual(orchestrator.status()["nvidia"]["available"], ["evaluator"])
        transport.assert_not_called()
        result = orchestrator.nvidia.evaluate({"claim": "test"})
        transport.assert_called_once_with(
            "evaluator", "evaluate", {"claim": "test"},
            {"Authorization": "Bearer test-only-key"},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["output"]["score"], 0.9)
        self.assertIsNone(result["vote"])
        self.assertFalse(result["quorum_member"])
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["execution_authorized"])
        self.assert_unchanged(orchestrator, before)

    def test_guard_transport_exception_denies_without_changing_state(self):
        env = {
            "NVIDIA_NEMOTRON_POLICY_URL": "https://example.invalid/policy",
            "NVIDIA_API_KEY": "test-only-key",
        }
        transport = Mock(side_effect=RuntimeError("offline"))
        orchestrator = self.held_orchestrator(NvidiaCapabilityAdapter(
            environ=env, health_probe=Mock(return_value=True), transport=transport,
        ))
        before = self.snapshot(orchestrator)
        self.assertEqual(orchestrator.status()["nvidia"]["available"], ["policy"])
        transport.assert_not_called()
        result = orchestrator.nvidia.guard({"action": "review"})
        self.assertEqual(transport.call_count, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "UNREACHABLE")
        self.assertEqual(result["decision"], "deny")
        self.assertIsNone(result["vote"])
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["execution_authorized"])
        self.assert_health_boundary(orchestrator.status()["nvidia"])
        self.assert_unchanged(orchestrator, before)


if __name__ == "__main__":
    unittest.main()
