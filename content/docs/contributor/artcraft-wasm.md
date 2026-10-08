+++
aliases = ["docs/artcraft-wasm", "docs/artcraft-crafting-apps"]
title = "ArtCraft wasm packages"
description = "Map ArtCraft Crafting Apps to Wawona /wasm/v1. Browser web is wrong ABI; no Craft packages published until Wayland."
weight = 30
date = 2026-10-08
+++

ArtCraft **Crafting Apps** (`storytold/*craft`) are clean-room Rust apps
(After Effects / Photoshop / … analogs). They are **not** the AI studio IDE
[`storytold/artcraft`](https://github.com/storytold/artcraft).

Site index: <https://getartcraft.com/apps>.

Full matrix and crate inventory live in
[`wasm-packages/docs/artcraft-crafting-apps.md`](https://github.com/Wawona/wasm-packages/blob/development/docs/artcraft-crafting-apps.md).

## ABI gap (hard)

| Lane | Target | Wawona `/wasm/v1` |
|------|--------|-------------------|
| ArtCraft Web (`cargo xtask web`) | `wasm32-unknown-unknown` + eframe/WebGPU + JS glue | **No.** Wrong ABI for Relay |
| Wawona Runtime (`wpm` / Pulley) | `wasm32-wasip1` | Catalog path |

Do not publish `*_bg.wasm` + JS as `component.wasm`. Hosting a static web dist
elsewhere is fine; it is not today’s `wpm` catalog.

## Catalog status

**No ArtCraft / EffectCraft packages are published on `/wasm/v1` right now.**
The short-lived `effectcraft-expr` CLI slice was **pulled** until there is a
real **egui → Wayland** path (`wl_shm` baseline; GPU WSI later). A
`check_syntax` WASI binary is not the Crafting Apps product.

Republish only after a shared wasip1 Wayland runner exists and at least one
Craft app speaks it.

## Fan-out

All Crafting Apps (`effectcraft`, `photocraft`, …), `effectcraft-cli`, and
`effectcraft-expr` stay **blocked** (and pruned from the live index) in the
wasm-packages allowlist. `craft-fonts` is fonts only. Builds run on GitHub
Actions in [`Wawona/wasm-packages`](https://github.com/Wawona/wasm-packages),
not laptop blobs.

## Related

- [WASM / WASI](@/docs/user/wasm.md) (user install)
- [Wasm host ABI](@/docs/contributor/wasm-host-abi.md)
- [Wayland wasm](@/docs/contributor/wayland-wasm.md)
