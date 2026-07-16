#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 scripts/build_content.py
