+++
aliases = ["docs/keyboard", "docs/keymapping"]
title = "Keyboard and IME"
description = "Host keyboard and IME on every platform. No layout picker in Settings."
weight = 6
date = 2026-09-08

+++

Wawona does not ship a keyboard-layout list. Typing uses the **host** keyboard
and IME. Wawona maps that onto Wayland `wl_keyboard` and `zwp_text_input_v3`.

Keep these three words split:

- **IME / multilingual input:** type Chinese, Japanese, Arabic, Hindi, and
  every other script the host already knows. Host IME goes to
  `zwp_text_input_v3`. Wawona does not catalog languages.
- **i18n:** the compositor accepts any Unicode and any host keymap without a
  new Wawona table.
- **l10n:** Machines and Settings chrome follow the host locale when we
  translate UI. That is not a keymap setting. Date and number formats are
  l10n, not XKB.

[Touch Input Type](@/docs/user/settings.md) and Android Touchpad Mode choose
touch vs virtual pointer. They are not layout.

## How it works

| What you type | What clients see |
|---------------|------------------|
| Letters, swipe, CJK, emoji | `text-input-v3` commit / preedit |
| Hardware keys (arrows, modifiers, F-keys) | `wl_keyboard.key` (position) |
| Terminals that ignore text-input | compositor injects Enter / Tab / Backspace |
| Nested Weston or Niri | their own seats, using a small us/evdev data tree |

On macOS and Android, `wl_keyboard.keymap` is generated from the live host
layout (`UCKeyTranslate` / `KeyCharacterMap`). iOS family seats stay on a
small US fallback; letters still arrive through text-input. Host IME
characters are the ones you typed.

## Per platform

| Platform | Keyboard | IME |
|----------|----------|-----|
| macOS | System input source. Command/Option remap stays (`Swap CMD/ALT`). | AppKit marked text |
| iOS / iPadOS / visionOS | System keyboard + optional hardware HID | UIKit `insertText` |
| watchOS | Host text / dictation | Same |
| tvOS | Remote / optional hardware. No software keyboard | Remote select as keys |
| Android | System InputMethod + `KeyCharacterMap` | `commitText` / composing |
| Linux | Host XKB (`XKB_DEFAULT_*`) | IBus / Fcitx later via IM-v2 |

## Settings

There is **no** Settings row for layout or language. Change the keyboard in
the host OS (iOS globe key, Android Gboard, macOS input menu).

Still in Settings: Touch Input Type, Touchpad Mode, Text Assist, Dictation,
Swap CMD/ALT. Those are input mode and modifier remap.

Contributor notes: [keyboard-layouts.md](https://github.com/Wawona/Wawona/blob/development/docs/keyboard-layouts.md).
Protocols: [Protocol Support](@/docs/contributor/protocols.md).
