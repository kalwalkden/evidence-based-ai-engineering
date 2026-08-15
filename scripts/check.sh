#!/usr/bin/env bash

# Run the same checks CI runs, locally, at the same pinned tool versions.
#
# Requires uv (https://docs.astral.sh/uv/) and npx. Nothing needs installing
# ahead of time: uv and npx fetch and cache each pinned tool on first use.

set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

# shellcheck source=scripts/tool-versions.env disable=SC1091
source "$repo_root/scripts/tool-versions.env"

usage() {
  cat <<'EOF'
Usage: scripts/check.sh [GROUP ...]

Groups:
  lint       ruff, yamllint, shellcheck
  prose      markdownlint, codespell, cspell
  validate   skill-structure validator, sync script dry run
  test       pytest across the supported Python versions

With no arguments every group runs. Set PYTHON_VERSIONS to override the test
matrix, e.g. PYTHON_VERSIONS="3.12" scripts/check.sh test
EOF
}

case "${1:-}" in
  -h | --help)
    usage
    exit 0
    ;;
esac

for tool in uv npx; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'Missing required tool: %s\n' "$tool" >&2
    exit 1
  fi
done

: "${PYTHON_VERSIONS:=3.10 3.11 3.12 3.13}"

failures=()
log_dir="$(mktemp -d)"
trap 'rm -rf "$log_dir"' EXIT

# check NAME COMMAND... — run one check, print a status line, remember failures.
# Output is shown only when the check fails, so a green run stays readable.
check() {
  local name="$1"
  shift
  local log="$log_dir/${name// /_}.log"

  printf '  %-28s' "$name"
  if "$@" >"$log" 2>&1; then
    printf 'PASS\n'
  else
    printf 'FAIL\n'
    sed 's/^/      /' "$log"
    failures+=("$name")
  fi
}

group_lint() {
  printf '\nlint\n'
  check "ruff check" uvx "ruff@$RUFF_VERSION" check .
  check "ruff format" uvx "ruff@$RUFF_VERSION" format --check .
  check "yamllint" uvx "yamllint@$YAMLLINT_VERSION" --strict .
  check "shellcheck" uvx --from "shellcheck-py==$SHELLCHECK_VERSION" \
    shellcheck sync-installable-skills.sh scripts/check.sh
}

group_prose() {
  printf '\nprose\n'
  check "markdownlint" npx --yes "markdownlint-cli2@$MARKDOWNLINT_VERSION"
  check "codespell" uvx --from "codespell[toml]==$CODESPELL_VERSION" codespell
  check "cspell" npx --yes "cspell@$CSPELL_VERSION" \
    --no-progress --show-suggestions "**"
}

group_validate() {
  printf '\nvalidate\n'
  check "validate skills" uv run --no-project --with "PyYAML==$PYYAML_VERSION" \
    python scripts/validate_skills.py
  check "sync dry run" ./sync-installable-skills.sh --dry-run
}

group_test() {
  printf '\ntest\n'
  local version
  for version in $PYTHON_VERSIONS; do
    check "pytest py$version" uv run --no-project --python "$version" \
      --with "pytest==$PYTEST_VERSION" pytest -q
  done
}

groups=("$@")
if [[ ${#groups[@]} -eq 0 ]]; then
  groups=(lint prose validate test)
fi

for group in "${groups[@]}"; do
  case "$group" in
    lint) group_lint ;;
    prose) group_prose ;;
    validate) group_validate ;;
    test) group_test ;;
    *)
      printf 'Unknown group: %s\n\n' "$group" >&2
      usage >&2
      exit 1
      ;;
  esac
done

printf '\n'
if [[ ${#failures[@]} -gt 0 ]]; then
  printf '%d check(s) failed: %s\n' "${#failures[@]}" "${failures[*]}" >&2
  exit 1
fi

printf 'All checks passed.\n'
