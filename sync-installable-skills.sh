#!/usr/bin/env bash

# Sync the skills listed in installable-skills.txt into Codex and Claude.
# This script deliberately manages symlinks only; it never removes real files
# or directories from either destination.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sync-installable-skills.sh [--dry-run]

Create or repair absolute symlinks for every skill named in
installable-skills.txt, then remove symlinks in ~/.codex/skills and
~/.claude/skills that are not named in that file.
EOF
}

dry_run=false
case "${1:-}" in
  "") ;;
  --dry-run) dry_run=true ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
skill_list="$script_dir/installable-skills.txt"

if [[ ! -f "$skill_list" ]]; then
  printf 'Missing skill list: %s\n' "$skill_list" >&2
  exit 1
fi

run() {
  if "$dry_run"; then
    printf 'Would:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

is_desired_skill() {
  local candidate="$1"
  local skill
  for skill in "${skills[@]-}"; do
    [[ "$skill" == "$candidate" ]] && return 0
  done
  return 1
}

skills=()
sources=()
while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
  skill_name="$(printf '%s' "$raw_line" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
  [[ -z "$skill_name" || "$skill_name" == \#* ]] && continue

  if ! printf '%s\n' "$skill_name" | grep -Eq '^[A-Za-z0-9][A-Za-z0-9._-]*$'; then
    printf 'Invalid skill name in %s: %s\n' "$skill_list" "$skill_name" >&2
    exit 1
  fi

  if is_desired_skill "$skill_name"; then
    printf 'Duplicate skill name in %s: %s\n' "$skill_list" "$skill_name" >&2
    exit 1
  fi

  source_dir="$script_dir/$skill_name"
  if [[ ! -d "$source_dir" || ! -f "$source_dir/SKILL.md" ]]; then
    printf 'Listed skill is missing a directory or SKILL.md: %s\n' "$source_dir" >&2
    exit 1
  fi

  source_path="$(cd "$source_dir" && pwd -P)"
  case "$source_path" in
    "$script_dir"/*) ;;
    *)
      printf 'Listed skill resolves outside this repository: %s\n' "$source_dir" >&2
      exit 1
      ;;
  esac

  skills+=("$skill_name")
  sources+=("$source_path")
done < "$skill_list"

if [[ ${#skills[@]} -eq 0 ]]; then
  printf 'No skills found in %s\n' "$skill_list" >&2
  exit 1
fi

sync_skill() {
  local destination_root="$1"
  local skill_name="$2"
  local source_path="$3"
  local destination="$destination_root/$skill_name"

  if [[ -L "$destination" ]]; then
    current_target="$(readlink "$destination")"
    if [[ "$current_target" == "$source_path" ]]; then
      printf 'Unchanged: %s -> %s\n' "$destination" "$source_path"
      return
    fi

    printf 'Repairing: %s -> %s\n' "$destination" "$source_path"
    run rm "$destination"
    run ln -s "$source_path" "$destination"
    return
  fi

  if [[ -e "$destination" ]]; then
    printf 'Refusing to replace non-symlink: %s\n' "$destination" >&2
    return 1
  fi

  printf 'Linking: %s -> %s\n' "$destination" "$source_path"
  run ln -s "$source_path" "$destination"
}

prune_unlisted_symlinks() {
  local destination_root="$1"
  local candidate
  local name

  shopt -s dotglob nullglob
  for candidate in "$destination_root"/*; do
    [[ -L "$candidate" ]] || continue
    name="${candidate##*/}"
    if ! is_desired_skill "$name"; then
      printf 'Removing unlisted symlink: %s\n' "$candidate"
      run rm "$candidate"
    fi
  done
  shopt -u dotglob nullglob
}

ensure_no_managed_name_collisions() {
  local destination_root="$1"
  local index
  local destination

  for index in "${!skills[@]}"; do
    destination="$destination_root/${skills[$index]}"
    if [[ -e "$destination" && ! -L "$destination" ]]; then
      printf 'Refusing to replace non-symlink: %s\n' "$destination" >&2
      return 1
    fi
  done
}

destinations=("$HOME/.codex/skills" "$HOME/.claude/skills")
for destination_root in "${destinations[@]}"; do
  run mkdir -p "$destination_root"
  ensure_no_managed_name_collisions "$destination_root"
done

for destination_root in "${destinations[@]}"; do

  for index in "${!skills[@]}"; do
    sync_skill "$destination_root" "${skills[$index]}" "${sources[$index]}"
  done

  prune_unlisted_symlinks "$destination_root"
done

if "$dry_run"; then
  printf 'Dry run complete. No changes were made.\n'
else
  printf 'Skill link sync complete.\n'
fi
