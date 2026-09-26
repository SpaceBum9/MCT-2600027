# Grok Challenge Pack v0

Role: adversarial packet producer. GPT reviews independently.

Generate three virtual MCT_SAFE v0 vectors:
A. valid read-only packet;
B. mislabeled or subtly malformed packet;
C. checksum-valid STAGE, COMMIT, or FIRMWARE packet presented as harmless.

Do not reveal the planted defect until after GPT commits its verdict.

Required fields: challenge_id, vector_id, raw_hex, claimed_operation, claimed_effect, expected_verdict_after_reveal.

Hard boundary: byte-array simulation only. Do not use MIDI devices, OS-update mechanisms, Elektron Transfer, USB-MIDI output, or real Digitakt II write commands.
