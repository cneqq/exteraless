# No-Plugins Branch Design

## Intent

Keep `main` as the plugin-enabled edition and make `no-plugins` a separately buildable edition with no plugin engine or plugin entry points. Both editions must retain the same Freezgram app identity and signing lineage so a newer build of either edition can update the other in place.

## Goals

- Remove plugin execution, Python embedding, permission/grant handling, hook and menu injection, plugin installation, and plugin-specific screens/actions from `no-plugins`.
- Remove build dependencies and packaged resources that exist only for plugins.
- Keep normal Telegram/Freezgram actions working wherever plugin hooks are removed.
- Build a release APK from the no-plugin branch through the existing signed CI workflow and verify it does not contain the plugin runtime.
- Preserve unrelated local edits. The three original local differences in build/workflow/docs were stale package-identity changes from the ZIP; preserve backup copies, but align this edition with `main`'s `com.freezgram.app` identity to satisfy cross-edition updates.

## Non-goals

- Change or remove plugin support from `main`.
- Change the application ID, signing setup, or release workflow as part of plugin removal.
- Remove unrelated Freezgram features, generic Telegram functionality, or non-plugin Python tools unless dependency analysis proves they are plugin-only.
- Merge the no-plugin changes into `main` or alter the plugin-enabled branch. The user separately authorized committing/pushing `no-plugins` and running the existing Personal release APK workflow.

## Approaches

1. **Remove plugin support from this branch (chosen).** Delete the runtime, plugin-only build dependencies, permissions, installers, UI, entry points, and injection hooks. Restore ordinary app behavior at each former integration point. This satisfies the request for an edition fully without plugins and removes their runtime/build weight, at the cost of a broad cross-cutting change.
2. **Disable plugins behind a build flag.** Keep the engine and plugin API in source while hiding the interface and skipping startup. This reduces immediate code churn but leaves plugin code and dependencies in the no-plugin edition, so it does not meet the requested scope.

## Design

The `no-plugins` branch is the only target of this work; `main` remains the plugin edition. Remove `app.exteraless.plugins` and plugin-only Python runtime sources after checking for consumers that also serve non-plugin features. Remove Chaquopy configuration, its source submodule integration, plugin-specific hook/filter libraries, ProGuard keep rules, plugin-only test fixtures, translated strings, manifest intent filters, and the safe-mode shortcut only where they are exclusively plugin-related.

At app integration points, delete plugin callbacks and restore the existing non-plugin path rather than retaining no-op stubs. This includes application lifecycle and message hooks, menu/settings injection, plugin download/install handling, profile/chat menus, and plugin diagnostics in crash/profiling screens. Preserve message/file behavior for ordinary files and links.

Keep the same personal application ID (`com.freezgram.app`) and signing configuration as the plugin edition on `main`. Use the existing shared monotonic version-code policy so a build from either branch can update one from the other without a downgrade. Preserve application data on update; do not delete leftover plugin files or settings from app storage. A locally debug-signed APK is a compilation artifact; updating an installed personal release requires the same release signing key used by the existing CI workflow.

## Verification

- Add focused static regression checks that fail if plugin startup, plugin menu/actions, file installers, plugin runtime dependencies, or plugin package artifacts return to this branch.
- Remove or retire tests that only exercise the deleted plugin engine; keep and run tests for unaffected app features.
- Run the repository Python test suite with any required external corpus expectations reported accurately.
- Build `:TMessagesProj:assembleRelease` for arm64 using the existing CI signing configuration. Inspect the APK contents to confirm Chaquopy/Python plugin runtime and plugin-only entry points are absent.
- Review the final branch diff to confirm the three carried local edits and unrelated app code remain intact.

## Constraints and risks

- Plugin references are spread across core Telegram screens and services, so removing one class without restoring the original control flow can break normal UI or message behavior.
- The workspace has several uninitialized Git submodules, including the Chaquopy source submodule. Removing Chaquopy should avoid that submodule, but an Android build may still require other native submodules or local SDK configuration.
- Some strings and icons may be shared with unrelated features; remove only resources proven to be plugin-specific.
- Both editions share package identity; updates also require the same signing key and a non-decreasing version code across branches.
