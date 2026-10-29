---
oip: 37
title: BreakpointBravo Hardfork
description: The BreakpointBravo profile of Istanbul digest version 2 and the optional system call omission check.
author: ONEchain Contributors
status: Draft
type: Meta
created: 2026-10-29
requires: 34, 35, 36
---

# OIP-37: BreakpointBravo Hardfork

## Abstract

This Meta proposal lists the BreakpointBravo changes present in the reference main-branch revision.
It includes Istanbul digest version 2 and the optional system call omission check.

## Motivation

A fork name can also appear on development branches carrying additional changes.
A reproducible profile must identify exactly which rules exist in its pinned implementation.

## Specification

### Activation and Included Rules

BreakpointBravo is active when London is active, `breakpointBravoTime` is configured, and the block timestamp reaches that value.
The mainnet and ZoneZero presets leave that timestamp unset; this Draft does not describe other source presets.
That fact does not establish how any independently configured or subsequently upgraded node is running.

This profile builds on the Breakpoint profile in [OIP-34](oip-34.md) and includes:

| Specification | Change |
| --- | --- |
| [OIP-35](oip-35.md) | Digest version 2 prefix and the commitment of epoch signer keys to header hashes. |
| [OIP-36](oip-36.md) | Rejection of an omitted slash or mitigation call that would succeed. |

The BreakpointBravo timestamp also enters the EIP-2124 fork identifier of [OIP-12](oip-12.md), and the blob schedule continues to use the Prague entry.
BreakpointBravo introduces no additional instruction table, precompile gas schedule, or contract-replacement registry entry in this revision.

### Revision Boundary

The pinned `IstanbulExtra` has no parent-commit certificate field.
Offline proposer selection still reads the parent's round under [OIP-26](oip-26.md).
Do not import a later parent-certificate, signer-filtering, or slashing change merely because another branch uses the same fork name.
Such additions require a separately identified implementation revision and a decision on compatibility before being included in this profile.

## Rationale

A narrow profile makes the source revision auditable and prevents branch-specific behavior from being presented as an already merged consensus rule.

## Backwards Compatibility

The included rules must not be applied retroactively to blocks before activation.
Adding a required certificate to an already used historical timestamp would need separate replay analysis.

## Test Cases

| Case | Expected result |
| --- | --- |
| Timestamp before BreakpointBravo | Apply neither included rule. |
| Timestamp at BreakpointBravo | Apply both OIP-35 and OIP-36. |
| Decode the pinned header format | Do not require an absent parent-certificate extension. |
| Independent clients replay the boundary | Agree on block hashes, random values, and accepted blocks. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [BreakpointBravo predicate and schedules](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Digest selection and omission check](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-37/verification.md).

## Implementation and Activation

No public activation time is assigned here.
Any future revision of this profile must identify its implementing commit and distinguish newly introduced rules from those in 4c0838f.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Run digest, signer-key, optional-call, and full-state replay tests at the exact intended activation boundary.
- Resolve which implementation revision is to be documented before adding any development-branch extensions.

## Security Considerations

Clients that adopt only one of the included rules split from the network at the activation boundary.
Operators must agree on the activation timestamp, since it changes block hashes, random values, and block validity.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
