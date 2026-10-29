# Freezgram Liquid Glass

Settings live under **Freezgram settings → Appearance → iOS Design**:

- **Navigation bar** and **Liquid Glass navigation bar** enable the navigation style.
- **Bottom panel** adjusts width (80–100%), bottom gap (0–64dp) and contact visibility.
- **Chat header** enables the centered glass header.
- **Input panel style** chooses Default, iOS glass, or Android glass.
- **Input panel spacing** appears for the iOS input style: text inset (4–24dp,
  default 12dp) and emoji inset (0–16dp, default 6dp).
- **Liquid Glass** is the shared optical editor with sample header, composer and
  navigation surfaces. It controls blur (0–30dp), refraction (0–100%) and fill
  transparency (0–100%). Each geometry editor has its own preview as well.

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
drawable padding. Text starts after that visible edge plus the configured text
inset. Emoji moves inward by its configured margin, and the edit field reserves
space for its full touch target plus a gap. Returning to replies, editing, voice
recording, bot controls, or narrow layouts restores the original control
arrangement. Existing send/attach/record handlers remain unchanged.

Spacing and shared optics are included in settings backup. The contact switch
only changes contact visibility and does not modify other tab preferences.

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
