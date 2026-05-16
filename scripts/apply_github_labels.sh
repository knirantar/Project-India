#!/usr/bin/env bash
set -euo pipefail

# Apply GitHub labels for Project India using the `gh` CLI.
# Usage: ./scripts/apply_github_labels.sh

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI 'gh' is required. Install from https://cli.github.com/"
  exit 1
fi

labels=(
  "good first issue|0e8a16|Good for newcomers: easy, well-defined tasks"
  "help wanted|f9d0c4|Extra help is welcome on this issue"
  "documentation|0366d6|Improvements or additions to documentation"
  "research|5319e7|Research, data collection, or analysis tasks"
  "backend|0e8a16|Backend / server-side work"
  "dashboard|fbca04|Dashboard, UI, or visualization work"
  "data-model|006b75|Changes to database schema or data models"
  "bug|d73a4a|Unexpected behavior or a reproducible bug"
  "enhancement|a2eeef|New feature or enhancement"
  "needs-discussion|cfd3d7|Requires discussion before implementation"
)

for entry in "${labels[@]}"; do
  IFS="|" read -r name color desc <<< "$entry"
  echo "Applying label: $name"
  if gh label list --limit 1000 | awk '{print $1}' | grep -Fxq "$name"; then
    gh label edit "$name" --color "$color" --description "$desc"
  else
    gh label create "$name" --color "$color" --description "$desc"
  fi
done

echo "Done. Labels applied (or updated)."
