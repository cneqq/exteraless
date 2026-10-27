# No-Plugins Implementation Plan

> **For agentic workers:** Execute with superpowers:executing-plans in this session.

**Goal:** Build an edition on `no-plugins` with the plugin system entirely removed.
**Architecture:** Delete the runtime and restore ordinary control flow at all plugin integration points. Keep package/signing identity and version policy shared with `main`.
**Tech Stack:** Java/Kotlin, Android Gradle, Python static regression checks.
**Spec:** `docs/superpowers/specs/2026-10-27-no-plugins-branch-design.md`

## Global Constraints

- Work on `no-plugins`, preserving the three existing local edits and all existing user tests.
- Keep the application ID, signing configuration, and shared version-code policy.
- Preserve user data and unrelated messaging features.
- The user authorized a commit, push of `no-plugins`, and the existing signed CI build. Do not merge or change `main`.

## Review Focus

- Message send/update/request paths must retain ordinary control flow after hooks disappear.
- File taps and links must fall back to standard Telegram behavior.
- Saved menu layouts must gracefully ignore obsolete plugin menu IDs.
- APK must contain no Python/Chaquopy/plugin runtime.
- Both editions must retain package/signing continuity; an older version code cannot update a newer APK.

## Tasks

### 1. Runtime and app integration

- [ ] Preserve a baseline copy of existing local edits in `.git/no-plugin-work`.
- [ ] Add `tests/test_no_plugins.py` contract checks for runtime, dependency and entry-point absence; observe failure against the plugin edition.
- [ ] Remove plugin Java/Python runtime and compatibility plugin APIs, plus plugin-specific app callbacks, request/message hooks and diagnostics. Preserve ordinary core behavior.
- [ ] Remove all plugin UI routes, menu injection, settings rows, file installation handlers, safe-mode shortcut and plugin-only resources.

### 2. Build and tests

- [ ] Remove Chaquopy/runtime tasks, plugin-only dependencies, submodule integration and ProGuard rules. Adapt existing build workflow caches/inputs only where they require the deleted runtime.
- [ ] Preserve existing tests; explicitly skip plugin-engine tests on the no-plugin edition and keep unrelated tests active.
- [ ] Run focused no-plugin contracts and the full existing suite; fix relevant failures.

### 3. APK and review

- [ ] Check Android build dependencies without reading secret values. Build the arm64 APK with the existing signing/identity configuration where available.
- [ ] Inspect resulting APK for plugin runtime absence, package identity, version code and signing certificate.
- [ ] Review the whole diff with a fresh reviewer and fix material issues.
- [ ] Report the APK path and any verification/build limitations with evidence.

## Execution decisions

- The approved specification authorizes implementation; this plan is an execution record rather than another approval gate.
- Existing user tests will be preserved rather than deleted, following AGENTS.md.
- Use the existing feature branch in the current workspace; a second checkout is unnecessary.
- Commit/push only task files, as explicitly authorized after source review.

## Progress

- Runtime/UI/build dependency removal completed; pre-existing stale package-ID differences aligned with `main` to satisfy cross-edition updates, with original copies retained locally.
- Source review found no confirmed defects. Full active test suite: 19 passed, 1 AAPT2-dependent test skipped; Java syntax, XML and workflow YAML parse passed.
- Existing plugin test files are preserved and explicitly excluded on this edition; generic app tests remain active.
- Signed release build and APK inspection pending.
