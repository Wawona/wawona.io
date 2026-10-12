+++
aliases = ["docs/nested-compositors"]
title = "Nested compositors"
description = "Weston and Niri stay real ports. Install as debs or wasm, not mandatory App Store in-app archives."
weight = 22
date = 2026-08-25

+++

Weston and Niri remain **real** Wayland compositor ports. Fake entry points do not count.

They are **optional software**: install later from `repo.wawona.io` as debs (jailbreak iOS, Termux, Linux) or wasm (store hosts). The App Store app keeps the Wawona compositor, Relay wasm, zsh, uutils, and fastfetch. See contributor rule `wawona-optional-software`.

Deb builds are normal processes (fork/JIT allowed). They do not carry App Store no-fork patches.

Port fidelity still applies: same protocols and windowing path as upstream on Linux over waypipe. Substitute libc, EGL to ANGLE, DRM to iland. Display backend remains a user setting (`auto` / `wayland` / `drm`).
