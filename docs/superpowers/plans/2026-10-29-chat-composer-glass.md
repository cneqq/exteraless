# Chat composer glass implementation plan

Goal: add Default, iOS + Liquid Glass, Android + Liquid Glass input styles.
Spec: user-approved proposal in chat, 2026-10-29. No Android build, commit or push.
Architecture: retain ChatActivityEnterView controls; use the existing blur3 backdrop and lens. Settings persist through AppearanceConfig. iOS splits the attachment, field and record surfaces; Android retains one capsule.

- [x] Add persisted, validated style selection and Russian/English labels in Appearance.
- [x] Add isolated composer color/lens policy; share the existing independent 6dp capture output with the header, retaining separate factories.
- [x] Swap existing attachment/emoji positions for iOS in ordinary input; keep complex bot/sender/edit/record states on a whole readable surface.
- [x] Configure separate left/right glass surfaces with shared animation alpha, position, theme updates and capture bounds.
- [x] Run available local policy/resource checks and diff review, without Gradle or CI.

Review focus: unsupported Android/blur off/power saving, long multiline text, reply/edit/record transitions, bot/sender controls, narrow screens. Device appearance and touch verification remain pending until an APK is available.

Verification: 3 standalone Java policy/geometry/state tests pass; 8 existing header/navigation tests pass. JavacTask.parse checked 5 modified Java files (syntax only). Russian/English XML and git diff whitespace checked. Full non-plugin unittest run tracked separately. No Android build or device run.

Ruling: when enabling the style with an already constructed chat underneath settings,
use that chat's existing frosted capture if its independent weak capture was not
allocated. This preserves the live chat backdrop; reopening the chat enables 6dp.
Full no-plugin unittest attempt: 27 tests collected, one dependency import error
(test_no_plugins requires unavailable pytest), one AAPT2 check skipped. No Android
build, AAPT2 invocation, device tests, commit or push.
