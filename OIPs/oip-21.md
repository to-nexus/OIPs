---
oip: 21
title: System Contract Upgrades at Fork Boundaries
description: Ordered code, storage, and initialization changes for protocol contracts at execution fork boundaries.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 19
---

# OIP-21: System Contract Upgrades at Fork Boundaries

## Abstract

This proposal records the reference client's fork-driven system contract installation and replacement rules.
It covers the Prague history contract and Breakpoint PoSA contracts, separately from the genesis allocations in [OIP-18](oip-18.md).

## Motivation

Independent clients must reproduce code and storage changes at the same block and execute initialization calls in the same order.
A proxy address alone does not identify the implementation or its initialization state.

## Specification

### Activation and Ordering

A fork boundary occurs when the parent does not satisfy the fork predicate and the child does.
The reference registry applies Prague changes first and Breakpoint changes second when both boundaries occur in the same block.
The Breakpoint registry and its initialization calls are skipped when `istanbul` or its `posa` configuration is absent.
Registry lookup uses a chain-specific entry when present and otherwise the entry for chain ID `0`.
A fork already active at genesis has no boundary, so its registry entry is never applied; the genesis allocation MUST then contain the corresponding code and storage.

On the ordinary Istanbul processing path, these changes occur during finalization after ordinary transactions.
Import and block assembly MUST use the same registry and ordering.
The earlier parent-hash system call and its first-fork-block implications are specified in [OIP-31](oip-31.md).

### Installed State

| Boundary | Address | Change |
| --- | --- | --- |
| Prague | `0x0000F90827F1C53a10cb7A02335B175320002935` | Install the configured history-storage runtime. |
| Breakpoint | `0xfeed00000000000000000000000000000000C0DE` | Replace CrossEx runtime. |
| Breakpoint | `0x1001` / `0xa001` | ValidatorSet proxy / implementation. |
| Breakpoint | `0x1002` / `0xa002` | StakeHub proxy / implementation. |
| Breakpoint | `0x1003` / `0xa003` | RewardHub proxy / implementation. |
| Breakpoint | `0x1004` / `0xa004` | ValidatorSlash proxy / implementation. |

Short addresses in this table are left-padded to 20 bytes.
Each implementation receives the value `0xffffffffffffffff` in the OpenZeppelin `Initializable` slot `0xf0c57e16840df040f15088dc2f81fe391c3923bec73e23a9662efc9c229c6a00`, which disables its initializers.
Each proxy receives its implementation address in ERC-1967 slot `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`.
The complete runtime bytes and additional storage values are those in the pinned registry and embedded artifacts; they MUST NOT be replaced by artifacts from a newer contract build.

The reference updater writes nonempty replacement code, sets nonce `1` when first deploying to a previously nonexistent account, and overwrites only the explicitly listed storage slots.
It does not clear unrelated storage or balances.

### Initialization

Initialize ValidatorSet, StakeHub, RewardHub, and ValidatorSlash in that order using the signed system transactions in [OIP-19](oip-19.md).
ValidatorSet receives the configured administrator, validator addresses, and BLS keys.
StakeHub receives the delegation-pool address, administrator, operators, validators, BLS keys, and validator IDs.
ValidatorSet receives each configured BLS key normalized to 48 bytes, keeping its last 48 bytes or left-padding it with zeros, whereas StakeHub receives the configured bytes unchanged.
RewardHub receives the delegation-pool address, administrator, and reward start block.
ValidatorSlash receives the administrator.
The administrator and delegation-pool addresses MUST be nonzero, and the reward start block MUST be configured; operators SHOULD validate these values before the boundary.
A block whose initialization calls cannot be constructed or fail MUST NOT be accepted or produced.

## Rationale

Pinning the registry makes historical execution reproducible even after newer contracts exist.
Code installation and contract initialization are separate state transitions, so their ordering is explicit.

## Backwards Compatibility

This describes the existing registry rather than authorizing an upgrade.
Changing runtime bytes, storage writes, initialization arguments, or their position relative to transactions can change the state root.
Administrative proxy upgrades after installation are separate from this fork registry.

## Test Cases

| Case | Expected result |
| --- | --- |
| Parent before the boundary; child at or after it | Apply the corresponding registry exactly on that transition. |
| Prague and Breakpoint activate together | Apply Prague, then the configured Breakpoint entries. |
| Breakpoint with no PoSA configuration | Skip the whole Breakpoint registry entry, including the CrossEx replacement, and its initialization. |
| Existing proxy with unrelated storage | Preserve unrelated slots while writing the declared implementation slot. |
| Missing, reordered, or reverting initialization transaction | Reject the block or fail block assembly. |
| Breakpoint active at genesis | Apply no registry entry; take code and storage from the genesis allocation. |
| Replay from the same parent state | Match code hashes, storage, receipts, and the final state root. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Upgrade registry and application](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go).
- [Addresses and storage slots](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/const.go).
- [Finalization and initialization calls](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Existing upgrade tests, including Breakpoint runtime code-hash checks](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-21/verification.md).

## Implementation and Activation

Prague uses `IsOnPrague`; Breakpoint uses `IsOnBreakpoint` plus the presence of PoSA configuration.
The registry records contract source revisions, but a reproducible match between those source builds and embedded runtime bytes has not been established by this Draft.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Record independently reproduced runtime hashes and initializer argument vectors for each target network.
- Verify fork-boundary processing, genesis-active configurations, and replay across installed contract versions.

## Security Considerations

A wrong implementation slot or administrator changes authority over protocol state.
A registry update must preserve deterministic replay and avoid exposing an uninitialized proxy to transactions at an unintended point.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
