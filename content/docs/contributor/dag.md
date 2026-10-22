+++
aliases = ["docs/dag"]
title = "Repo DAG"
description = "Acyclic L0-L4 flake inputs. Never invert."
weight = 21
date = 2026-08-13

+++

Canonical: [wwn-repo-dag.md](https://github.com/Wawona/Wawona/blob/development/docs/wwn-repo-dag.md).

{% mermaid() %}
flowchart BT
  toolchain["L0 wwn-toolchain"]
  iland["L1 iLand"]
  catalog["catalog repo.wawona.io"]
  peers["L3' waypipe ssh zsh relay"]
  app["L4 Wawona"]
  toolchain --> iland --> app
  toolchain --> catalog --> app
  toolchain --> peers --> app
  iland --> app
{% end %}

## Wawona flake inputs today

`wwn-toolchain`, `iLand`, `wwn-zsh`, `wwn-ssh`, `wwn-waypipe`, `Wawona-Swinging-Bridge`, `wwn-uutils-rs`, `wwn-relay`, `Doorman`, `iGetty`, `iomfb-rs`, `iowatchdog-tools`, plus nixpkgs, rust-overlay, crate2nix, microvm, nix-appimage. Weston and niri are not fork repos. They ship as debs from the [repo.wawona.io catalog](https://repo.wawona.io/deb).

L0 never imports L1+. Graphics keys (ANGLE, SwiftShader, MoltenVK, KosmicKrisp) live in L1. cairo/pango/pixman stay L0.

## Not flake-wired

Retired `wwn-apt`, `wwn-runtime` (consolidated into Wawona Relay), DE skeletons, [wwn-mcp](@/docs/contributor/wwn-mcp.md)
(contributor Cursor RAG. Stdio install), this site. Do not document them as
product inputs. Optional software = Wawona Relay Wasm packages, not StoreKit
`apt`.

Never treat [repo.wawona.io](https://github.com/Wawona/repo.wawona.io) (jailbreak Procursus APT) as Wawona docs.
