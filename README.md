# mokarate-lora-train

ai-toolkit (ostris) LoRA training image for SaladCloud GPU training:
**mokarate_face_v1** — a face LoRA for モカラテ (locked face f6, seed
880306) trained on MOSS-Image-Base (`arch: moss_image:base`, ConvRot
INT8 quantization), so Kromoss generations can keep her face.

Contents:
- `Dockerfile` — `pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime` base,
  clones ostris/ai-toolkit and pip-installs its requirements, then bakes
  in the dataset, the training config, the file server and the
  entrypoint.
- `dataset/` — 21 PNG + 21 caption files (f6 originals + café, the
  8-angle Qwen multi-angle set, and the 8 extra Chroma scenes; the gym
  scene was excluded by ユウ's instruction because its leg expression
  looked odd).
- `mokarate_face_v1.yml` — sd_trainer LoRA config (rank 16, 2000 steps,
  layer 22 excluded via `ignore_if_contains`, matching the SLG skip).
- `server.py` / `entrypoint.sh` — the entrypoint starts a small file
  server first (so Salad's /ready probe passes and logs/checkpoints can
  be downloaded while training runs), runs `python run.py
  /app/mokarate_face_v1.yml`, writes a TRAINING_DONE marker with the
  exit code, and keeps serving files until the group is stopped.

Built by GitHub Actions (`.github/workflows/build.yml`): plain
`docker build` + push to GHCR under a per-run test tag, verification
(manifest size limits, ai-toolkit commit, dataset count, config files,
torch import), then promotion to the final tag by `crane copy` with a
digest-equality check.

Result: `ghcr.io/ththth-mokarate/mokarate-lora-train:train1`
