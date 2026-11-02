---
oip: 4
title: Istanbul Chains Without the Merge Transition
description: Execution upgrades after Paris on Istanbul consensus chains that never transition to proof of stake.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-4: Istanbul Chains Without the Merge Transition

## Abstract

This proposal specifies how ONEchain networks that use Istanbul consensus adopt Ethereum execution upgrades scheduled after Paris without the proof-of-stake transition of [EIP-3675](https://eips.ethereum.org/EIPS/eip-3675).
Every header keeps a difficulty of one and is validated only by Istanbul consensus rules, and the configured terminal total difficulty is never reached.
Shanghai and later execution upgrades activate by block number and timestamp alone, and the EVM treats each block as post-merge when selecting instruction semantics.
It also records how the reference client keeps block production on Istanbul rules after Shanghai through its Adventure activation.

## Motivation

On Ethereum, Shanghai and later execution upgrades followed the transition to proof of stake.
Upstream execution clients therefore associate these upgrades with post-merge behavior: zero-difficulty headers, block authorization supplied by an external consensus layer, and the header rules of EIP-3675.

ONEchain finalizes blocks with Istanbul Byzantine fault tolerant consensus inside the execution client and has no beacon chain.
It adopts post-merge execution features while retaining Istanbul headers and validator seals.
Clients must agree on which header rules apply, how upgrade activation is evaluated without the transition, and how total difficulty and the terminal total difficulty are interpreted.
A client that follows upstream defaults could produce proof-of-stake headers that Istanbul validators reject, accept headers that no validator sealed, or leave post-merge upgrades inactive.

The behavior of individual consensus-layer features, such as withdrawals, beacon block roots, execution-layer requests, and blob data, is defined with the upgrade that activates each feature and is outside this proposal.

## Specification

### Conventions and Scope

An *Istanbul chain* is a network whose chain configuration contains an `istanbul` consensus section.
`TD(B)` denotes the total difficulty of block `B`: the sum of header difficulties from genesis through `B`.
`TTD` denotes the configured `terminalTotalDifficulty`.
*Post-merge header rules* are the requirements that EIP-3675 applies to proof-of-stake headers, including zero difficulty, a zero nonce, and an empty ommers list.

The rules in this proposal apply to every block of an Istanbul chain, including genesis.
Istanbul header contents, seals, validator selection, and the derivation of `mixDigest` are defined by Istanbul consensus and are outside this proposal.
Peer-to-peer block propagation and synchronization by total difficulty are also outside its scope.

### No Proof-of-Stake Transition

An Istanbul chain MUST NOT perform the transition defined by EIP-3675.
No block is a terminal proof-of-work block, and no block is a proof-of-stake block.
Block validity, finality, and the canonical chain are determined by Istanbul consensus without input from an external consensus layer.

Every header MUST have a difficulty of exactly `1`.
A header with any other difficulty, including `0`, is invalid.
Consequently, `TD(B) = number(B) + 1` for every block `B`.

The chain configuration MUST define `TTD`, and its value MUST exceed the total difficulty of any block the network can produce.
The reference presets use `TTD = 2^63 - 1 = 9223372036854775807`, which only a block numbered `2^63 - 2` or higher would reach.
`TTD` exists for compatibility with client configuration checks and has no effect on block validity.

### Header Validation

Clients MUST validate every header of an Istanbul chain with Istanbul consensus rules, regardless of which execution upgrades are active.
They MUST NOT apply post-merge header rules as an alternative validation path.
In particular, a header's difficulty, timestamp, or total difficulty MUST NOT cause it to be validated as a proof-of-stake header.

This requirement covers every path by which a client accepts headers or blocks, including block announcements, header and body synchronization, and direct chain insertion.
Clients MUST also finalize every block with Istanbul consensus rules and MUST NOT apply post-merge block finalization.
Header fields introduced by execution upgrades, such as the base fee, withdrawals root, blob gas fields, parent beacon block root, and requests hash, follow the rules that the corresponding upgrade defines for Istanbul chains.

### Upgrade Activation

On an Istanbul chain, an execution upgrade scheduled by timestamp is active at a block exactly when its block-number and timestamp conditions are met.
Post-merge status is not an additional prerequisite.

For example, Shanghai is active at block number `n` with timestamp `t` exactly when London is active at `n`, `shanghaiTime` is configured, and `t >= shanghaiTime`.
The same rule applies to Cancun, Prague, Osaka, and later timestamp-scheduled upgrades whose rules upstream clients condition on post-merge state.
An unset activation time disables the corresponding upgrade.

### Execution Context

The EVM MUST treat every block of an Istanbul chain as post-merge when selecting instruction semantics.
Opcode `0x44` therefore behaves as `PREVRANDAO` from [EIP-4399](https://eips.ethereum.org/EIPS/eip-4399) and does not return the header difficulty.

The value returned by `PREVRANDAO` is `keccak256(mixDigest)`, computed over the 32-byte `mixDigest` field of the executing block's header.
This differs from EIP-4399, where the value is the `mixHash` field itself.
How Istanbul consensus fills `mixDigest` is outside this proposal.

### Block Production

A block producer on an Istanbul chain MUST construct headers with a difficulty of `1` and the fields required by Istanbul consensus.
It MUST NOT construct headers under post-merge header rules, whichever execution upgrades are active.

For the reference-client profile documented here, Shanghai and Adventure activate at the same timestamp.
Alternative activation schedules are outside this profile.

## Rationale

A constant nonzero difficulty keeps Istanbul headers distinct from proof-of-stake headers in upstream code, which identifies the latter by zero difficulty.
It also keeps total difficulty increasing by one per block, so existing total-difficulty fields in headers and peer messages remain well defined.
Total difficulty is not a measure of work or security on an Istanbul chain; Istanbul finality determines the canonical chain.

Upstream clients refuse to start a network whose configuration omits `TTD`.
Setting `TTD` to a value the chain cannot reach satisfies that check without modifying it and keeps inactive the code paths that wait for a consensus layer after `TTD`.

Using the presence of Istanbul consensus in place of the post-merge prerequisite keeps upstream fork scheduling by timestamp.
Marking Istanbul blocks as post-merge throughout the client would instead also select upstream proof-of-stake behavior for header validation, sealing, and block propagation.

Returning `mixDigest` directly from `PREVRANDAO` would expose the fixed 16-byte Istanbul prefix as half of the value.
Hashing the field gives contracts a 32-byte value without that constant portion.

The reference client ties its block-production rule to Adventure activation, as described in [Implementation and Activation](#implementation-and-activation).
This proposal records that integration and its simultaneous Shanghai/Adventure activation constraint.

## Backwards Compatibility

This proposal records the consensus behavior of existing ONEchain networks and changes no finalized block, transaction, or receipt.
Every block finalized by Istanbul consensus already has a difficulty of `1`, because validators apply Istanbul header validation before committing a block.
Rejecting zero-difficulty headers on every import path therefore invalidates no block on these chains and requires no fork.
The reference presets for ONEchain mainnet (`612055`) and ZoneZero (`612044`) use a genesis difficulty of `1` and `TTD = 2^63 - 1`.

Tools written for Ethereum after the transition may assume zero difficulty, a `PREVRANDAO` value equal to `mixHash`, or a total difficulty that stopped increasing at the transition.
On Istanbul chains, difficulty is `1`, `PREVRANDAO` differs from `mixDigest`, and total difficulty continues to increase.

Changing `TTD` to a reachable value, introducing a proof-of-stake transition, or removing the Istanbul configuration would change consensus behavior and requires a separate proposal.

## Test Cases

Unless stated otherwise, the chain is an Istanbul chain with London, Shanghai, and Adventure active from genesis and `TTD = 2^63 - 1`.

| Case | Expected result |
| --- | --- |
| Header with difficulty `1` that satisfies Istanbul consensus rules | Valid with respect to this proposal. |
| Header with difficulty `0`, received by announcement, synchronization, or direct insertion | Invalid; not executed or stored as part of the chain. |
| Header with difficulty `2` | Invalid. |
| Genesis with difficulty `1`; block number `n` | `TD = n + 1`. |
| `shanghaiTime = 0` without a proof-of-stake transition | Shanghai rules, including `PUSH0`, apply from genesis. |
| `cancunTime` unset | Cancun rules do not apply at any timestamp. |
| Block production at a timestamp where Shanghai is active | A header with difficulty `1` and Istanbul fields is produced. |

The following vector checks only the `PREVRANDAO` derivation.
Its first 16 bytes are the ASCII prefix `Cross Istanbul. ` used by Istanbul headers, and the remaining bytes are arbitrary.

```text
mixDigest  = 0x43726f737320497374616e62756c2e200123456789abcdef0123456789abcdef
PREVRANDAO = 0x8a0657ff121883007437d73266604532ec282b3434f6719c66eb914f8ed66fff
```

Reproducible client tests for these cases remain pending.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Merge status, upgrade rules, and network presets](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Istanbul header validation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Merge-aware engine wrapper](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/beacon/consensus.go).
- [Consensus engine construction](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/ethconfig/config.go).
- [Block context and `PREVRANDAO` value](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-4/verification.md).

## Implementation and Activation

The reference client wraps the Istanbul engine in the upstream merge-aware engine.
That wrapper switches block preparation, difficulty calculation, and sealing to proof-of-stake behavior when the configuration reports post-merge state, which upstream derives from `shanghaiTime`, `mergeNetsplitBlock`, or a zero `TTD`.
The reference client reports pre-merge state whenever Adventure is active, so the Istanbul engine continues to prepare and seal blocks after Shanghai.
Without Adventure, the reference client would stop producing Istanbul blocks once Shanghai activates.

Networks running the reference client therefore need Adventure active no later than Shanghai.
Because the client's fork-order check also requires Adventure not to precede Shanghai, the two activation times are equal in practice.
The reference presets set both `shanghaiTime` and `adventureTime` to `0`.

The other rules do not depend on Adventure.
Istanbul header validation requires a difficulty of `1` for every block, including genesis.
Upgrade activation uses the presence of Istanbul consensus in place of post-merge status.
The EVM treats a block with difficulty `1` as post-merge because its block context carries the `PREVRANDAO` value.

Applying Istanbul validation and finalization on every import path, as required by [Header Validation](#header-validation), is a client conformance requirement rather than a consensus change.
This proposal is intended for Final registration under [OIP-1's retrospective path](oip-1.md#documenting-existing-deployed-behavior).
That registration requires a merged implementing revision to be referenced and its header verification, block import, and finalization paths to be verified against this requirement.

This specification records existing behavior and schedules no new fork.
The reference source settings do not establish the activation history of deployed networks.

## Security Considerations

Upstream merge-aware engines validate proof-of-stake headers without proposer or validator seal checks, because an external consensus layer is trusted to have authorized them.
An Istanbul chain has no such layer.
A client that validates any header under post-merge rules could accept a block that no validator sealed and that bypassed Istanbul block finalization.
Clients must reject headers whose difficulty is not `1` on every import path before executing or storing them, and implementations reusing upstream merge-aware components should test each path.

If `TTD` were reachable, upstream code would stop sealing new blocks and reject synchronized headers past `TTD`, waiting for a consensus layer that does not exist.
The network would halt, so configuration changes affecting `TTD` need the same review as consensus changes.

Total difficulty equals the block number plus one and is easy to claim.
Clients must not treat a higher advertised total difficulty as evidence that a chain is valid or final.

`PREVRANDAO` on Istanbul chains comes from Istanbul consensus rather than a beacon chain RANDAO.
Contracts must not assume beacon chain properties; the value's unpredictability and bias resistance depend on how Istanbul consensus derives `mixDigest`.

## References

- [EIP-650: Istanbul Byzantine Fault Tolerance](https://eips.ethereum.org/EIPS/eip-650).
- [EIP-3675: Upgrade consensus to Proof-of-Stake](https://eips.ethereum.org/EIPS/eip-3675).
- [EIP-4399: Supplant DIFFICULTY opcode with PREVRANDAO](https://eips.ethereum.org/EIPS/eip-4399).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
