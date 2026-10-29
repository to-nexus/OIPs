---
oip: 35
title: Istanbul Digest V2
description: The BreakpointBravo mix-digest prefix and the commitment of epoch signer keys to Istanbul header hashes.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 8, 23, 24
---

# OIP-35: Istanbul Digest V2

## Abstract

This proposal specifies digest version 2 for Istanbul blocks from BreakpointBravo.
It changes the fixed prefix of `mixDigest` and keeps epoch BLS signer keys in the filtered header used for the block hash and the commit-signing hash.

## Motivation

Digest version 2 makes epoch signer keys part of block identity.
A distinct prefix lets clients select the hashing rule from the header itself without redefining historical block hashes.

## Specification

### Activation

Digest version 2 applies to a block when London is active, `breakpointBravoTime` is configured, and the block timestamp is at least that value.
The genesis block keeps the original prefix even when BreakpointBravo is active from genesis.
The predicate is independent of PoSA activation, so it also applies to Istanbul blocks that use the ECDSA reveal of [OIP-8](oip-8.md).

### Mix Digest Prefix

From activation, the 16-byte prefix of `mixDigest` is `0x43726f737320497374616e62756c2e32` (`Cross Istanbul.2`).
It replaces the prefix `0x43726f737320497374616e62756c2e20` (`Cross Istanbul. `) defined by OIP-8 and used by [OIP-24](oip-24.md).
The prefix is selected by the predicate of the block being built or validated.
The 16-byte tail is derived unchanged: by OIP-24 for PoSA blocks and by OIP-8 otherwise.
The EVM value remains `keccak256(mixDigest)` over all 32 bytes, so the prefix change also changes `PREVRANDAO`.
A validator MUST recompute and compare the complete digest; recognizing either prefix alone is insufficient.

### Signer-Key Commitment

When a header's validated `mixDigest` carries the version 2 prefix, the filtered header defined in [OIP-23](oip-23.md) retains `signers`.
With the original prefix, the filtered header clears `signers` as specified by OIP-23.
Committed seals and `signersBitset` remain cleared in both versions; the block hash sets the round to zero, and the commit-signing hash uses the committed round.
With retained keys, the filtered extra-data has eight elements and `signersBitset` is encoded as the empty list `0xc0`; otherwise it has six elements.

### Revision Boundary

The pinned `IstanbulExtra` has no parent-commit certificate field.
This proposal does not include certificate, signer-filtering, or slashing changes found on later development branches.

## Rationale

Selecting the hashing rule from the validated prefix keeps each header self-describing and leaves earlier block hashes unchanged.
Committed seals and the signer bitset stay outside the hash because they are assembled after the block content is fixed.

## Backwards Compatibility

Blocks before activation keep the original prefix and hash filtering.
Re-encoding an original-prefix header with version 2 filtering changes its identity.
From activation, block hashes and `PREVRANDAO` values differ from those computed under the original prefix.
The BreakpointBravo timestamp also enters the EIP-2124 fork identifier of [OIP-12](oip-12.md).

## Test Cases

| Case | Expected result |
| --- | --- |
| Timestamp immediately before and at BreakpointBravo | Select the original and version 2 prefix respectively. |
| Genesis with BreakpointBravo active from genesis | Keep the original prefix. |
| Non-PoSA block after BreakpointBravo | Keep the OIP-8 reveal derivation with the version 2 prefix. |
| Change an epoch signer key under the version 2 prefix | Change the filtered block hash. |
| Original-prefix historical header | Exclude signer keys from the filtered hash. |
| Version 2 epoch header with signer keys | Encode eight filtered elements with `signersBitset` as `0xc0`. |
| Correct prefix with a modified tail | Reject the mix-digest mismatch. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Digest prefixes and filtered-header hashing](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go).
- [Digest selection, genesis prefix, and validation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [BreakpointBravo predicate](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Existing digest tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-35/verification.md).

## Implementation and Activation

Digest version 2 follows `IsBreakpointBravo`.
The mainnet and ZoneZero presets leave `breakpointBravoTime` unset, and this Draft proposes no activation time.
Activation is coordinated through the BreakpointBravo profile in [OIP-37](oip-37.md).

Before advancing beyond Draft:

- Publish digest, filtered-header hash, and `PREVRANDAO` vectors on both sides of the activation boundary, for PoSA and non-PoSA blocks.
- Run full-header verification and replay tests at the intended activation boundary.

## Security Considerations

Clients that disagree on the activation timestamp compute different block hashes and random values and therefore split.
The prefix change does not alter the bias properties of the random value described in OIP-8 and OIP-24.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
