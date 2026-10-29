---
oip: 17
title: Adventure Hardfork
description: Included specifications, activation conditions, and compatibility boundaries of the Adventure hardfork.
author: ONEchain Contributors
status: Review
type: Meta
created: 2026-10-28
requires: 2, 3, 4, 5, 6, 7, 8, 9, 11
---

# OIP-17: Adventure Hardfork

## Abstract

This proposal collects the specifications that define ONEchain's Adventure hardfork.
Adventure combines fee-delegated transactions and native coin transfer logs with a Shanghai-based execution environment and early adoption of transient storage and memory copying instructions.
The profile retains ONEchain's Istanbul consensus, fee accounting, and randomness conventions.

This Meta document records existing behavior and its specification dependencies.
It does not schedule a new activation or establish that the reference configuration matches a deployed network's historical configuration.

## Motivation

An Ethereum fork name alone does not describe ONEchain's execution rules.
Adventure adopts selected execution features without adopting Ethereum Beacon consensus, and some rules have different activation predicates or ONEchain-specific behavior.
Clients and applications need one place to identify the included specifications and inherited rules.

Individual OIPs define behavior that can be reviewed independently.
This document connects those specifications into an identifiable network upgrade without duplicating their transaction formats, execution algorithms, or service interfaces.

## Specification

### Scope and Dependencies

The Adventure profile describes Istanbul networks with the earlier execution forks through London and Shanghai active, before a later execution fork supersedes the Adventure instruction table.
It distinguishes rules enabled by Adventure from rules inherited from the configured execution and consensus baseline.
Activating Adventure does not independently enable every rule listed below.

[OIP-2](oip-2.md) and [OIP-3](oip-3.md) define Adventure's transaction and transfer-log additions.
The `requires` field lists the OIPs needed to define the profile's execution and consensus rules.
The Shanghai instruction changes and Adventure opcode additions below adopt their linked upstream specifications by reference, subject to this document's activation conditions and ONEchain compatibility rules.
[OIP-4](oip-4.md) also describes how Istanbul consensus is retained while adopting post-merge execution features.

| Specification or feature | Included scope | Relationship to Adventure |
| --- | --- | --- |
| OIP-2 | Fee-delegated dynamic fee transactions, type `0x07`, sender/payer authorization, gas payment, and receipts. | Enabled by Adventure; ordinary legacy, access-list, and dynamic-fee transactions remain supported. |
| OIP-3 | Protocol-generated native coin transfer logs and their receipt commitments. | Enabled by Adventure for qualifying transfers, independently of transaction type. |
| [OIP-9](oip-9.md) | Base fee calculation, block gas limits, and [EIP-3198][eip3198] `BASEFEE`, with the ONEchain differences from [EIP-1559][eip1559]. | Inherited London/Istanbul behavior, including parameter heights, bounds, and transition overrides. |
| [OIP-11](oip-11.md), execution fees | Execution fee crediting to the configured beneficiary. | Inherited Istanbul accounting. |
| Shanghai execution changes | [EIP-3651][eip3651] warm coinbase, [EIP-3855][eip3855] `PUSH0`, and [EIP-3860][eip3860] initcode limits and metering. | Shanghai execution baseline, with its separate activation condition. |
| Transient storage and memory copying | [EIP-1153][eip1153] `TLOAD`/`TSTORE` and [EIP-5656][eip5656] `MCOPY`. | Added to the Adventure instruction table. |
| [OIP-8](oip-8.md) | [EIP-4399][eip4399] opcode semantics adapted to Istanbul-derived randomness. | Inherited `PREVRANDAO` instruction with ONEchain's random-reveal and Istanbul digest rules. |
| [OIP-4](oip-4.md) and [OIP-5](oip-5.md), execution compatibility | Ethereum Merge/Beacon assumptions and [EIP-4895][eip4895] withdrawal differences. | Defines the limits of Shanghai adoption on an Istanbul network. |
| [OIP-6](oip-6.md) | Istanbul QBFT consensus, validator authorization, seals, header commitments, and voting. | Inherited consensus baseline. |
| [OIP-7](oip-7.md) | Istanbul consensus messages, round changes, timeouts, and proposer selection. | Inherited consensus protocol. |
| [OIP-18](oip-18.md), informative network context | Applicable genesis predeploys and reserved addresses. | Network presets; Adventure does not itself trigger a system-contract replacement. |

### Activation and Fork Ordering

Let `n` and `t` be the executing block's number and timestamp, and let `T` be the configured `AdventureTime`.
The Adventure predicate is:

```text
AdventureActive(n, t) = LondonActive(n) and T is configured and t >= T
```

An unset `AdventureTime` disables that predicate.
A value of `0` satisfies its timestamp condition from genesis onward; the London prerequisite still applies.
The first block satisfying the predicate uses the Adventure rules, and earlier blocks retain their applicable historical rules.

A valid configuration for this profile includes the prerequisite execution forks and a configured `ShanghaiTime` no later than `AdventureTime`.
The Adventure predicate itself does not check `ShanghaiTime`.
Clients must preserve the separate Shanghai checks used for coinbase warming, contract-creation transaction metering, and initcode-size validation, as well as the inherited Shanghai instruction table.
Enabling only the Adventure opcodes is not a complete implementation of this profile.

For continuous Istanbul block production with the reference client, Shanghai and Adventure must activate together.
While Shanghai is active and Adventure is not, the reference client's `IsPostMerge` predicate selects post-merge block preparation; its engine wrapper then prepares zero-difficulty headers instead of invoking Istanbul preparation.
Adventure suppresses that selection, while fork-order validation prevents it from preceding Shanghai.
The resulting deployment constraint is `ShanghaiTime = AdventureTime` for the reference client, in addition to the general execution predicates above.
An alternative schedule requires resolving this client integration first; isolated Shanghai execution tests do not establish a working block-production configuration.

Historical execution must evaluate the complete chain configuration; `AdventureTime` alone does not identify the entire rule set.

### ONEchain Compatibility Rules

Adventure uses Shanghai execution semantics with EIP-1153 and EIP-5656 enabled.
`SELFDESTRUCT` retains its legacy behavior.

#### Fees and Gas Limits

Adventure retains `BASEFEE` and the dynamic-fee transaction model, with Istanbul-specific base fee parameters, bounds, and block gas limit transitions.
For Istanbul headers, the expected gas limit comes from the configured transition or, when no limit is configured, the parent header.
[OIP-9](oip-9.md) specifies the parameter lookup, calculation, and bound application.

Execution fees include the base fee component and are credited to the configured beneficiary, falling back to the execution coinbase when no beneficiary override is configured.
The base fee is not burned.
Fee delegation changes which account pays under OIP-2, not the fee recipient or the applicable base fee calculation.
[OIP-11](oip-11.md) specifies the recipient selection and accounting.

#### Randomness and Consensus

The inherited instruction at `0x44` exposes `PREVRANDAO`, but its value does not come from an Ethereum Beacon Chain.
For an Istanbul block, the reference implementation supplies the Keccak-256 hash of the header's `MixDigest` as the EVM random value.
The random-reveal path uses validator ECDSA signatures and the Istanbul digest construction.
[OIP-8](oip-8.md) specifies the derivation, verification, and proposer influence, with validator authorization defined by [OIP-6](oip-6.md).

Adventure retains Istanbul consensus and does not activate Ethereum's Merge consensus transition.
Applications must not infer Beacon randomness properties or Beacon validator behavior from the presence of the opcode.

#### Shanghai and Beacon Withdrawals

Shanghai adoption in this profile includes warm coinbase, `PUSH0`, and initcode limits and metering, not Ethereum Beacon withdrawal processing.
Under the Adventure-only profile, ordinary Istanbul blocks with block number greater than zero must omit `withdrawalsRoot`, and their bodies must omit the withdrawals list.

The reference genesis construction includes an empty withdrawal commitment and empty list when Shanghai is configured at genesis.
That genesis exception does not enable withdrawals in subsequent Adventure blocks.

#### Precompiles and Predeployed Contracts

Adventure introduces no additional precompile beyond its Berlin execution baseline, which uses addresses `0x01` through `0x09`.

Genesis predeploys are part of each network's initial state, not deployments performed by the Adventure predicate.
OIP-3 uses the reserved CrossEx address for its logs without requiring code at that address.
The reference client's fork-upgrade registry has no Adventure-specific system-contract replacement or initialization step.

### Related Interfaces

[OIP-13](oip-13.md) is a companion interface specification for OIP-2.
[OIP-16](oip-16.md) describes optional sponsorship service behavior.
Neither service availability nor a sponsorship policy is an Adventure block-validity requirement.
OIP-13 and OIP-16 are therefore companion interfaces rather than required dependencies; OIP-18 supplies informative network context.
Application standards remain separate ORCs.

## Rationale

A fork Meta document gives implementers a stable entry point while keeping detailed specifications independently reviewable.
The aggregation approach follows the purpose of Ethereum's [hardfork Meta documents][eip7568].

Separating inherited rules from Adventure-gated changes avoids assigning new activation semantics to existing London, Shanghai, or Istanbul behavior.
Explicit Ethereum differences are necessary because matching opcode availability does not establish matching consensus, fee distribution, withdrawals, or complete fork compatibility.
Links to the individual proposals and upstream EIPs make their review and adoption status explicit.

## Backwards Compatibility

This document itself changes no client behavior or network configuration.
Implementing Adventure on a network where it is not active changes accepted transaction types, opcode execution, and receipt logs at the activation boundary.
Clients using different rules can disagree on block validity, state roots, receipt roots, and blooms.

Wallets and sponsoring services need OIP-2 support to construct sponsored transactions, and receipt consumers need OIP-3 support to interpret the additional logs.
Existing contracts can continue to use previously available instructions, subject to the adopted Shanghai gas and initcode rules.
Contracts targeting additional instructions or different execution semantics may be incompatible with Adventure.

## Test Cases

The following are acceptance criteria for the combined profile, not a report of executed tests.
Individual transaction and log vectors remain in OIP-2 and OIP-3.
Boundary tests must use a configuration limited to the execution rules listed in this profile.

| Case | Expected result |
| --- | --- |
| `AdventureTime` unset, or `t < T`, with Shanghai active | No Adventure fee-delegated transactions or transfer logs; `TLOAD`, `TSTORE`, and `MCOPY` are unavailable; Shanghai behavior remains active. |
| `t = T`, with all prerequisites active | Type `0x07`, qualifying native transfer logs, transient storage, and memory copying are active in that block. |
| London inactive | Adventure predicate is false, regardless of its timestamp setting. |
| Missing Shanghai configuration or `ShanghaiTime > AdventureTime` | Fork-order validation rejects the configuration for this profile. |
| Shanghai active before Adventure in isolated execution | Coinbase warming, `PUSH0`, and initcode checks use Shanghai's predicate; this does not validate block production under that schedule. |
| Reference-client block preparation at simultaneous Shanghai/Adventure activation | Keep Istanbul preparation and nonzero difficulty; do not switch to post-merge block production. |
| Transient writes, nested reverts, static calls, and consecutive transactions | EIP-1153 ownership, rollback, write restrictions, gas, and transaction-scoped lifetime are preserved. |
| Overlapping and zero-length memory copies, with memory expansion | EIP-5656 results and gas agree with the upstream specification. |
| Same successful execution paid by sender or separate payer | Apply OIP-2 payment rules and the same fee recipient policy, without base fee burning. |
| Istanbul `PREVRANDAO` execution | Value agrees with the specified header-derived random value and the validated reveal path. |
| Genesis versus ordinary Adventure block | Preserve the genesis withdrawal-commitment exception; reject withdrawal fields or bodies in ordinary Adventure-only Istanbul blocks. |
| Replay across the activation boundary | Independent executions agree on state, receipts, logs, blooms, and block commitments. |

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Fork configuration and activation predicates](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Execution instruction sets](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go).
- [Istanbul header and consensus integration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).

Source observations and verification limits are recorded in the separate [verification record](../assets/oip-17/verification.md).

## Implementation and Activation

The reference client's default source configurations contain:

| Network | Chain ID | London block | Shanghai time | Adventure time |
| --- | --- | --- | --- | --- |
| ONEchain mainnet | `612055` | `0` | `0` | `0` |
| ZoneZero | `612044` | `0` | `0` | `0` |

These values satisfy the London, Shanghai, and Adventure activation predicates from genesis.
The table records only the activation parameters relevant to this profile.
The table records source defaults, not independently verified deployment dates, activation blocks, or currently running binaries.
Generated genesis files and custom network configurations must be checked separately.

This proposal schedules no new hardfork.
For any future activation or historical deployment record, maintainers must identify the network and genesis hash, authoritative chain configuration, activation decision, compatible client release, and boundary verification evidence.
Node operators, validators, RPC providers, wallets, and receipt consumers must coordinate any activation on a network where Adventure is not already active.
Historical network activation evidence, minimum compatible release identification, and the combined profile test results remain unverified in this proposal.

This proposal remains in Review because its required OIP-4 dependency has an unresolved reference-client validation gap.
Final registration requires OIP-4 to identify and verify the implementing revision and reach Final; the dependency list above is otherwise resolved.

## Security Considerations

Different timestamp predicates, partial opcode adoption, or inconsistent execution configuration can produce consensus divergence.
Fee collection must preserve the distinction between the transaction sender, fee payer, execution coinbase, and configured beneficiary.
Assuming Ethereum base fee burning would change balances and state commitments.

Istanbul-derived `PREVRANDAO` must not be treated as an unbiased Beacon randomness source without examining its own threat model.
Shanghai-compatible execution must not enable unintended Beacon withdrawal credits or bypass Istanbul header validation.
Native transfer logs affect receipt commitments, so they must follow OIP-3's activation and rollback rules.

Source configuration and a merged proposal are not evidence that a network has adopted a rule.
Changes to historical configuration require replay and compatibility checks before use with an existing chain database.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).

[eip1559]: https://eips.ethereum.org/EIPS/eip-1559
[eip3198]: https://eips.ethereum.org/EIPS/eip-3198
[eip3651]: https://eips.ethereum.org/EIPS/eip-3651
[eip3855]: https://eips.ethereum.org/EIPS/eip-3855
[eip3860]: https://eips.ethereum.org/EIPS/eip-3860
[eip1153]: https://eips.ethereum.org/EIPS/eip-1153
[eip5656]: https://eips.ethereum.org/EIPS/eip-5656
[eip4399]: https://eips.ethereum.org/EIPS/eip-4399
[eip4895]: https://eips.ethereum.org/EIPS/eip-4895
[eip7568]: https://eips.ethereum.org/EIPS/eip-7568
