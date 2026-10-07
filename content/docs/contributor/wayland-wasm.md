+++
aliases = ["docs/wayland-wasm", "docs/wasm-wayland"]
title = "Wayland wasm"
description = "Write real Wayland clients for Wawona Runtime (WASI P1). wl_shm, xdg, host fd bridge."
weight = 29
date = 2026-10-06
+++

Build a **real Wayland client** as `wasm32-wasip1` and run it inside Wawona via
Relay’s Runtime (`wasm` / `wpm`). Full import table:
[Wasm host ABI](@/docs/contributor/wasm-host-abi.md). User install path:
[WASM / WASI](@/docs/user/wasm.md).

## What you are building

A guest that speaks the same protocols as a Linux `weston-simple-shm`:

- `wl_compositor` + `wl_surface`
- `wl_shm` + pool/buffer (XRGB8888 or ARGB8888)
- `xdg_wm_base` / `xdg_surface` / `xdg_toplevel`

Pixels go into Wawona’s compositor (iland present on Apple/Android). There is
**no** Wawona-specific draw API. Host imports only fix WASI gaps: unix connect
to `WAYLAND_DISPLAY`, anonymous SHM, and `SCM_RIGHTS` on `sendmsg`.

Port fidelity: if the same client built on Linux and streamed over waypipe
looks different, the wasm port is wrong, not the compositor. See
[Porting](@/docs/contributor/porting.md).

## Prerequisites

1. A live Wayland display from Wawona (start a Machines session / nested
   weston/niri, or run under the host compositor). `WAYLAND_DISPLAY` and
   usually `XDG_RUNTIME_DIR` must be set (Runtime defaults
   `XDG_RUNTIME_DIR=/tmp/wawona-$UID`, `WAYLAND_DISPLAY=wayland-0`).
2. Toolchain for `wasm32-wasip1` (Rust, Go, Swift, wasi-sdk, Zig, …).
3. Relay Runtime on PATH inside the shell (`wasm`), or `wpm install` then
   `wasm <name>`.

## Minimal sequence

```text
1. wawona_wayland_connect(&wl_fd)
2. wl_display.get_registry + sync; bind compositor, shm, xdg_wm_base
3. create_surface → get_xdg_surface → get_toplevel → set_title → commit
4. wawona_wayland_shm_create(size, &shm_fd)
5. Paint pixels in guest memory → wawona_wayland_shm_write(shm_fd, …)
6. wl_shm.create_pool via wawona_wayland_sendmsg(wl, req, len, shm_fd)
7. create_buffer, wait xdg_surface.configure, ack_configure
8. attach + damage + commit
9. Event loop: wawona_socket_recv on wl_fd; handle ping, configure, close
```

Use `wawona_wayland_sendmsg` for every request that needs an fd, and for
ordinary requests with `scm_fd = -1` if you route all traffic through the host
helper. Protocol detail:
[`PROTOCOL.md`](https://github.com/Wawona/Relay/blob/development/import/wasm/examples/wayland-shm/PROTOCOL.md).

## Starter templates

| Goal | Example | Notes |
|------|---------|-------|
| Smallest GUI smoke | [`hello-wasi-gui`](https://github.com/Wawona/Relay/tree/development/import/wasm/examples/hello-wasi-gui) | One buffer. Bundled on every product target |
| Interactive SHM | [`wayland-shm`](https://github.com/Wawona/Relay/tree/development/import/wasm/examples/wayland-shm) | Seat, resize, checkbox, typing. Rust / Go / Swift |
| Full Wayland app (catalog) | [`chess-wawona`](https://repo.wawona.io/search/?channel=wasm&query=chess-wawona) | Chess + variants; see showcase below |
| CLI + TCP | [`examples/rust`](https://github.com/Wawona/Relay/tree/development/import/wasm/examples/rust) | Sockets only |

```bash
cd Relay/import/wasm/examples/hello-wasi-gui/rust && ./build.sh
# artifact: dist/hello-wasi-gui.wasm

# In Wawona shell:
wasm ./hello-wasi-gui.wasm
# or:
wpm install ./hello-wasi-gui.wasm
wasm hello-wasi-gui
```

```bash
rustup target add wasm32-wasip1
cargo build --target wasm32-wasip1 --release
```

## Showcase: `chess-wawona`

Published Mode A package on
[`repo.wawona.io/wasm/v1`](https://repo.wawona.io/search/?channel=wasm&query=chess-wawona).
Source: [`chess-for-linux/wasm`](https://github.com/cube-one-ber/chess-for-linux/tree/main/wasm)
(GPL-3.0-or-later). Same rules/engine Rust as the native Linux app; the wasm
frontend is a **real Wayland client** (`wl_compositor`, `wl_shm`, `xdg_wm_base`,
`wl_seat`). No Qt, no browser. Optional `wawona_vk_*` host imports can paint the
Wood 3D scene when present; pixels still leave through `wl_shm`. Without those
imports, the software 2D board runs.

In a Wawona shell with a live compositor:

```text
wpm install chess-wawona
wasm chess-wawona
```

Controls (2D path): click/tap piece then destination; type UCI/SAN and Enter;
Crazyhouse drops like `N@e4`; on-screen New / Undo / Redo / AI / Variant
(Standard, Crazyhouse, Suicide, Losers). No file save or network in this build.

Build from source (developers):

```bash
git clone https://github.com/cube-one-ber/chess-for-linux
cd chess-for-linux
rustup target add wasm32-wasip1
./scripts/build-wasm.sh
# → artifacts/wasm/packages/chess-wawona/<version>/component.wasm
wasm ./artifacts/wasm/packages/chess-wawona/*/component.wasm
```

Use this as the reference for a non-trivial Wayland wasm app: host ABI for
connect + SHM + seat traffic, catalog `kind: wayland`, honest package version,
and [port fidelity](@/docs/contributor/porting.md) against the Linux client.

## Publishing to the catalog

1. Package is bytecode under `/wasm/v1` (Mode A). See
   [repo.wawona.io wasm-abi](https://github.com/Wawona/repo.wawona.io/blob/development/docs/wasm-abi.md)
   and [`Wawona/wasm-packages`](https://github.com/Wawona/wasm-packages).
2. Catalog `version` is the **software** version, not the ABI label.
3. Prefer a real upstream port with the upstream release version. Scratch demos
   use honest `wawona-*` names.
4. GUI packages still speak protocol bytes, not a private host draw ABI.

Browse: [`repo.wawona.io/search/?channel=wasm`](https://repo.wawona.io/search/?channel=wasm).

## GPU / EGL / Vulkan

| Path | Status |
|------|--------|
| `wl_shm` + xdg | **Supported** portable GUI (required smoke: `hello-wasi-gui`) |
| Wayland-EGL / GLES via ANGLE | Native clients first; wasm GPU is not the store baseline |
| `wawona_vk_*` board imports | Experimental; not the Wayland contract |
| watchOS | SHM + SpriteKit present only. No Metal/GLES wasm |

Do not re-host a Wayland client onto a fake KMS path because EGL is unfinished.

## Hard rejects

- Custom `wawona_draw_*` instead of Wayland
- Assuming host TLS (`wawona_socket_tls_connect_host` is `ENOSYS`)
- Mixing WASI fds with host Wayland/SHM fds
- Shipping Cranelift / `MAP_JIT` for store Apple mobile
- Claiming the guest is a VM or container

## Related

- [Wasm host ABI](@/docs/contributor/wasm-host-abi.md)
- [Porting](@/docs/contributor/porting.md)
- [WASM / WASI](@/docs/user/wasm.md) (users)
- Gate: Wawona workflow `wasm-wayland.yml`
