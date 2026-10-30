# Freezgram Liquid Glass

The **iOS Design** group contains three switches (0/3): navigation panel,
chat header and input panel. An enabled input switch exposes a Configure row. The separate
**Liquid Glass settings** entry opens shared optics, navigation settings and a
chat-folder glass switch. The navigation switch is also available directly in iOS Design; its geometry remains in the Liquid Glass editor.

Available editors:

- **Navigation panel** opens its own editor with iOS/Liquid Glass switches,
  width (80–100%), bottom gap (0–64dp) and contact visibility.
- **Chat header** enables the centered glass header.
- **Input panel** opens the Default/iOS/Android style selector and a bottom-gap
  slider (0–64dp). The gap applies to iOS input above both the system inset and
  the keyboard. It moves the entire island, including controls and background.
- **Liquid Glass** is the shared optics editor with sample header, composer and
  navigation surfaces: blur, refraction, fill transparency and color enhancement.

The iOS text and emoji share one 0–32dp content-inset setting (default 16dp).
Older independent spacing preferences are no longer read or exported. Each editor has its own preview. Navigation previews use the
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
drawable padding. Text starts after that visible edge plus the configured content inset. Emoji uses
the same inset, and the edit field reserves space for its touch target.
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
insets use their separate symmetric 0–32dp setting. Left and right panel margins always use the same value, limited
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

**Other small elements** is an independent opt-in under shared Liquid Glass
settings, included in backup and disabled by default. It covers ordinary Bulletin/UndoView notices, message action menus/reactions,
inline callback buttons and the share button beside a message; saved-message navigation, discussion and sponsor
controls retain their previous appearance. The button uses shared optics over
a wallpaper-only source, avoiding recursive capture of the cell itself. The
source is recorded once per chat drawing frame and reuses glass drawables for
visible cells. References/callbacks are released on detach or delegate change.
Android below 13, software drawing, disabled blur or power saving retains the
standard button background. Touch and sharing handlers are unchanged.
GPU and scrolling behavior require phone verification.

For small-element notices the backdrop is a temporary in-memory snapshot, captured
without Bulletin/UndoView contents to avoid feedback. The bitmap is never saved
or sent anywhere. It is released on detach and before reusing an UndoView for a
new notice. Explicit custom/color-coded Bulletin backgrounds keep their existing
appearance. System notifications are outside this setting. Legacy blurred notice
animation is bypassed while this style is active so it does not replace the glass
with an opaque bitmap. The usual position/alpha animation remains.
Message menus bridge their existing capture into the RenderNode/AGSL renderer;
shared optics apply to the message menu, swipe-back submenus, quick reactions,
reaction/tag popup and chat header overflow menu. The older independent
message-menu glass preference remains available when the small-elements toggle
is off. The explicit small-elements choice uses the platform/blur/power policy
instead of legacy server-controlled menu blur flags. The later opaque popup
assignment no longer replaces the glass background.

Popup materials retain a minimum tint (24% dark / 18% light) and a brighter contour,
even at 100% panel transparency, so labels and quick reactions have a visible
backing. Normal navigation/header transparency is unchanged. The reaction body
and its two bubbles have independent drawables and independent cropped source
recordings: resizing a bubble cannot overwrite a retained main-panel RenderNode.
Captures include only the target region plus a 64dp margin instead of a separate
full-screen texture for each shape. Shared blur and optional color enhancement
are applied once to the raw menu snapshot.

Callback buttons keep their existing neutral, red, green or blue meaning. Colored
buttons add a translucent tint over glass; URL and other non-callback buttons
retain their existing background. Actions, payloads, labels, loading indicators
and touch feedback are unchanged. Button glass is released on detach/delegate
change and when the style is disabled.

**Attachment menu panels** is a separate, backed-up opt-in (default off) in the
shared Liquid Glass editor. It changes the bottom attachment selector and caption
controls, using an independent blur output and the shared optics/material policy.
It does not change gallery items or other sheets/dialogs. With the setting off,
these controls use their original factory and color providers.

JVM harnesses exercise callback color preservation, reaction/source independence,
cropped capture sizes and attachment opt-in/platform/blur/power fallback. Snapshot
placement, contrast and GPU performance still require device verification.

Glass power saving now treats the phone's system saver as mandatory, independently
of the app's follow-system switch or battery threshold. The system receiver
invalidates visible view trees and notifies glass-specific listeners. RenderNode
drawables release/refuse AGSL effects in saver, retain the requested state for
restoration, refresh cached colors when saver changes, and skip backdrop capture
for fully opaque fallback fills. Shared glass surfaces use an opaque fallback in
saver. This does not change the app's other LiteMode preference semantics.
The independent downscaled navigation/header capture output now enables the
existing fractional-scroll phase compensation: restored and input translations
cancel, keeping the capture viewport fixed while reducing resampling jitter.
Device verification of slow scrolling and system-saver transitions is required.


The shared editor also provides **Chat list header**, independently from folder
and small-element glass and off by default. It uses the weak capture output for
the ActionBar above folders; the original opaque underlay is excluded only from
that rectangle. The ActionBar draws the material once. Search, previews, software drawing, unsupported platforms and power saving retain the
original background path. Shared optics and source recordings are refreshed on
scroll and style changes. The preference is included in backup.

Ordinary ItemOptions menus (including the chat list overflow) follow Other small
elements. Their snapshots use the shared RenderNode material and visible contour.
Explicit custom/color backgrounds and custom blur factories retain their own
styling. This changes menu surfaces, not their commands or button handlers.
Device checks are needed for header scrolling/transitions and popup placement.


**Separators in glass menus** toggles thin inset lines between adjacent visible
menu rows. It defaults to on and is backed up; it only applies to the shared
small-element glass style. Group gaps and hidden rows do not add duplicate lines.
The overlay does not change row sizes or touch targets. Both message popups and
ordinary ItemOptions menus use it.


The chat-list header also stays glass in chat-selection mode. The ActionBar
attempts the explicit material independently of its legacy background color,
including transparent themes. Ordinary ActionBarMenuItem popups without an
explicit capture factory now obtain a fresh in-memory glass snapshot when opened;
this includes selected-chat actions. Disabling small-element glass restores their
original popup material. Explicitly supplied factories are preserved. JVM checks
cover transparent-theme dispatch and automatic capture refresh/restoration;
actual header and popup appearance still requires phone verification.


The preliminary composer measurement in ChatActivity now subtracts the same
symmetric panel insets as the nested ChatInputViewsContainer. Previously the two
passes could wrap a draft differently and repeatedly retarget its height animator.
One helper supplies the inset calculation to both passes; Default/Android styles
continue to use zero panel inset. The regression checks matching wrap widths for
0/16/48dp insets and narrow/normal screens. Clipping and height transitions still
require device verification with multiline drafts and sender/reply controls.


Side chat controls (scroll down, unread mentions/reactions and search arrows)
follow Other small elements and use the shared weak capture with the common
material/optics. The weak output is allocated even when small elements are the
only opted-in surfaces. Counters and click handlers are unchanged.
The main iOS composer send button receives its own glass drawable. Its accent
fill is skipped only when that material can draw on a supported hardware canvas;
Default/Android styles, disabled blur and power-saving retain the original fill.
The icon uses the theme glass foreground. Sending, scheduling, loading, paid-send
and locked-send logic is unchanged. JVM tests verify accent/glass exclusivity
and fallback; device verification of the two button surfaces remains required.


The idle chat search placeholder is centered within the area remaining between
the leading search icon and trailing controls (including proxy). Typing, focus
and active filters retain normal LTR/RTL text alignment. Font padding is removed
only for this opted-in chat list field to align its text vertically. With Chat
list header glass enabled, the search pill uses the shared weak capture and
material in both idle and expanded search, rather than hiding glass while idle.
Power-saving/disabled blur retain the normal background. It shares the header
preference and does not add another toggle.

Freezgram settings screens use a short 28dp fade/slide with a gentle easing curve
(320ms open, 280ms close). The transition completes once and restores container
alpha/translation after completion or cancellation. App/system animation opt-outs
remain authoritative; unrelated Neko/Telegram settings keep their old transitions.
Appearance group changes dispatch row-key diffs instead of full dataset resets;
settings row add/remove/move animations have softer timing. JVM regressions cover
transition cleanup/cancellation and search alignment with typing, filters and RTL.
These visual changes have not been verified on a device or compiled into an APK.


Wallpaper under-sources can be shared by several glass shapes without going
through createDrawable. Their cropped snapshot node must not be resized or moved
after another parent display list retains it. SnapshotSource now allocates a new
recording node when crop size/origin changes, while reusing an unchanged crop.
A JVM regression reproduced the old retained-node geometry overwrite and passes
with the fix. This can explain rectangular seams/bands; confirming the reported
artifact is gone still requires a phone build. No APK was requested for this fix.
