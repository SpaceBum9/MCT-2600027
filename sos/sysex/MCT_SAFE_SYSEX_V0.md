# MCT_SAFE SysEx v0 — Virtual Guardrail Protocol

Status: EXPERIMENTAL / SIMULATION ONLY

This specification defines a virtual SysEx-shaped protocol for adversarial guardrail testing. It is **not** an Elektron/Digitakt II protocol and MUST NOT be transmitted to hardware.

## Authority boundary

- hardware_io: DENIED
- transmit: false
- persistent_write: false
- firmware_write: false
- execute: false

A valid frame never implies authorization.

## Virtual frame

```
F0 7D 4D 43 54 VV OP FL LL [PAYLOAD...] CC F7
```

- `7D`: educational/non-commercial SysEx manufacturer ID, used here only in simulation fixtures.
- `4D 43 54`: ASCII `MCT` namespace marker.
- `VV`: protocol version, v0 = `00`.
- `OP`: operation.
- `FL`: flags.
- `LL`: payload length, 0..127.
- `CC`: virtual checksum = sum of bytes VV..payload modulo 128.

All bytes between F0/F7 MUST be 7-bit.

## Operations

- `01 CAPS?` read-only
- `02 STATE?` read-only
- `03 PATTERN?` read-only
- `10 DIFF` simulation-only
- `11 SIMULATE` simulation-only
- `20 STAGE` denied in v0
- `21 VERIFY` simulation-only
- `22 COMMIT` denied in v0
- `23 ROLLBACK` simulation-only
- `70 FIRMWARE` always denied

## Verdicts

`ALLOW_ANALYZE`, `ALLOW_SIMULATE`, `HOLD_UNKNOWN`, `DENY_WRITE`.

Unknown opcode, malformed framing, model ambiguity, checksum failure, trailing/concatenated data, persistent-write intent, or firmware/bootloader intent cannot escalate authority.

## Adversarial invariants

1. Claimed metadata is untrusted.
2. Parser classification comes from bytes, not labels.
3. Checksum-valid != safe.
4. Known opcode != authorized.
5. STAGE/COMMIT/FIRMWARE remain DENY_WRITE.
6. Parser MUST preserve and hash original bytes before any normalization.
7. No fixture or test may open MIDI ports.
8. Tests operate on byte arrays only.

This v0 intentionally avoids real Digitakt II manufacturer/model/command bytes. Real-device mapping is a separate reviewed layer.
