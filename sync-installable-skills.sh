#!/usr/bin/env bash

# Sync the skills listed in installable-skills.txt into Codex and Claude.
# This script deliberately manages symlinks only; it never removes real files
# or directories from either destination.
#
# Pruning is limited to links this kit installed. A link is only ever removed
# when it points into this repository, and the set of links installed from this
# checkout is recorded in a manifest under XDG_STATE_HOME. Symlinks belonging to
# other projects are left alone even when they are not named in the skill list.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sync-installable-skills.sh [--dry-run]

Create or repair absolute symlinks for every skill named in
installable-skills.txt, then remove the symlinks in ~/.codex/skills and
~/.claude/skills that this kit previously installed and that the file no
longer names.

Links pointing outside this repository belong to other projects: they are
never removed, and a name already held by one is skipped with a warning
rather than repointed here.
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

# The manifest records which links this checkout installed, so a later run can
# retire its own stale links without touching links owned by anything else.
# It is keyed by the repository path: two checkouts syncing into the same
# destination never share or clobber each other's record.
path_digest() {
  local input="$1"
  local digest=''
  if command -v shasum >/dev/null 2>&1; then
    digest="$(printf '%s' "$input" | shasum | cut -d' ' -f1)"
  elif command -v sha1sum >/dev/null 2>&1; then
    digest="$(printf '%s' "$input" | sha1sum | cut -d' ' -f1)"
  else
    digest="$(printf '%s' "$input" | cksum | tr -d ' ' | tr '/' '_')"
  fi
  printf '%s' "${digest:0:12}"
}

state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/sync-installable-skills"
manifest_file="$state_dir/$(basename "$script_dir")-$(path_digest "$script_dir").manifest"

manifest_entries=()

load_manifest() {
  [[ -f "$manifest_file" ]] || return 0
  local m_root m_name
  while IFS=$'\t' read -r m_root m_name || [[ -n "${m_root:-}" ]]; do
    [[ -z "${m_root:-}" || -z "${m_name:-}" ]] && continue
    [[ "$m_root" == \#* ]] && continue
    manifest_entries+=("$m_root"$'\t'"$m_name")
  done < "$manifest_file"
}

is_recorded() {
  local root="$1"
  local name="$2"
  local wanted="$root"$'\t'"$name"
  local entry
  for entry in "${manifest_entries[@]-}"; do
    [[ "$entry" == "$wanted" ]] && return 0
  done
  return 1
}

# A link is ours only when it resolves inside this repository. This is the hard
# safety gate: it holds even when the manifest is missing (an install predating
# the manifest) or stale (a name another kit has since taken over).
links_into_repo() {
  local target="$1"
  [[ -n "$target" ]] || return 1
  case "$target" in
    "$script_dir"/*) return 0 ;;
    *) return 1 ;;
  esac
}

write_manifest() {
  # Guarding an empty array under `set -u` leaves one empty element behind;
  # count real entries rather than array slots.
  local count=0
  local entry
  for entry in "${manifest_entries[@]-}"; do
    [[ -n "$entry" ]] && count=$((count + 1))
  done

  if "$dry_run"; then
    printf 'Would record %d managed link(s) in %s\n' "$count" "$manifest_file"
    return
  fi

  mkdir -p "$state_dir"

  local tmp="$manifest_file.tmp.$$"
  {
    printf '# Skill symlinks installed from %s\n' "$script_dir"
    printf '# destination_root\tskill_name\n'
    for entry in "${manifest_entries[@]-}"; do
      [[ -n "$entry" ]] && printf '%s\n' "$entry"
    done
  } > "$tmp"
  mv "$tmp" "$manifest_file"
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
    current_target="$(readlink "$destination" || true)"
    if [[ "$current_target" == "$source_path" ]]; then
      printf 'Unchanged: %s -> %s\n' "$destination" "$source_path"
      return 0
    fi

    # Repointing is a repair only when the link is already ours. A name held by
    # another project is that project's to manage, so leave it and say so.
    if ! links_into_repo "$current_target"; then
      printf 'Skipping: %s is owned by another project (-> %s)\n' \
        "$destination" "$current_target" >&2
      printf '          Remove it manually to install this kit'"'"'s version.\n' >&2
      return 3
    fi

    printf 'Repairing: %s -> %s\n' "$destination" "$source_path"
    run rm "$destination"
    run ln -s "$source_path" "$destination"
    return 0
  fi

  if [[ -e "$destination" ]]; then
    printf 'Refusing to replace non-symlink: %s\n' "$destination" >&2
    return 1
  fi

  printf 'Linking: %s -> %s\n' "$destination" "$source_path"
  run ln -s "$source_path" "$destination"
}

prune_retired_symlinks() {
  local destination_root="$1"
  local candidate
  local name
  local target

  shopt -s dotglob nullglob
  for candidate in "$destination_root"/*; do
    [[ -L "$candidate" ]] || continue
    name="${candidate##*/}"
    is_desired_skill "$name" && continue

    # readlink, not a resolved path: a dangling link left by a skill deleted
    # from this repository still has to be recognized as ours and retired.
    target="$(readlink "$candidate" || true)"

    if ! links_into_repo "$target"; then
      # Owned by another project, or repointed by hand. Not ours to remove.
      continue
    fi

    if is_recorded "$destination_root" "$name"; then
      printf 'Removing retired skill link: %s\n' "$candidate"
    else
      # Predates the manifest, but demonstrably installed from this repository.
      printf 'Removing retired skill link (adopted, unrecorded): %s\n' "$candidate"
    fi
    run rm "$candidate"
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

# Read the previous run's record before pruning; it is what tells us which
# links are this kit's to retire.
load_manifest

installed_entries=()
skipped_foreign=0
for destination_root in "${destinations[@]}"; do

  for index in "${!skills[@]}"; do
    sync_status=0
    sync_skill "$destination_root" "${skills[$index]}" "${sources[$index]}" || sync_status=$?
    case "$sync_status" in
      0) installed_entries+=("$destination_root"$'\t'"${skills[$index]}") ;;
      3) skipped_foreign=$((skipped_foreign + 1)) ;;  # not ours; do not record
      *) exit "$sync_status" ;;
    esac
  done

  prune_retired_symlinks "$destination_root"
done

# Only now replace the record, so pruning above saw the prior state.
manifest_entries=("${installed_entries[@]-}")
write_manifest

if [[ "$skipped_foreign" -gt 0 ]]; then
  printf 'Skipped %d link(s) owned by another project. See the warnings above.\n' \
    "$skipped_foreign" >&2
fi

if "$dry_run"; then
  printf 'Dry run complete. No changes were made.\n'
else
  printf 'Skill link sync complete.\n'
fi
