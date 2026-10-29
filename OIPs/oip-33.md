---
oip: 33
title: Beacon Interface Adaptations for Istanbul
description: Withdrawals, parent beacon roots, and execution-request commitments without an Ethereum consensus layer.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 4, 5
---

# OIP-33: Beacon Interface Adaptations for Istanbul

## Abstract

This proposal records which Ethereum Beacon-related execution fields are retained, adapted, or excluded on Istanbul networks.
It covers Cancun and Prague integration without introducing Ethereum validator operations.

## Motivation

A header can retain an upstream field for encoding compatibility while its corresponding Beacon operation remains disabled.
Clients must verify the actual commitment and processing rules instead of equating fork names with full Beacon functionality.

## Specification

### Header and Body Profile

Use the Istanbul engine and header context of [OIP-4](oip-4.md) and [OIP-5](oip-5.md).
The reference profile is:

| Condition | Withdrawals | Parent beacon root | Requests hash |
| --- | --- | --- | --- |
| Ordinary block before Cancun | Commitment absent; body list absent. | Absent. | Absent before Prague. |
| Cancun active | Empty withdrawal commitment and matching empty body. | Present and equal to zero. | Governed separately by Prague. |
| Prague active | Retain Cancun requirements where Cancun is active. | Retain the Cancun zero-root rule. | Present; full execution checks it against the empty request result. |

Configurations MUST activate Cancun no later than Prague; the reference block producer sets the requests hash only when Cancun is active.
Genesis can contain the empty withdrawal commitment when Shanghai is active, as documented in [OIP-17](oip-17.md) and [OIP-18](oip-18.md).
That exception does not authorize withdrawal credits in ordinary blocks.

### Processing Adaptations

[EIP-4895](https://eips.ethereum.org/EIPS/eip-4895) supplies the upstream withdrawal field, but this profile does not process Beacon validator withdrawals.
[EIP-4788](https://eips.ethereum.org/EIPS/eip-4788) supplies the parent-root field; the zero-root Istanbul path skips its BeaconRoots EVM call.
Do not synthesize a nonzero Beacon root for a chain with no Beacon consensus layer.

The Prague processing branch for deposit, withdrawal, and consolidation requests explicitly excludes Istanbul chains.
Consequently [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110), [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002), and the consolidation path associated with [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251) are not activated as Beacon validator services here.
The [EIP-7685](https://eips.ethereum.org/EIPS/eip-7685) requests-hash field remains, with the hash of the empty request sequence verified by full block processing.
A non-null requests field alone does not prove its value is correct.

### Retained Independent Functionality

The parent execution-block history call remains enabled under Prague and is specified in [OIP-31](oip-31.md).
It is independent of Beacon root storage and validator request queues.
The reference Istanbul active-system-contract listing includes history storage but omits BeaconRoots and the Beacon request contracts.
This Draft does not assert that every possible call to an address is blocked; it specifies the automatic consensus processing and commitments.

## Rationale

Keeping field compatibility while explicitly disabling unsupported external-consensus operations allows execution upgrades without importing an absent trust source.

## Backwards Compatibility

Generic Ethereum tooling must not interpret empty withdrawals or request commitments as evidence of Beacon validator support.
The genesis and ordinary-block cases remain distinct, and custom fork schedules require all relevant predicates to be evaluated.

## Test Cases

| Case | Expected result |
| --- | --- |
| Ordinary pre-Cancun header with withdrawals commitment | Reject, independently of the Shanghai genesis exception. |
| Cancun header with nonzero parent beacon root | Reject through Istanbul header verification. |
| Cancun body with a nonempty withdrawal list | Reject against the required empty commitment. |
| Prague header with absent requests hash | Reject. |
| Prague configured without Cancun | Reject the configuration for this profile. |
| Prague header with a nonempty-request hash | Fail full execution commitment validation. |
| Prague Istanbul processing | Keep execution history storage while skipping Beacon request production. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Istanbul header field checks](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Processing gates and system calls](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_processor.go).
- [Body and execution commitment checks](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/block_validator.go).
- [Genesis withdrawal commitment](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/genesis.go).
- [Active system contracts](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Header construction](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-33/verification.md).

## Implementation and Activation

Cancun and Prague predicates govern the corresponding fields and processing gates.
These rules apply on every Istanbul import path; OIP-4 requires that Istanbul blocks are never verified or finalized under post-merge rules.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Verify nil versus empty body encodings, genesis exceptions, and empty request commitments across activation boundaries.
- Check these rules on every import and finalization path covered by OIP-4, not only in header verification.

## Security Considerations

Istanbul blocks rely on Istanbul seal verification; Beacon processing rules provide no validator authorization on these chains.
Header-only checks and full execution commitments provide different guarantees and must both be covered.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
