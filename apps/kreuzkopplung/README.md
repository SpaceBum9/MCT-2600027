---
title: Kreuzkopplung
emoji: ~
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: "5.49.1"
app_file: app.py
pinned: false
license: mit
short_description: Adaptive two-channel DualEntangledSystem.run()
---

# Kreuzkopplung

Classical two-channel controller. Not quantum mechanics. Mix/balance loop with a cross-coupling matrix.

`DualEntangledSystem.run(inputs)` is implemented: each scalar is a `step`. Weights and coupling persist across the batch.

## Status

| Surface | State |
| --- | --- |
| GitHub `SpaceBum9/kreuzkopplung` | **source of truth** |
| Hugging Face `huggingface.co/SpaceBum9` | **ABSENT (404)** |
| Space `spaces/SpaceBum9/kreuzkopplung` | **not deployed** |

This repo is Gradio-import source only. Do not claim the Space is live until an operator imports it in the Hugging Face UI. No Hugging Face token in this repo.

## Install

```bash
pip install -r requirements.txt
python dual_entangled.py --steps 64
python app.py
```

## `run`

```python
from dual_entangled import DualEntangledSystem
import numpy as np

sys = DualEntangledSystem()
t = np.linspace(0, 4 * np.pi, 240)
outputs, telemetry = sys.run(np.sin(t))
# outputs.shape == (240, 2)
```

`reset=False` continues a previous series.

## Hugging Face import (operator, UI)

1. [New Space](https://huggingface.co/new-space)
2. Import from GitHub → `SpaceBum9/kreuzkopplung`
3. SDK: Gradio, `app_file`: `app.py`

Until that happens, status remains **absent**.

## License

MIT
