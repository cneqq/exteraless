# iOS navigation Liquid Glass

Enable **Freezgram settings → Appearance → iOS Design → Navigation bar**,
then **Liquid Glass navigation bar**. The child option is local and off by default.

The main tabs use the existing Telegram backdrop capture, `LiquidGlassEffect`
and `liquid_glass_shader`. Refraction requires Android 13+, enabled blur and
inactive power saving. Other configurations use a more opaque frosted surface.
The preference is included in settings backup. No new runtime dependency,
native library or network service is added.

Reference projects reviewed for the implementation choice:

- [Kyant0/AndroidLiquidGlass](https://github.com/Kyant0/AndroidLiquidGlass):
  Apache-2.0, Compose Multiplatform; `LiquidBottomTabs` combines a backdrop,
  lens, highlights and shadows. Adding Compose is unnecessary for this View UI.
- [QmDeve/AndroidLiquidGlassView](https://github.com/QmDeve/AndroidLiquidGlassView):
  MIT, Android View refraction/dispersion, Android 13+. Its older-platform
  transparent fallback would need adaptation for readable navigation.

No source code from these projects was copied. This implementation configures
the client's existing renderer and adds an opt-in navigation color provider.

Phone verification: switch on/off, change light/dark themes, scroll and switch
tabs, rotate, show/hide navigation, and verify fallback with blur disabled or
power saving active. GPU appearance and performance require a device check.

The navigation capture has a separate weak-blur output (6dp) even when the old
client-wide Liquid Glass flag is off. Only the navigation capture rectangle uses
that output; existing frosted surfaces keep the previous strong-blur output.
The color overlay is 10% in dark themes and 7% in light themes; unsupported or
power-saving configurations retain the 82% fallback. The visible upper edge is
also softer. These are overlay alpha values, not the final composited opacity.

An additional **Bottom panel** entry in the expanded iOS Design group opens a
synthetic-content preview using the same AGSL renderer. Sliders persist blur
(0–30dp), refraction intensity (0–100%), and fill transparency (0–100%). They
apply to the live panel when returning to the main tabs. Reset restores 6dp,
55%, and the theme-dependent default transparency. Values are included in
settings backup and clamped when read. The Android/power-saving fallback keeps
its fixed opacity. The optional Feed tab delegates capture to ChatActivity and
retains its existing background blur; tint/refraction still use the new values.
Device checks should include that limitation, restore/reset, theme changes,
and both the old global glass toggle states.

## iOS chat header

The existing **iOS Design → Chat header** option also enables glass for the
centered name/status capsule and the back/avatar surfaces. The avatar opens
the existing chat menu; the name opens the profile. iOS takes precedence if
the Material chat-header preference is also enabled.

The header uses its own capture source and the separate 6dp weak-blur output,
including when the global Liquid Glass option is off. Other chat surfaces
keep their existing blur. Refraction uses a 12dp lens thickness and 55%
intensity; tint alpha is 12% in light themes and 18% in dark themes. These are
overlay values, not final composited opacity. Bottom-panel sliders do not
change the header.

Android 13+, enabled chat blur and inactive power saving are required for
refraction; other configurations use an 88% tint. The center capsule keeps
round ends independently of avatar corners, including after search closes.
Its vertical edge inset relaxes during search and message selection.

Java policy/capture/hit-test regressions can run without an APK. Appearance,
touch transitions and GPU performance still require verification on a phone.

Panel geometry controls set width (80–100% of the available width before the
existing side margins) and distance above the system bottom inset (0–64dp).
The contact switch changes only the existing hide-contacts preference; it does
not modify Feed or other tab preferences. Geometry/tab changes rebuild
underlying fragments when leaving the editor so content padding, FAB clearance,
and cached pager positions stay in sync. Preview tabs use the same components
as the real panel. Phone layout checks are still needed.


## Chat input styles

Appearance → Input panel style offers Default, iOS + Liquid Glass, and Android +
Liquid Glass. Default keeps the existing appearance. Android retains one capsule;
iOS moves the existing attachment control to a separate left circle and retains
an independent record/send surface on the right. The existing emoji control moves
to the right end of the field. Existing attach/record/send handlers remain in use.

The new styles use a separate color/lens policy and the existing independent 6dp
chat capture output, without following the global glass toggle or navigation
sliders. Refraction requires Android 13+, chat blur and inactive power saving;
otherwise the fill is 92% opaque. A chat constructed before the style was enabled
uses its existing stronger frosted capture until reopened. Replies, edits,
recording, sender/bot/rich-draft controls and widths below 240dp retain a whole
glass surface and the original control arrangement. Multiline ordinary input
keeps the field growing and both side circles aligned at the bottom.

No APK build was run for this change. Standalone Java tests cover eligibility,
surface bounds, lens/color fallback and animation alpha; Java parsing and XML
validation do not prove Android integration or visual fidelity. Device checks
remain: light/dark themes, typing/send, attachment and voice/video recording,
keyboard/emoji, reply/edit, channels, narrow/multiline input and power-saving.
