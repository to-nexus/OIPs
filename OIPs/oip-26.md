---
oip: 26
title: Offline Validator Penalties and Mitigation
description: Offline proposer selection, penalty calls, jail integration, and periodic counter mitigation.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 19, 22, 23
---

# OIP-26: Offline Validator Penalties and Mitigation

## Abstract

This proposal records how the reference PoSA client derives offline proposer targets and invokes ValidatorSlash and StakeHub.
It covers the baseline round-based calculation.

## Motivation

Penalty targets must be deterministic, and a failed proposal round must not be confused with proof that a validator was disconnected.
Penalty counters, monetary slashing, jail, and peer eligibility have separate effects.

## Specification

### Client Target Selection

Use the system transactions of [OIP-19](oip-19.md), council rules of [OIP-22](oip-22.md), and BLS header profile of [OIP-23](oip-23.md).
While finalizing a PoSA child, examine its parent block's committed round.
For the baseline algorithm, only round-robin policy is supported; genesis cases, unavailable predecessor context, empty validator sets, or round zero produce no targets where the implementation explicitly returns an empty result.
Use the validator snapshot at the parent's predecessor, sorted by address, and that predecessor's author to calculate proposers for rounds `0` through `parentRound - 1`.
Deduplicate the resulting addresses and sort them by address before encoding `slashOffline(address[])`.
Do not penalize an address multiple times for repeated appearances in this target list.

The reference revision reads the round from the parent header itself.
It has no child-carried parent certificate or recent-parent-commit signer filter; such later changes are outside this Draft.
The relationship between this historical round field and certificate validation requires explicit boundary tests.

### Contract Counters and Penalties

The installation registry references ValidatorSlash and StakeHub at `5cbc608bd77ef186120308ec8219a016197efba2`.
ValidatorSlash skips an unregistered or rotated-away validator address.
An already penalized validator is skipped while inactive; when active again its penalized flag is cleared before further counting.
A validator is counted at most once per current block.
At the configured threshold, reset its offline count, invoke `StakeHub.penalizeOffline`, and set the penalized flag.
`slashOffline` does not catch a revert from `penalizeOffline`; such a revert, including StakeHub's refusal to jail its last active validator, reverts the whole call, so no target's counter changes in that block.
The initial threshold is `50`.

StakeHub checks the calling contract and current validator identity, requests a pool slash, deactivates the validator in ValidatorSet, and jails it with a release time set by the configured jail duration.
Jail does not end automatically: after the release time, the operator must call `unjail()` while meeting the minimum stake.
StakeHub returns without effect for a revoked or unregistered operator.
The referenced initialization values are `10000 * 10^18` wei for the requested slash and two days for jail duration.
These are mutable contract parameters, not claims about current deployed settings or guaranteed amounts recovered from a pool.

### Mitigation and Failure

At a council-period transition where both the parent and the block are PoSA blocks, after reward distribution and before council update, the client queries the slashed list at the parent state.
An empty result or a failed list query causes no mitigation call in the reference path.
Otherwise call `mitigate()`.
Subtract `floor(offlineSlashThreshold / mitigateRate)` from positive counters, saturating at zero and removing cleared records.
The initial mitigation divisor is `4`, giving a reduction of `12` with threshold `50`.

Slash and mitigation use OIP-19's optional-call semantics.
From BreakpointBravo, [OIP-36](oip-36.md) limits omission of these calls to calls that would fail.
A counter reduction is not itself an unjail operation or a promise of immediate council reentry.

## Rationale

Deterministic proposer reconstruction gives all clients the same contract input.
Separating counting from contract penalties preserves the historical behavior while making mutable policy and recovery conditions visible.

## Backwards Compatibility

This Draft preserves the baseline round source and does not retroactively apply later certificate formats.
Changing target selection, skipped calls, thresholds, or mitigation arithmetic can alter historical state and requires separate activation analysis.

## Test Cases

| Case | Expected result |
| --- | --- |
| Parent round zero | No offline target call. |
| One address appears in several missed rounds | Include it once in the sorted target array. |
| Counter 49 with threshold 50 | The next counted event invokes the configured penalty and resets the count, unless the penalty call reverts. |
| Penalty would jail the last active validator | The slash call reverts; no counter changes in that block. |
| Counter 20 with threshold 50 and divisor 4 | Mitigation leaves 8. |
| Counter 12 with the same settings | Mitigation removes the cleared counter record. |
| Rotated-away validator address | Skip the stale identity in the referenced contract. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

References to `to-nexus/cross-contracts` are [internal verification sources](../README.md#verification-sources) and require access to the cited repositories.

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Target selection, calls, and mitigation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go).
- [Optional-call finalization](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Existing penalty tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus_test.go).
- [Referenced ValidatorSlash](https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/ValidatorSlash.sol).
- [Referenced StakeHub](https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-26/verification.md).

## Implementation and Activation

Target calculation runs in the PoSA finalization path.
Historical contract state determines penalty policy.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Verify historical round authority and target computation against actual committed certificates and validator rotations.
- Pin the pool version and test slash amounts, jail/recovery behavior, mitigation, and reverted calls end to end.

## Security Considerations

A wrong parent round, snapshot, or proposer order can punish the wrong operator.
A missed round is an operational inference, not a cryptographic proof of misconduct.
Pool slash outcomes and jail recovery need separate verification from peer admission.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
