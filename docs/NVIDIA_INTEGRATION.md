# NVIDIA capability integration

This integration adds NVIDIA as an evidence/capability layer beneath MCT/GARAS.
It does not make NVIDIA a Brain/quorum member and it does not grant execution
authority.

## Discovery sources

The NVIDIA skills catalog currently exposes relevant Agentic AI entries such as:

- `nemo-evaluator-plugin`
- `nemo-retriever`
- `nemotron-policy-generator`
- `nemo-relay-get-started`
- NIM-related runtime workflows

The ChatGPT environment used to prepare this slice exposes the NVIDIA skill
finder plus BioNeMo-oriented skills. Those are not treated as proof that NeMo
Evaluator/Retriever/Relay services are reachable from this repository runtime.

Therefore the adapter only marks a backend AVAILABLE when explicit runtime
configuration exists and an injected health probe verifies reachability.

## Runtime configuration

Supported environment variables:

- `NVIDIA_API_KEY` or `NGC_API_KEY`
- `NVIDIA_NEMO_EVALUATOR_URL`
- `NVIDIA_NEMO_EVALUATOR_VERSION`
- `NVIDIA_NEMO_RETRIEVER_URL`
- `NVIDIA_NEMO_RETRIEVER_VERSION`
- `NVIDIA_NEMOTRON_POLICY_URL`
- `NVIDIA_NEMOTRON_POLICY_VERSION`
- `NVIDIA_NEMO_RELAY_URL`
- `NVIDIA_NEMO_RELAY_VERSION`
- `NVIDIA_NIM_BASE_URL`
- `NVIDIA_NIM_VERSION`

Credentials are read from the process environment only. The adapter does not
persist, trace, or print secret values.

## Status model

Every backend resolves to exactly one state:

- `AVAILABLE`
- `INSTALLED_NOT_CONFIGURED`
- `UNREACHABLE`
- `NOT_FOUND`
- `UNKNOWN`

No network access is implicit. Health probing and request transport are injected
by the runtime. Without them, the adapter reports UNKNOWN/blocked rather than
pretending success.

## MCT/GARAS governance

NVIDIA results are evidence only.

Hard invariants:

- NVIDIA is not a quorum member.
- NVIDIA cannot emit GPT/Grok ballots.
- NVIDIA cannot authorize merges.
- NVIDIA cannot authorize execution.
- Missing/ambiguous guard backends default to `deny`.
- Tool/service failures do not change LIVE_RAIL, HOLD, vendor, relay, or execute
  state.
- Evidence can carry `trace_id`, `proposal_id`, and exact `head_sha` binding.
- Inputs and outputs are SHA-256 hashed in the evidence envelope.

## Adapter operations

`NvidiaCapabilityAdapter` exposes:

- `discover()`
- `capabilities()`
- `health()`
- `infer()`
- `evaluate()`
- `retrieve()`
- `guard()`

The transport is deliberately abstract. A later slice can bind verified NVIDIA
NIM/NeMo endpoints without changing MCT's authorization boundary.

## Current boundary

This slice changes observation/evidence plumbing only.

It does not:

- install NVIDIA services,
- activate a vendor,
- enable a relay,
- merge a pull request,
- execute external actions,
- change existing LIVE_RAIL/default/HOLD semantics.
