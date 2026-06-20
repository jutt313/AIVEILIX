#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

export TMPDIR="${TMPDIR:-$REPO_ROOT/.tmp}"
mkdir -p "$TMPDIR"

COMMIT_MESSAGE="${1:-chore: sync production deploy $(date '+%Y-%m-%d %H:%M:%S')}"

TRACKED_STAGE_PATHS=(
  backend/.dockerignore
  backend/.env.example
  backend/.gcloudignore
  backend/Dockerfile
  backend/alembic
  backend/alembic.ini
  backend/app
  backend/pytest.ini
  backend/requirements.txt
  backend/run.py
  backend/scripts
  backend/tests
  deploy/gcp
  firebase.json
  .firebaserc
  .env.example
  .gitignore
  frontend/index.html
  frontend/package-lock.json
  frontend/package.json
  frontend/postcss.config.js
  frontend/public
  frontend/src
  frontend/tailwind.config.js
  frontend/vite.config.js
)

UNTRACKED_SCAN_PATHS=(
  backend/alembic
  backend/app
  backend/scripts
  backend/tests
  deploy/gcp
  frontend/public
  frontend/src
)

EXCLUDE_PATTERNS=(
  ".claude/*"
  ".firebase/*"
  "2026-05-24test/*"
  "Aiveilix-pipline/*"
  "New Folder With Items/*"
  "benchmark/*"
  "formarketing/*"
  "its for final test/*"
  "phase1_3_validation_output/*"
  "frontend/.claude/*"
  "frontend/.DS_Store"
  "frontend/public/benchmark*.pdf"
  "backend/run_*test.py"
  "backend/PIPELINE_TODO.md"
  "backend/PROGRESS.md"
  "frontend/log.md"
  "frontend/progress.md"
  "*.md"
)

matches_exclude() {
  local path="$1"
  local pattern
  for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    if [[ "$path" == $pattern ]]; then
      return 0
    fi
  done
  return 1
}

has_prefix_match() {
  local path="$1"
  shift
  local prefix
  for prefix in "$@"; do
    if [[ "$path" == "$prefix" || "$path" == "$prefix/"* ]]; then
      return 0
    fi
  done
  return 1
}

find_out_of_scope_changes() {
  local path
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    if ! has_prefix_match "$path" "${TRACKED_STAGE_PATHS[@]}"; then
      printf '%s\n' "$path"
    fi
  done <<< "$1"
}

stage_production_changes() {
  git add -u -- "${TRACKED_STAGE_PATHS[@]}"

  local untracked=()
  local path
  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    if matches_exclude "$path"; then
      continue
    fi
    untracked+=("$path")
  done < <(git ls-files --others --exclude-standard -- "${UNTRACKED_SCAN_PATHS[@]}")

  if ((${#untracked[@]} > 0)); then
    git add -- "${untracked[@]}"
  fi
}

classify_changes() {
  local path
  NEED_PUSH=0
  NEED_BACKEND=0
  NEED_FRONTEND=0
  NEED_DB=0

  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    NEED_PUSH=1

    if has_prefix_match "$path" backend deploy/gcp; then
      NEED_BACKEND=1
    fi
    if has_prefix_match "$path" frontend; then
      NEED_FRONTEND=1
    fi
    if [[ "$path" == "firebase.json" || "$path" == ".firebaserc" ]]; then
      NEED_FRONTEND=1
    fi
    if has_prefix_match "$path" backend/alembic backend/app/models; then
      NEED_DB=1
    fi
    if [[ "$path" == "backend/alembic.ini" || "$path" == "backend/scripts/apply_schema.py" ]]; then
      NEED_DB=1
    fi
  done <<< "$1"
}

git fetch origin main --quiet

behind_count="$(git rev-list --count HEAD..origin/main)"
if ((behind_count > 0)); then
  echo "Local HEAD is behind origin/main. Rebase or merge first." >&2
  exit 1
fi

stage_production_changes

staged_files="$(git diff --cached --name-only)"
if [[ -n "$staged_files" ]]; then
  git diff --cached --check
  git commit -m "$COMMIT_MESSAGE"
fi

git fetch origin main --quiet

ahead_files="$(git diff --name-only origin/main..HEAD -- "${TRACKED_STAGE_PATHS[@]}")"
out_of_scope_files="$(find_out_of_scope_changes "$(git diff --name-only origin/main..HEAD)")"

if [[ -n "$out_of_scope_files" ]]; then
  echo "Refusing to push commits that touch non-production paths:" >&2
  echo "$out_of_scope_files" >&2
  exit 1
fi

classify_changes "$ahead_files"

if ((NEED_PUSH == 0)); then
  echo "No production changes to push or deploy."
  exit 0
fi

git push origin HEAD:main

if ((NEED_DB == 1)); then
  echo "Database changes detected. They will be applied by the backend migration job."
fi

if ((NEED_BACKEND == 1)); then
  "$SCRIPT_DIR/deploy-backend.sh"
fi

if ((NEED_FRONTEND == 1)); then
  API_URL="${API_URL:-https://api.aiveilix.com}" "$SCRIPT_DIR/deploy-frontend.sh"
fi

echo "All required production updates are done."
