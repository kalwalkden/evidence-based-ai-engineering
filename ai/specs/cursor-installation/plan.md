# Cursor installation support

## Scope and decisions

Prepare one standalone task to install the existing toolkit for Cursor alongside Codex and Claude
Code. The user's request is the scoped task input; no feature task list is needed.

- User decision, 2026-10-26: pre-production; preserve existing installation behavior.
- User request: add Cursor installation support. Existing Codex and Claude destinations remain.
- Design decision: append `~/.cursor/skills` to the default destinations, using the existing
  symlink lifecycle. Keep the current no-argument and `--dry-run` commands; no runtime selector,
  copies, marketplace package, project-local installer, or rule conversion.
- Repository contract: `installable-skills.txt` remains the single list of ten skills.
- User boundary: leave implementation unstaged. Git mutations require specific approval.
- Non-visual maintenance task: no visual design is needed.

This is a planning handoff, not authorization to install into the user's actual home directory.
Only this spec package is created during shaping.

## Current behavior and compatibility

`sync-installable-skills.sh` validates the complete skill list and resolves source directories,
preflights destination collisions, loads a checkout-specific manifest, synchronizes each skill,
prunes retired links into this checkout, and replaces the manifest. Its `destinations` array
currently contains only Codex and Claude roots. The same functions already accept any destination.

Preserve Bash 3.2 compatibility, absolute source links, checkout-specific state paths, tab-separated
manifest entries, and existing exit behavior. No manifest migration is needed because entries
already include the destination root. Adding Cursor adds entries to the same manifest.

Foreign symlinks are skipped and not recorded. Real files and directories at managed names fail
preflight. Retired symlinks are removed only when their literal target points into this checkout,
including dangling and unrecorded links. Preserve these actual rules; the manifest is not the sole
ownership gate. Dry runs must not create directories, links, or state files.

Existing install commands will additionally manage Cursor links, as requested. Existing Codex and
Claude link contents and locations remain unchanged. A Cursor name collision may fail the shared
preflight before synchronization, following the existing all-destination behavior. No other breaking
changes are approved.

## Implementation sequence

1. Recheck the installer and this map against the current tree. Confirm the Cursor local discovery
   boundary with the official documentation recorded in `references.md`. Directory discovery is
   documented; symlink discovery still needs a runtime check.
2. Append the Cursor destination to `destinations`. Update the script's header and `usage` text to
   cover all three roots. Reuse `sync_skill`, `ensure_no_managed_name_collisions`,
   `prune_retired_symlinks`, and manifest handling without runtime-specific branches.
3. Add isolated installer regression coverage under a new `scripts/tests/test_sync_installable_skills.py`.
   Copy the installer into a temporary miniature checkout with minimal skills and its own list.
   Run Bash with a child-process environment containing temporary home and state paths; never
   change the interactive shell's home or run a real install against the user's home.
4. Update `README.md`: runtime badge, quick start wording, installation details, and installer
   safety destinations. Keep the existing commands. Explain that local installation does not
   certify every workflow capability; orchestration still requires the capabilities its skill
   declares. Update the introductory runtime list in `scripts/validate_skills.py` without changing
   structural validation. Adjust `ARCHITECTURE.md` only where coverage or installer facts change.
5. Run relevant canonical checks and verify Cursor discovery in an isolated profile if available.
   Report unavailable runtime validation explicitly; do not equate symlink creation with discovery.

## Validation needs and acceptance

There are no installer behavior tests in the current tree. `scripts/check.sh validate` runs only
structural validation and an installer dry run. Existing Python tests cover archival behavior.

Protect these meaningful filesystem boundaries with isolated tests:

- Fresh installation creates links to the listed source directories in all three destinations,
  and records successful links with the correct destination roots.
- Repeated installation is stable; upgrading a two-destination state adds Cursor without disturbing
  existing Codex or Claude links.
- Dry run leaves absent or existing destination/state trees unchanged while reporting Cursor work.
- A foreign Cursor link is retained and excluded from the manifest; real file/directory collisions
  fail without replacing contents or synchronizing skill links in other destinations.
- An owned wrong link is repaired; retired owned links, including dangling links, are removed while
  foreign retired links remain. Exercise the shared behavior across destinations where useful.

Acceptance requires all listed skills to be linked for Cursor using the same source layout,
unchanged existing runtime behavior, accurate help/README instructions, and passing relevant
checks. Verify in Cursor that a representative linked skill is discovered and its instructions and
supporting relative files are readable. Check duplicate presentation with the same skills linked
in all three roots. Record Cursor version and result; if unavailable, leave that acceptance evidence
pending rather than asserting complete runtime support.

Canonical commands from `scripts/check.sh` and `AGENTS.md`:

```bash
scripts/check.sh lint prose
scripts/check.sh validate test
```

The user selected no validation mode. Use focused development checks and these canonical checks
before completion; the developer chooses detailed cases. No feature-wide review or deferred
feature check applies to this standalone task. No static type checker is configured.

## Boundaries and risks

Keep skill instructions, manifests, model mappings, archive behavior, dependency versions, and CI
workflow structure unchanged. Existing pytest discovery already includes the proposed new tests.
`ship-feature` explicitly handles unlisted runtimes by capability and stops when mandatory worker
capabilities are absent; installation support must not weaken those gates.

No stale task brief paths were inherited. One correction to the architecture report matters:
the installer is Bash, not POSIX shell. Do not introduce Bash features beyond the advertised 3.2 floor.

Cursor cloud synchronization and marketplace distribution are outside scope. If local Cursor does
not follow these directory symlinks, report the evidence and revise the installation approach before
implementing a copying mechanism with different ownership and update semantics.

No product decisions remain open. Runtime symlink discovery remains an explicit validation risk.

## Implementation record — 2026-10-26

Implementation is finished; Cursor runtime acceptance remains pending. The shared installer now
includes Cursor, with documentation updated and six isolated filesystem regression tests added.
These tests protect link ownership and non-destructive installation, which had no prior coverage.

Validation used focused development checks followed by all required canonical groups:

- `python3 -m unittest discover -s scripts/tests -v`: exit 0, six tests passed.
- `scripts/check.sh lint prose validate test`: exit 0; all checks passed, including the full Python
  suite on 3.10, 3.11, 3.12, and 3.13. No full-suite checks were deferred.
- `git diff --check`: exit 0.

Task review: Pass. No findings; zero blocking and zero advisory findings. The reviewed implementation
used temporary Git trees to isolate this task from the pre-existing untracked spec package.

Cursor and cursor-agent were not available on PATH, and Cursor.app was not present in standard
system or user Applications locations. Runtime discovery, relative-resource loading within Cursor,
and duplicate presentation remain unverified. No actual user skill directories were changed.
Keep this spec active until that acceptance evidence is supplied; do not claim runtime verification
or archive it as fully accepted. A draft PR can carry this explicit validation limit.
