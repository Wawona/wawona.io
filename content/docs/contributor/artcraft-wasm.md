+++
aliases = ["docs/artcraft-wasm", "docs/artcraft-crafting-apps"]
title = "ArtCraft wasm packages"
description = "Map ArtCraft Crafting Apps to Wawona /wasm/v1. Browser web is wrong ABI; pilot is EffectCraft expr WASI."
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

## Pilot

| Catalog id | Upstream | Version | What it is |
|------------|----------|---------|------------|
| [`effectcraft-expr`](https://repo.wawona.io/search/?channel=wasm&query=effectcraft-expr) | [storytold/effectcraft](https://github.com/storytold/effectcraft) v0.6.0 | `0.6.0` | WASI CLI: expression `check_syntax` only |

```text
wpm install effectcraft-expr
wasm effectcraft-expr '1+1'
# ok
```

This is **not** browser parity, not the full EffectCraft GUI, and not
`effectcraft-cli` (still blocked: ui-egui/gpu). Full GUI needs a real Wayland
or software path, not `xtask web` reuse.

## Fan-out

Other Crafting Apps (`photocraft`, `vectorcraft`, …) and `effectcraft` /
`effectcraft-cli` stay **blocked** in the wasm-packages allowlist until each
has a green wasip1 recipe. `craft-fonts` is fonts only (asset dep, not a Runtime
package). Builds run on GitHub Actions in
[`Wawona/wasm-packages`](https://github.com/Wawona/wasm-packages), not laptop
blobs.

## Related

- [WASM / WASI](@/docs/user/wasm.md) (user install)
- [Wasm host ABI](@/docs/contributor/wasm-host-abi.md)
- [Wayland wasm](@/docs/contributor/wayland-wasm.md)
