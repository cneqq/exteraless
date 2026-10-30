# Freezgram Liquid Glass

The **iOS Design** group contains only two switches (0/2): chat header and
input panel. An enabled input switch exposes a Configure row. The separate
**Liquid Glass settings** entry opens shared optics, navigation settings and a
chat-folder glass switch. The navigation style does not count toward iOS 0/2.

Available editors:

- **Navigation panel** opens its own editor with iOS/Liquid Glass switches,
  width (80–100%), bottom gap (0–64dp) and contact visibility.
- **Chat header** enables the centered glass header.
- **Input panel** opens the Default/iOS/Android style selector and a bottom-gap
  slider (0–64dp). The gap applies to iOS input above both the system inset and
  the keyboard. It moves the entire island, including controls and background.
- **Liquid Glass** is the shared optics editor with sample header, composer and
  navigation surfaces: blur, refraction, fill transparency and color enhancement.

The iOS text and emoji insets are fixed at 16dp, including for existing installs
with older spacing preferences. The obsolete spacing preferences are no longer
read or exported. Each editor has its own preview. Navigation previews use the
actual MainTabsLayout measurement and GlassTabView components, rather than equal
weighted placeholder columns. Reset affects only the current editor.

## Shared appearance

`LiquidGlassStyle` supplies the same theme color, tint alpha, outline, shadow,
12dp lens thickness, and configurable refraction intensity for all three glass
surfaces. Defaults are 6dp blur, 55% refraction, and 90% dark / 93% light fill
transparency. These percentages describe the color overlay, not total composited
opacity. Unsupported or power-saving configurations retain an 82% opaque fill.
Each surface still has its own opt-in style switch. Parameters are stored using
the existing navigation preference keys, so existing slider choices are retained;
they now apply to the header and composer too. Geometry preferences remain separate.
Reset only affects the editor currently open.

**Enhance colors** controls the existing 3× saturation filter on the independent
capture output used by these panels. It defaults to enabled to preserve the
previous look and is included in backup. Disable it to remove this extra color
filter; blur, tint, lighting and compositing can still change perceived colors.
The preview applies the same choice, including at zero blur. Unrelated legacy
frosted surfaces retain their previous color policy.

Refraction requires Android 13+, enabled chat blur and inactive power saving.
The preview uses the same renderer on sample content, with the actual navigation
tab components and composer icon resources. It illustrates enabled glass, even
if a particular production style is currently disabled. It is not a live chat.
Changes are previewed immediately; underlying fragments rebuild on leaving the
editor. Header/composer drawable revisions update after shared optics change.

The existing Telegram capture, `LiquidGlassEffect` and `liquid_glass_shader` are
reused; no runtime dependency, native library or network service was added.
An independently allocated capture output avoids depending on the old global
Liquid Glass flag. Navigation supplies the selected blur radius for its capture;
ChatActivity supplies the same radius for the header and composer. Zero blur
removes the blur effect and uses full-resolution capture. Existing unrelated
frosted surfaces keep their old blur. Feed delegates navigation capture to the
chat source; tint and refraction are shared, while its capture remains dependent
on the enabled chat styles. A chat constructed before enabling a glass style may
retain a stronger fallback capture until reopened.

## Composer geometry

The iOS field is inset 50dp on either side, plus its existing 7dp transparent
drawable padding. Text starts after that visible edge plus 16dp. Emoji has a
fixed 16dp margin, and the edit field reserves space for its touch target.
Returning to replies, editing, voice recording, bot controls, or narrow layouts
restores the original control arrangement. Existing send/attach/record handlers
remain unchanged.

The iOS bottom gap moves child views and captured drawable bounds by the same
amount. Occupied-height calculations include that gap, so list padding, scroll
buttons, overlays and capture bounds stay above the lifted input. Keyboard
translation is accounted for separately. Style Default/Android retains zero
additional gap. Geometry and shared optics are included in settings backup.
The contact switch only changes contact visibility.

## Validation

Standalone Java harnesses exercise glass eligibility, shared optical values,
capture selection, slider updates, drawable lifetime, composer bounds and spacing
restoration. Java/Kotlin parsing and XML validation do not prove GPU appearance.
Check on a phone: light/dark themes, existing and reopened chats, search/selection,
long text, keyboard/emoji, replies/edits, attachments, voice/video recording,
channels, screen rotation, disabled blur and power saving, settings reset/restore.

Reference projects reviewed for the original renderer choice:

- [Kyant0/AndroidLiquidGlass](https://github.com/Kyant0/AndroidLiquidGlass), Apache-2.0.
- [QmDeve/AndroidLiquidGlassView](https://github.com/QmDeve/AndroidLiquidGlassView), MIT.

No source code from these projects was copied.

Folder glass uses the independent capture output and shared color/refraction
policy, including saturation and power-saving fallback. Channel action/search/
gift controls use the composer capture factory when the glass input style is
selected. This covers the separate controls around the subscribe/mute action,
not just the central input island. Visual/device validation remains necessary.
Visible upstream branding is replaced by Freezgram; attribution, upstream links,
namespace identifiers and import compatibility descriptions are retained.

Input settings also expose a single symmetric side-inset slider (0–48dp).
The entire iOS island and its backdrop are inset together; text/emoji internal
insets remain fixed at 16dp. Left and right always use the same value, limited
on narrow windows to retain at least 240dp for the input where possible.
The preview, reset and settings backup include this parameter. Other input
styles retain their existing horizontal geometry.

The shared editor now includes actual FilterTabsView-based folder preview tabs;
the folder glass toggle updates that preview and the shared optics. The header
switch also controls the common top-panel surface containing pinned messages,
translation and chat information notices. It uses the same independent capture,
colors and power-saving behavior as the header, with cached effect updates.
The default chat-list title is Freezgram in the shared title helper; explicit
custom titles remain unchanged.

Wallpaper capture preserves ChatBackgroundDrawable's dim amount when unwrapping
the raw image. A wrapped source composites black over only the wallpaper capture
bounds before foreground messages or glass refraction. The source bitmap is not
modified. System-bar color estimates also include that dim amount. No additional
user-facing dim slider or arbitrary global dark overlay is introduced.

The shared editor provides **Apply wallpaper dimming** (enabled by default,
backed up with other settings). It switches the wallpaper backdrop between the
actual rendered wallpaper-only view (preserving all drawable filters/dimming)
and the raw image source. Foreground messages are captured separately. The
rendered path is clipped to the capture rectangle and falls back to the image
until the wallpaper view is measured. It does not add another dark layer over
the already-rendered wallpaper. Switching increments the shared style revision
so cached glass is refreshed; default reset re-enables it.

Text-send transition endpoints subtract only the input field's collapsible
height above 44dp. The fixed iOS bottom gap remains in the target list padding;
it is not part of the height change animated away after sending. The regression
covers single/multiline fields and 0/16/64dp gaps at 2× density.

The idle voice/video recording button background follows the iOS style rather
than eligibility for the split layout. Group sender controls, replies and narrow
layouts can retain the whole composer without restoring the opaque accent circle.
The icon uses the glass foreground color. Recording handlers and the active
recording animation are unchanged; Default/Android styling retains its policy.
