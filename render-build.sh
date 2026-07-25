#!/usr/bin/env bash
# Render build step. The persistent disk is NOT mounted here, so this only
# installs dependencies and collects static files — migrations run in the
# preDeploy command (see render.yaml), when the disk is available.
set -o errexit

pip install uv
uv sync --frozen --no-dev

# Compiled Tailwind CSS + vendored JS are committed, so no Node build needed.
.venv/bin/python cricbox/manage.py collectstatic --no-input
