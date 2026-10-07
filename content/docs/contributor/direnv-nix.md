+++
title = "Reproducible development with Nix and direnv"
description = "Use Wawona's pinned flake through nix-direnv without putting signing credentials in Git or the Nix store."
+++

Wawona's development environment is defined by `flake.nix` and pinned by
`flake.lock`. [nix-direnv](https://github.com/nix-community/nix-direnv) makes
the flake shell persistent and cached when you enter the checkout.

## Setup

Install Nix, direnv, and nix-direnv. On macOS, use a modern Bash through Nix,
Homebrew, or Home Manager. Then clone Wawona and run:

```sh
cp .envrc.local.example .envrc.local
direnv allow
```

The committed `.envrc` loads `.envrc.local` first, then runs `use flake`.
`flake.lock` is the reproducibility boundary. Do not replace this with an
unlocked `nix-shell` setup or manually installed compiler list.

## Signing stays local

`.envrc.local` is ignored. Put `TEAM_ID` and paths to your local certificate
and provisioning profile there. Keep passwords in `pass` or SecretSpec, never
in `flake.nix`, `.envrc`, Nix derivations, CI logs, or Git.

Use the normal development shell for builds. A signed Apple release needs the
local signing inputs and an explicit impure invocation because Nix otherwise
intentionally cannot read environment secrets:

```sh
nix build --impure .#wawona-ios-ipa
```

See [Compilation](@/docs/contributor/compilation.md),
[Nix build system](@/docs/contributor/nix-build-system.md), and the
[nix-direnv flake guide](https://github.com/nix-community/nix-direnv#flakes-support).
