---
oip: 22
title: Stake-Based Validator Council Selection
description: Stake ranking, deterministic council selection, and validator epoch publication for Istanbul PoSA.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 19, 21
---

# OIP-22: Stake-Based Validator Council Selection

## Abstract

This proposal specifies how Istanbul PoSA derives its active council from StakeHub and publishes validator addresses and BLS keys at validator epochs.
It distinguishes council selection from peer eligibility.

## Motivation

Stake, registration, council membership, and the validator snapshot change at different points.
Clients need identical ranking and boundary rules to agree on which validators authorize a block.

## Specification

### Activation and State Inputs

PoSA is active only when the block number is at least `1`, London is active, Istanbul PoSA configuration exists, and the timestamp is at least `breakpointTime + 1`.
The Breakpoint installation boundary and the first PoSA block are therefore separate conditions.
Use the parent block state for `StakeHub.getValidators(0, 0)` and `maxCouncil()`.
The returned entries associate validator address, BLS signer key, voting power, and creation time.
The referenced StakeHub gives zero power to an inactive validator or one below the minimum stake.

### Council Algorithm

Reject an empty candidate result or a zero maximum council size.
Sort candidates by descending power, then ascending creation time, then ascending validator-address bytes.
Take at most `maxCouncil` entries and discard zero-power entries.
Reject an empty selected result.
Sort the selected entries by ascending validator address, preserving each address/key pairing.
On a council-period transition where both the parent and the block are PoSA blocks, submit that result through `ValidatorSet.updateValidators` using [OIP-19](oip-19.md).
Protocol contract installation is defined in [OIP-21](oip-21.md).

### Breakpoint Boundary

At the block where the Breakpoint predicate first holds, the validator snapshot replaces its validator set with the configured PoSA validators and BLS keys, or keeps its current list when none are configured.
The same block discards pending votes and tallies, and its header vote is not applied.
From the first PoSA block, header votes are no longer read, and the validator set changes only through epoch headers.
ValidatorSet holds the configured initial set from the [OIP-21](oip-21.md) initialization until the first council update.

### Periods and Epochs

A council-period transition occurs when `parentTime != 0` and `floor(parentTime / P) != floor(blockTime / P)`.
The reference fallback for a zero configured `P` is `86400` seconds.
A validator epoch occurs when `blockNumber mod E == 0`, with reference fallback `E = 300` blocks.
A council update changes the contract state during finalization; publishing a validator list in an epoch header changes the subsequent snapshot according to the consensus rules.
Non-epoch PoSA headers carry no validator-address or signer-key lists.

At an epoch, read the active ValidatorSet result from the parent state, validate matching address/key counts and 48-byte keys, and sort paired entries by address.
If the epoch is also a council-period transition and the parent is PoSA, compute the new council from parent StakeHub state instead of reading the old council from ValidatorSet.
Preparation and verification MUST use the same calculation.
If ValidatorSet has no code or returns no active validators at the parent state, the epoch header MUST publish the parent snapshot's validator addresses and signer keys unchanged.

Consensus keys are indexed by the byte-sorted validator list; a peer being eligible does not by itself give it a council vote.

## Rationale

A deterministic tie-break and stable address order keep selection and BLS bitsets consistent.
Precomputing at coincident boundaries prevents the header from publishing the council that is about to be replaced.

## Backwards Compatibility

Validator changes by header vote, specified in [OIP-6](oip-6.md), end at the Breakpoint boundary when PoSA is configured.
This Draft does not change how blocks before that boundary are validated and requires no new deployment.

## Test Cases

| Case | Expected result |
| --- | --- |
| Equal stake and different creation times | Select the older entry first. |
| Equal stake and creation time | Break the tie by ascending validator address. |
| Zero-power candidate or zero council size | Exclude zero-power entries; reject a zero size or empty selection. |
| Epoch coincides with council rollover | Prepare and verify the same recomputed council from parent state. |
| Non-epoch PoSA header carries a validator list | Reject under the PoSA header rules. |
| ValidatorSet returns no active validators at an epoch | Publish the parent snapshot's addresses and keys unchanged. |
| Breakpoint boundary block | Replace the snapshot with the configured PoSA validators and keys and discard pending votes. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

References to `to-nexus/cross-contracts` are [internal verification sources](../README.md#verification-sources) and require access to the cited repositories.

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Council computation and contract reads](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go).
- [Epoch header preparation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Snapshot replacement at the boundary and at epochs](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go).
- [Periods and defaults](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/config.go).
- [Existing council and coincident-boundary tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus_test.go).
- [StakeHub source recorded by the installation registry](https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-22/verification.md).

## Implementation and Activation

The baseline network PoSA presets specify a council period of 86400 seconds and validator epochs of 300 blocks.
Contract parameters such as maximum council size and minimum stake are read from state and must not be inferred from current source defaults for historical blocks.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Verify snapshot activation at every epoch and the first PoSA blocks with the installed contract bytecode.
- Record registration, jail, and rotation vectors, including malformed or mismatched returned arrays.

## Security Considerations

Selection from a different state height or a different tie-break changes block authority.
Address rotation, jail status, and BLS key registration must preserve the distinction between operator identity, consensus address, and signing key.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
