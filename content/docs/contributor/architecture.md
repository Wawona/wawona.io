+++
aliases = ["docs/architecture"]
title = "Architecture"
description = "Rust compositor, native hosts, userspace DRM. Not UniFFI-only."
weight = 20
date = 2026-08-25

+++

Mission: **run any desktop software, on any platform, natively.** Canonical: [wawona-mission-and-architecture.md](https://github.com/Wawona/Wawona/blob/development/docs/wawona-mission-and-architecture.md).

Wawona is an L4 app: a Rust Wayland compositor plus native frontends. It does not assume a host compositor or a kernel DRM device.

## Layout

| Path | Owns |
|------|------|
| `src/core` | Protocols, surfaces, windows, input, scene |
| `src/ffi` | UniFFI + `WWNCore*` C poll ABI (Swift/JNI call it) |
| `src/platform/android` | JNI glue |
| `src/linux` | GTK UI |
| `Sources/WawonaModel` | Shared Swift model |
| `Sources/WawonaUI` | SwiftUI Machines / Welcome / Settings |
| `Sources/WawonaWatch` | watchOS companion |
| `Sources/WawonaApple` | Apple framework glue (Metal, seat, lifecycle, runners). No ObjC classes |
| `Darwin/` | Apple `@main` entry |

Layout rules: [2026-SOURCE-LAYOUT-RULES.md](https://github.com/Wawona/Wawona/blob/development/docs/2026-SOURCE-LAYOUT-RULES.md).

## Delivery

Clients arrive as **native ports**, **containers**, or **VM / remote over waypipe-rs 0.11.0**. Graphics go through `wwn-iland` userspace DRM/KMS/GBM ([iland](@/docs/contributor/iland.md)): never a real `/dev/dri`. Classic Desktop Replacement maps that KMS path to fullscreen Metal with WindowServer down.

Do not hand-count Wayland globals. See the generated [Protocols](@/docs/contributor/protocols.md) page.
