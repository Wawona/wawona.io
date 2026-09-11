+++
aliases = ["docs/vms", "docs/containers"]
title = "VMs and containers"
description = "Planned Machines kinds. Relay engine. Mode A StaticCpu on store iOS; Mode B may use Hypervisor.framework inside the UTM-era window."
weight = 3
date = 2026-09-11

+++

**Coming soon / planned.** Virtual machines and containers will be first-class **Machine** kinds. This is **not** the [on-device shell](@/docs/user/shell.md) and **not** [Wasm Runtime packages](@/docs/user/wasm.md).

Read [Mode A and Mode B](@/docs/user/mode-a-b.md) first (App Store vs TrollStore vs Sileo).

Engine: **[Wawona Relay](https://github.com/Wawona/Relay)**. Not QEMU. Not UTM as the product VM. Guest GUI is Wayland into Wawona (iland) over vsock + waypipe. You may still run a third-party UTM guest and connect with SSH + waypipe; that is not the Wawona Machines engine.

## iOS / iPadOS

| Channel | Engine |
|-------|--------|
| **App Store** (Mode A) | Relay **StaticCpu** (jitless). Planned. Fail closed. **No** Hypervisor.framework |
| **TrollStore** (Mode B tipa) | Same Relay. **`IosHv`** when SoC + OS + kernel probe pass (M1 / M2 / A16 on ≤16.3.1). Else StaticCpu. No Swinging Bridge by tipa alone |
| **Sileo** ([repo.wawona.io](https://repo.wawona.io)) | Same Relay HV window **plus** Desktop, LockScreen, Swinging Bridge Mode B |

Mode B is never shipped inside the App Store app. Store / TestFlight copy must not mention jailbreak, TrollStore, Hypervisor, or JIT. This page may.

Wasm stays `/wasm/v1` bytecode (Pulley on Apple mobile). MAP_JIT wasm is not Hypervisor.framework.

Canonical HV plan: [relay-ios-hypervisor.md](https://github.com/Wawona/Wawona/blob/development/docs/relay-ios-hypervisor.md).

## Platforms

| Platform | Gate | Path |
|----------|------|------|
| macOS | planned | **Virtualization.framework** + Apple [Containerization](https://github.com/apple/container). macOS HV is lab-only, not the product VM |
| iOS / iPadOS | planned | Relay StaticCpu (Mode A). Mode B may use Hypervisor.framework inside the window above |
| visionOS | **forbidden** | Native + remote + Wasm only. No VM/container kinds |
| Android | planned | Relay. Play = Mode A. Root = Mode B |
| Linux | planned | KVM via cloud-hypervisor or crosvm. Fail closed without `/dev/kvm` |
| tvOS / watchOS | **forbidden** | Native + remote only |

## Machine kinds

| `type` | Meaning |
|--------|---------|
| `virtual_machine` | Linux / NixOS guest via Relay |
| `container` | OCI unpack, then the same Linux VM backend |

Repo: [vms-containers.md](https://github.com/Wawona/Wawona/blob/development/docs/vms-containers.md).
