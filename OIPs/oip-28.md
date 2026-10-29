---
oip: 28
title: Validator Peer Admission
description: Istanbul peer eligibility, static and trusted exceptions, and connected-peer revalidation.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Networking
created: 2026-10-29
requires: 12, 22
---

# OIP-28: Validator Peer Admission

## Abstract

This proposal documents the reference Istanbul node's peer admission policy.
It distinguishes consensus snapshot membership from StakeHub eligibility and local connection exceptions.

## Motivation

Operators need predictable connectivity during sync, validator rotation, and stake changes.
A council rule alone does not describe which peers a validator node accepts.

## Specification

### Identity and Eligibility

Use the authenticated devp2p node identity to derive its nodekey address; the reference checker takes the last 20 bytes of the node ID.
Check membership in the consensus snapshot at the local chain head first.
A snapshot member is eligible even if its operator has already rotated to another address, because the old member can remain responsible until the next snapshot update.

For nonmembers after PoSA activation, StakeHub eligibility requires all of:

- A nonzero operator for the validator address.
- That operator's current validator address equals the queried address.
- The operator is not blacklisted.
- Its staked amount is at least `minValidatorStake`.

Before PoSA, snapshot membership supplies eligibility; do not apply the later contract rule to earlier blocks.
The council-selection process is specified in [OIP-22](oip-22.md).
Jail, revocation, and active-council membership are not additional checks in the nonmember peer-eligibility predicate.

### Admission Decision

| Local or peer condition | Decision |
| --- | --- |
| Outbound connection dialed as a static peer, or a trusted peer | Allow before eligibility lookups. |
| Permission checker absent | Allow. |
| Local node is not an eligible validator | Allow. |
| Local eligibility lookup fails | Allow; the node may be syncing without usable local state. |
| Local node is eligible; peer is eligible | Allow. |
| Local node is eligible; peer is ineligible or its lookup fails | Reject. |

An inbound connection from a node listed as static is checked like any other peer unless the node is also trusted.
Configured bootnodes do not receive an eligibility exemption; the reference omits the handshake rejection log for them but disconnects them during revalidation like other peers.
Apply the decision before the [OIP-12](oip-12.md) status exchange and when re-evaluating connected peers; a rejected peer exchanges no status message.
An admission decision grants connectivity, not a consensus vote or transaction validity exception.

### Reference Timing

The reference sweeps connected peers every 30 seconds with up to eight concurrent checks.
It caches both positive and negative per-address eligibility for one minute and the minimum stake for ten minutes.
These timings are implementation policy, not block-validity rules or a guaranteed disconnection deadline.
Cached eligibility can lag a stake, blacklist, or rotation change.

## Rationale

Snapshot membership keeps currently responsible validators connected through rotation.
Failing open for unknown local status allows synchronization, while a known validator rejects a peer whose eligibility cannot be established.

## Backwards Compatibility

This changes no wire message encoding or consensus validity rule.
Static/trusted configuration remains an operator choice and can admit nodes that would otherwise fail eligibility.

## Test Cases

| Case | Expected result |
| --- | --- |
| Snapshot validator with a rotated operator address | Allow until it ceases to be a snapshot member. |
| Static nonvalidator peer dialed by the local node | Allow. |
| Inbound connection from a static-listed nonvalidator | Check eligibility as for another peer. |
| Unknown local eligibility during sync | Allow. |
| Eligible local node; peer lookup error | Reject that peer. |
| Bootnode without eligibility or an explicit exception | Reject as for another peer. |
| Stake changes while cached | Apply the documented cache behavior, then re-evaluate and disconnect if required. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Admission decision and handshake](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/permission.go).
- [Admission before the status exchange](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/handshake.go).
- [Periodic revalidation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/handler.go).
- [Snapshot-first eligibility](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/backend.go).
- [StakeHub lookups and caches](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go).
- [Existing admission tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/permission_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-28/verification.md).

## Implementation and Activation

The handler enables this policy for an Istanbul engine exposing validator eligibility.
The current head and PoSA predicate determine which eligibility source applies; this Draft does not schedule a network activation.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Verify identity derivation, rotation, sync-time lookup failures, and cache expiry with actual peers.
- Test that disconnected ineligible peers cannot regain permission solely by redialing.

## Security Considerations

Trusted/static exceptions and local-status lookup failures broaden connectivity.
Eligibility must be derived from authenticated identities, and cache staleness must not be confused with consensus authority.
Connection filtering does not replace message signature or block verification.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
