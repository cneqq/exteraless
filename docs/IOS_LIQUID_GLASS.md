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
