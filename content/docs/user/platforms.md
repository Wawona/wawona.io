+++
aliases = ["docs/platforms"]
title = "Platforms"
description = "Four gate states: available, planned, blocked, forbidden."
weight = 5
date = 2026-09-11

+++

Never say "unsupported". Each cell is one of four states.

| Mark | State | Meaning |
|------|--------|---------|
| available | Shipping | Keep it green |
| planned | Platform allows it; our work is unfinished | Finish it |
| blocked | We want it; no public API | Re-check SDKs; no private API |
| forbidden | Product or store policy | Never enable |

## Capability matrix

| Capability | macOS | Android | iPadOS | visionOS | iOS | tvOS | watchOS |
|---|---|---|---|---|---|---|---|
| Native machines | available | available | available | available | available | available | available |
| Remote (SSH/waypipe) | available | available | available | available | available | available | available |
| VM / containers | planned | planned | planned | **forbidden** | planned | forbidden | forbidden |
| Hypervisor.framework (VM only) | lab-only (product VM is VZ) | forbidden | planned Mode B window | forbidden | planned Mode B window | forbidden | forbidden |
| Multi-window | available | if OS allows | required | required | single primary | forbidden | forbidden |
| Nested Weston + Niri | available | available | available | available | available | available | available (non-GL fallback) |
| Vulkan / GLES | available | available | available | available | available | available | blocked |
| Desktop + LockScreen | planned | planned | forbidden (App Store) | forbidden | forbidden (App Store) | forbidden | forbidden |
| Wawona Swinging Bridge | planned | planned | Mode B only (not App Store) | forbidden | Mode B only (not App Store) | forbidden | forbidden |
| iCloud Drive (shell HOME) | available | omitted | available | available | available | blocked | blocked |

Linux: native + remote available; VM/containers planned (KVM); Desktop/LockScreen and Wawona Swinging Bridge forbidden.

## Notes

- **iOS and iPadOS** share Desktop/LockScreen and Swinging Bridge policy (store Mode A vs TrollStore / Sileo Mode B). See [Mode A and Mode B](@/docs/user/mode-a-b.md).
- **VM / containers**. Engine is **Wawona Relay**. Mode A store iOS uses StaticCpu. Mode B may use Hypervisor.framework on M1 / M2 / A16 with iOS/iPadOS ≤16.3.1. macOS product path is Virtualization.framework. **visionOS, tvOS, and watchOS forbid VM/container kinds.** See [VMs and containers](@/docs/user/vms-containers.md) and [relay-ios-hypervisor.md](https://github.com/Wawona/Wawona/blob/development/docs/relay-ios-hypervisor.md).
- **Not the product engine:** QEMU, TCTI, UTM. Third-party UTM guests may still be used over SSH + waypipe.
- **On-device shell**. Bundled zsh (Mode A); Mode B may use unsandboxed jailbreak shell. See [On-device shell](@/docs/user/shell.md).
- **Desktop / LockScreen**. macOS Classic Take Over is implemented on desktop-host; LockScreen greeter and Android Home still planned. iOS/iPadOS via TrollStore / [repo.wawona.io](https://repo.wawona.io). See [Desktop and LockScreen](@/docs/user/desktop.md).
- **Wawona Swinging Bridge**. Separate host-app → Wayland bridge. See [Wawona Swinging Bridge](@/docs/user/swinging-bridge.md).
- **Wasm packages**. Mode A-safe Runtime packages. Browse [`/search/?channel=wasm`](https://repo.wawona.io/search/?channel=wasm), install with `wpm`. See [Packages](@/docs/user/packages.md) and [WASM](@/docs/user/wasm.md).
- **tvOS GPU** is available: OpenGL ES (ANGLE to Metal) and Vulkan (MoltenVK to Metal). **watchOS present** is SpriteKit. **watchOS GL/VK** is blocked: no `Metal.framework` in the SDK.
- **iCloud Drive** (Settings → iCloud Sync for shell HOME) is blocked on tvOS and watchOS.
- **macOS** is never limited by App Store feature rules.

Typing uses the host keyboard on every row. No in-app layout list. See
[Keyboard and IME](@/docs/user/keyboard.md).

More: [macOS](@/docs/user/macos.md), [Android](@/docs/user/android.md).
