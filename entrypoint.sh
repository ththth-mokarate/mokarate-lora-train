#!/bin/bash
# LoRA training container entrypoint.
# 1. Start the file server FIRST so Salad's /ready probe passes immediately
#    and logs/checkpoints are downloadable while training runs.
# 2. Run ai-toolkit training, logging into the served output directory.
# 3. Write a DONE marker (with the exit code) and keep serving the files
#    until the operator stops the group.
mkdir -p /app/ai-toolkit/output
nohup python3 /app/server.py > /app/server.log 2>&1 &
cd /app/ai-toolkit
python run.py /app/mokarate_face_v1.yml > /app/ai-toolkit/output/train.log 2>&1
echo "exit=$?" > /app/ai-toolkit/output/TRAINING_DONE
sleep infinity
