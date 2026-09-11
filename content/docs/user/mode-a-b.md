+++
aliases = ["docs/mode-a-b", "docs/mode-b", "docs/trollstore", "docs/sileo-mode-b"]
title = "Mode A and Mode B"
description = "Store Mode A vs TrollStore vs Sileo Mode B: Relay VMs, containers, Wasm, Desktop, Swinging Bridge."
weight = 4
date = 2026-09-11

+++

Wawona has two privilege classes. **App Store / Play builds are always Mode A.** Mode B is for TrollStore sideload, jailbreak (Sileo), SIP-disabled macOS Desktop, and privileged Android. Never inside the store binary.

Canonical: [mode-a-b.md](https://github.com/Wawona/Wawona/blob/development/docs/mode-a-b.md). Agent rule: [iOS Mode B channels](https://github.com/Wawona/Wawona/blob/development/docs/agent-rules/wawona-ios-mode-b-channels.md).

## iOS / iPadOS: three install channels

| Channel | How you install | VMs / containers | Wasm | Desktop + LockScreen | Swinging Bridge |
|--|--|--|--|--|--|
| **App Store / TestFlight** | Apple | Relay **StaticCpu** (jitless). No Hypervisor | Bytecode, **no** JIT | No | No |
| **TrollStore** | Sideload tipa (website) | Relay. **Hypervisor.framework** when SoC + OS ≤16.3.1 + kernel probe pass; else StaticCpu | Same `/wasm/` packages; JIT execute may be allowed later | Yes (IOMFB in-app) | No |
| **Sileo (`repo.wawona.io`)** | Jailbreak + Sileo | Same Relay HV window as tipa | Same | **Yes** (+ ElleKit) | **Yes** |

App Store and TestFlight materials must **never** mention TrollStore, Sileo, jailbreak, Hypervisor, or JIT. This site and [repo.wawona.io](https://repo.wawona.io) may.

### TrollStore

[TrollStore](https://github.com/opa334/TrollStore) installs a Mode B tipa. Relay owns the VM engine:

- Linux guests via **Wawona Relay** (not QEMU, not UTM-as-product)
- On M1 / M2 / A16 devices still on **iOS/iPadOS ≤16.3.1**, Mode B may use **Hypervisor.framework**
- On newer OS or other SoCs, Mode B falls back to Relay StaticCpu
- Wasm packages stay bytecode under `/wasm/`

TrollStore alone does **not** install Wawona Swinging Bridge Mode B (Sileo only).

### Sileo (full Mode B)

On a jailbroken device, install from [repo.wawona.io](https://repo.wawona.io). Same Relay VM story as tipa, **plus** Desktop, LockScreen, Swinging Bridge, unsandboxed shell, and host APT.

## Relay on iOS (not QEMU)

```text
App Store          →  Relay StaticCpu. No Hypervisor.framework. No MAP_JIT.
TrollStore / Sileo →  Relay. IosHv when probe window matches; else StaticCpu.
Wasm (all)         →  /wasm/v1 bytecode. Apple mobile execute = Pulley.
```

Same guest images and Machines UI. Different install channel. Never a store binary with a hidden “enable HV” or “enable JIT” switch.

HV plan and device tables: [relay-ios-hypervisor.md](https://github.com/Wawona/Wawona/blob/development/docs/relay-ios-hypervisor.md).

## Quick matrix (all platforms)

| | Mode A | Mode B |
|--|--------|--------|
| Who | App Store, TestFlight, Play | TrollStore / Sileo / SIP / root |
| iOS VMs and containers | Relay StaticCpu | Relay; Hypervisor.framework inside the UTM-era window |
| macOS VMs | Virtualization.framework | Same product path (Desktop Mode B is separate) |
| iOS shell | Sandboxed `wwn-zsh` | Unsandboxed / host APT (Sileo) |
| Desktop / LockScreen (iOS) | Not in the store app | TrollStore IOMFB and/or Sileo |
| Packages | Wasm from `repo.wawona.io/wasm/v1` + Files + `wpm` | Same wasm registry **plus** jailbreak `.deb` on Sileo |

## Related

- [VMs and containers](@/docs/user/vms-containers.md)
- [WASM / packages](@/docs/user/wasm.md) · [Packages (search / wpm / apt)](@/docs/user/packages.md)
- [Desktop](@/docs/user/desktop.md) · [Wawona Swinging Bridge](@/docs/user/swinging-bridge.md)
