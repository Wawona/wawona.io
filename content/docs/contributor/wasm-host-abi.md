+++
aliases = ["docs/wasm-host-abi", "docs/relay-wasm-abi"]
title = "Wasm host ABI"
description = "Wawona Relay WASI P1 host imports: sockets, Wayland fd bridge, terminal. Rootshell-style reference."
weight = 28
date = 2026-10-06
+++

Canonical developer reference for host imports linked by the Wawona Runtime
(Relay `import/wasm`, product `libwawona_wasm.a` / `wasm` / `wpm` run).

Implementation: [`Relay/import/wasm/src/host.rs`](https://github.com/Wawona/Relay/blob/development/import/wasm/src/host.rs).
Wayland how-to: [Wayland wasm](@/docs/contributor/wayland-wasm.md).
Examples: [`Relay/import/wasm/examples/`](https://github.com/Wawona/Relay/tree/development/import/wasm/examples).

Vanilla **WASI Preview 1** plus thin host modules where P1 has no sockets, no
unix `SCM_RIGHTS`, and no TTY mode bit. Same documentation shape as
Rootshell’s runtime ABI, with Wawona module names.

## Model

| Piece | Role |
|-------|------|
| WASI P1 | argv, environ, preopens, stdio, clocks, random, exit |
| `wawona_socket` (+ `env` alias) | TCP/UDP/unix table, Wayland connect, SHM fd bridge, experimental VK board |
| `wawona_terminal` (+ `env` alias) | raw/cooked bit, `is_tty` |

**Import modules.** Prefer named modules (`wawona_socket`, `wawona_terminal`).
Rust `#[link(wasm_import_module = "env")]` also works: the host registers every
symbol on both the named module and `env`.

**Fd spaces.** Host socket / Wayland / SHM fds live in a **separate** table from
WASI filesystem fds. Do not pass a `wawona_socket_*` fd to WASI `fd_close`, and
do not pass a WASI fd to `wawona_socket_close`. Host fds start at `3` and grow.

**Return value.** Every call returns `i32` errno: `0` success, else a WASI errno
constant:

| Name | Value | Typical use |
|------|------:|-------------|
| `EACCES` | 2 | `sendmsg` / SCM_RIGHTS failed |
| `EBADF` | 8 | Unknown host fd |
| `EINVAL` | 28 | Bad args, OOB linear memory |
| `EIO` | 29 | Connect/read/write/interrupt failure |
| `ENOSYS` | 52 | Not implemented (TLS today) |

Pointers are **linear-memory offsets** (`i32`). Out-params write little-endian
`i32` into guest memory.

**Engines.** Store Apple mobile through iOS 26: Wasmtime **Pulley**. macOS /
Linux: Cranelift. iOS 27+ Mode A may use Wasmer WASIX in WebKit when linked.
These host imports are the P1 Wasmtime path. Do not assume Cranelift or
`MAP_JIT` in App Store IPAs.

## Constants

```c
#define AF_UNIX     1
#define AF_INET     2
#define AF_INET6    30
#define SOCK_STREAM 1
#define SOCK_DGRAM  2
```

## `wawona_socket` — networking

WASI P1 has no sockets. Use this table for TCP/UDP. Wayland uses the same table
for the display unix stream and SHM files.

### `wawona_socket_socket(domain, ty, fd_out) -> errno`

Create a host fd.

| `domain` / `ty` | Result |
|-----------------|--------|
| `AF_INET` or `AF_INET6` + `SOCK_STREAM` | TCP slot (connect with `connect_host`) |
| `AF_INET` or `AF_INET6` + `SOCK_DGRAM` | UDP bound to `0.0.0.0:0` |
| `AF_UNIX` + `SOCK_STREAM` | Placeholder until Wayland/unix connect path replaces it |

Writes the new host fd to `*fd_out`. Other pairs → `EINVAL`.

### `wawona_socket_connect_host(fd, host, host_len, port) -> errno`

TCP connect. `host` is UTF-8 hostname or IP literal of length `host_len`.
Replaces the table entry for `fd` with a connected `TcpStream` (`TCP_NODELAY`
on). Failure → `EIO`.

### `wawona_socket_send(fd, buf, len, sent_out) -> errno`

Write up to `len` bytes from guest memory. Sets `*sent_out` to bytes written.
Supports TCP, unix, and UDP table entries. Bad fd → `EBADF`.

### `wawona_socket_recv(fd, buf, len, recv_out) -> errno`

Blocking read into guest memory. Sets `*recv_out` to bytes read (`0` at EOF).
Ctrl+C / guest interrupt returns `EIO`. A successful read with `n > 0` refills
Wasmtime fuel so a GUI event loop is not starved mid-frame.

### `wawona_socket_close(fd) -> errno`

Drop the host table entry. `EBADF` if unknown.

### `wawona_socket_tls_connect_host(fd, host, host_len, port) -> errno`

**Always `ENOSYS` today.** Use a guest TLS stack over TCP, or wait for a
host TLS land.

### Not exposed yet

`bind` / `listen` / `accept` / `sendto` / `recvfrom` / DNS helpers,
`setsockopt` / `poll` / `select`, raw ICMP. Open an issue on
[`Wawona/Relay`](https://github.com/Wawona/Relay) if a store-safe knob is
required.

## `wawona_socket` — Wayland fd bridge

Not a custom draw API. Guests speak **real Wayland wire protocol**
(`wl_display`, `wl_shm`, `xdg_wm_base`, …) into Wawona’s existing compositor
socket (`WAYLAND_DISPLAY`). The host only supplies unix connect + anonymous
SHM + `SCM_RIGHTS` (missing from WASI).

Env used by `wawona_wayland_connect`:

| Variable | Default |
|----------|---------|
| `XDG_RUNTIME_DIR` | `/tmp/wawona-$UID` |
| `WAYLAND_DISPLAY` | `wayland-0` |

Socket path: `$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY`.

### `wawona_wayland_connect(fd_out) -> errno`

Unix-stream connect to the compositor. Writes a host fd to `*fd_out`.
Failure → `EIO`.

### `wawona_wayland_shm_create(size, fd_out) -> errno`

Allocate an anonymous file of `size` bytes (POSIX `shm_open` + unlink when
available; else a temp file under `XDG_RUNTIME_DIR`). Writes host fd to
`*fd_out`. `size <= 0` → `EINVAL`.

### `wawona_wayland_shm_write(shm_fd, offset, buf, len) -> errno`

Copy `len` bytes from guest memory into the SHM file at `offset`.

### `wawona_wayland_sendmsg(wl_fd, buf, len, scm_fd) -> errno`

`sendmsg` on the Wayland unix fd: protocol bytes from guest memory, optional
`SCM_RIGHTS` of `scm_fd` when `scm_fd >= 0`. Pass `scm_fd = -1` for ordinary
requests. This is how `wl_shm.create_pool` gets a real fd into the compositor.

### `wawona_wayland_shm_send(wl_fd, shm_fd) -> errno`

Legacy helper: one dummy byte + `SCM_RIGHTS` of `shm_fd`. Prefer
`wawona_wayland_sendmsg` with real protocol bytes (see the wayland-shm
example).

## Experimental Vulkan board

Lab / demo path. Not the store Wayland GUI contract. Prefer `wl_shm` for
portable GUI (including watchOS SpriteKit present).

| Symbol | Meaning |
|--------|---------|
| `wawona_vk_probe() -> i32` | Non-zero if board path available |
| `wawona_vk_upload(desc) -> errno` | Upload SPIR-V / verts / texture layers from a guest descriptor |
| `wawona_vk_frame(desc) -> errno` | Rasterize into guest RGBA buffer |

Descriptor layouts live in `host.rs`. Treat as unstable.

## `wawona_terminal` — raw vs cooked

```c
i32 wawona_terminal_set_raw(i32 enabled);  /* 0 cooked, 1 raw */
i32 wawona_terminal_is_tty(i32 fd);        /* 1 if fd is 0/1/2 */
```

`set_raw` stores a process-scoped bit the shell host can observe (TUIs).
`is_tty` returns `1` for WASI fds 0–2, else `0`. When the wasm process exits,
the host restores cooked behaviour.

## Language bindings

```rust
#[link(wasm_import_module = "wawona_socket")]
extern "C" {
    fn wawona_wayland_connect(fd_out: *mut i32) -> i32;
    fn wawona_wayland_shm_create(size: i32, fd_out: *mut i32) -> i32;
    fn wawona_wayland_shm_write(shm_fd: i32, offset: i32, buf: *const u8, len: i32) -> i32;
    fn wawona_wayland_sendmsg(wl_fd: i32, buf: *const u8, len: i32, scm_fd: i32) -> i32;
    fn wawona_socket_recv(fd: i32, buf: *mut u8, len: i32, n_out: *mut i32) -> i32;
}
```

Go: `//go:wasmimport wawona_socket wawona_wayland_connect`.
Swift: `@_extern(wasm, module: "wawona_socket", name: "wawona_wayland_connect")`.

| Example | Repo path |
|---------|-----------|
| CLI + sockets | `Relay/import/wasm/examples/rust` |
| Wayland SHM interactive | `Relay/import/wasm/examples/wayland-shm` |
| Minimal GUI smoke | `Relay/import/wasm/examples/hello-wasi-gui` |
| WASI P2 | `Relay/import/wasm/examples/wasip2` (standard `wasi:*`, not this host ABI) |

## C host entry (native side)

Product link (`wawona_wasm.h`):

- `wawona_wasm_can_run(path)`
- `wawona_wasm_run(argc, argv)`
- `wawona_terminal_raw_enabled()`

Package CLI: `wpm`. Catalog: [`repo.wawona.io/wasm/v1`](https://repo.wawona.io/wasm/v1).
User-facing: [WASM / WASI](@/docs/user/wasm.md), [Packages](@/docs/user/packages.md).

## Hard rejects

- Custom draw host instead of Wayland wire protocol for GUI
- Claiming TLS host ABI works (`ENOSYS`)
- Mixing WASI fds and host socket fds
- Cranelift / `MAP_JIT` / Mode B engines in App Store IPA
- Documenting Rootshell module names (`rootshell_*`) as Wawona imports

## Related

- [Wayland wasm](@/docs/contributor/wayland-wasm.md)
- Catalog ABI labels (P1 / WASIX publish): [repo.wawona.io wasm-abi](https://github.com/Wawona/repo.wawona.io/blob/development/docs/wasm-abi.md)
- Source stub in Relay: [`docs/wasm-host-abi.md`](https://github.com/Wawona/Relay/blob/development/docs/wasm-host-abi.md) (points here)
