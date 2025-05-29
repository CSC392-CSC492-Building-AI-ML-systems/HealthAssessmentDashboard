#!/usr/bin/env bash

set -e

echo "Running update_requirements.sh..."

if ! git diff --quiet; then
  echo "⚠️  Skipping requirements.txt update: Working tree has unstaged changes."
  exit 0
fi

LOCK_FILE=".git/index.lock"
if [ -f "$LOCK_FILE" ]; then
  echo "⚠️  Skipping requirements.txt update: Git index is locked."
  exit 0
fi

./venv/bin/pip freeze > requirements.txt
git add requirements.txt

echo "✅ requirements.txt updated and staged."