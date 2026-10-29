---
oip: 23
title: BLS Istanbul Consensus and Header Extensions
description: Aggregate BLS commit seals, signer bitsets, and epoch key commitments for Istanbul PoSA.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 5, 6, 7, 22
---

# OIP-23: BLS Istanbul Consensus and Header Extensions

## Abstract

This proposal replaces the committed-seal and extra-data rules of Istanbul consensus with BLS commit seals and validator signing keys when PoSA is active.
It records the original header-hash behavior; [OIP-35](oip-35.md) changes the signer-key commitment from BreakpointBravo.

## Motivation

Aggregated signatures reduce committed-seal size but require an unambiguous mapping from a bit to an authorized validator key.
Header encoding and hash filtering must preserve historical block identities.

## Specification

### Scope and Extra Data

Use the PoSA activation and council rules of [OIP-22](oip-22.md), the underlying quorum rules of [OIP-6](oip-6.md), and the message protocol of [OIP-7](oip-7.md).
The base header encoding is defined by [OIP-5](oip-5.md).
From PoSA activation, this proposal replaces the six-element rule and the `committedSeals` and `randomReveal` field definitions of OIP-5, and the individual-seal quorum certificate of OIP-6.
Blocks before PoSA activation remain governed by those proposals.
BLS public keys are 48-byte compressed values; signatures are 96-byte compressed values.
The PoSA extra-data extends the six base RLP elements with `signersBitset` and `signers` in that order.
The bitset is an RLP list of unsigned 64-bit words; bit `i` is the low-to-high bit at `i mod 64` of word `floor(i / 64)`.
`signers` is the ordered list of validator public keys at an epoch boundary.
An encoder emits both trailing elements when either is nonempty and omits both otherwise; when only `signers` is nonempty, `signersBitset` is encoded as the empty list `0xc0`.
A sealed PoSA header therefore has eight elements, and a seven-element list is invalid.
In a PoSA header, `randomReveal` is the 96-byte BLS reveal specified in [OIP-24](oip-24.md).
Headers before PoSA activation MUST have exactly the six elements of OIP-5; the reference decoder's acceptance of longer lists is recorded in the [OIP-5 verification record](../assets/oip-5/verification.md).

### Commit Verification

A PoSA committed header contains exactly one aggregate signature in `committedSeal`.
Decode its bitset against validators sorted by ascending address bytes from the authorizing snapshot, not against an unverified list in the incoming header.
Reconstruct the expected word list from recognized set bits and require exact equality; reject empty selections, unknown bits, and noncanonical excess words.
The selected distinct validator count MUST satisfy the inherited quorum threshold.
Verify the aggregate signature over the filtered header hash with the committed round using the selected BLS keys.
Reject malformed keys, malformed signatures, or unsuccessful aggregate verification.
Signatures use the BLS12-381 ciphersuite with domain separation tag `BLS_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_POP_`, with 48-byte G1 public keys and 96-byte G2 signatures.
The certificate is checked with same-message fast aggregate verification, which is secure only if every key in the authorizing snapshot has a verified proof of possession.
At non-epoch heights, both validator-address and signer-key lists MUST be empty.
Epoch validator addresses and signer keys MUST match the council computation in OIP-22.

The COMMIT message retains its sequence, round, digest, and seal payload and its outer ECDSA message signature.
Its inner commit seal uses BLS in the PoSA profile and is checked for the source validator before being counted.
Header assembly rejects duplicate signer indices before aggregating the inner seals.

### Hash Commitments

For the block hash, clear committed seals and signer bits and set the round to zero.
For the commit-signing hash, use the committed round instead.
With the original Istanbul digest prefix of OIP-24, clear signer keys as well, so the filtered extra-data has six elements.
Digest version 2 in OIP-35 retains signer keys instead.

The reference revision contains no parent-commit-certificate extra-data field.
This Draft does not import a certificate format from a later development branch.

## Rationale

The bitset keeps aggregate signers tied to snapshot authority.
Committed seals and signer bits stay outside the hash because they are assembled after the block content is fixed.

## Backwards Compatibility

Clients implementing only the six-element format of OIP-5 cannot validate PoSA headers.
The BLS reveal derivation is specified separately in OIP-24.

## Test Cases

| Case | Expected result |
| --- | --- |
| Quorum of distinct authorized signers | Accept a valid aggregate certificate. |
| Duplicate signer during aggregation | Reject. |
| Unknown bit or extra noncanonical word | Reject the bitset. |
| Correct signature from too few selected validators | Reject for insufficient quorum. |
| Sealed PoSA header with seven extra-data elements | Reject. |
| Original-prefix historical header | Exclude signer keys from the filtered hash. |
| BLS inner seal with an invalid outer message signature | Reject the consensus message. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Extra-data and hash filtering](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go).
- [Seal verification and assembly](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Commit messages](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/commit.go).
- [BLS backend](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/crypto/bls/bls.go).
- [Existing BLS seal and bitset tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-23/verification.md).

## Implementation and Activation

BLS commit verification is selected by `IsIstanbulPoSA`.
The cryptographic backend is the blst implementation pinned through Prysm v5.3.2.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Publish independent aggregate-signature vectors under this ciphersuite, including invalid-key cases.
- Run activation, council-rotation, message, and full-header verification tests against the same snapshot.

## Security Considerations

Rogue keys, duplicate keys, malformed encodings, and incorrect snapshot selection can undermine aggregate verification.
The referenced StakeHub requires, when a key is registered or updated, a signature by that key over a hash binding the operator, the key, and the chain ID, verified through [OIP-27](oip-27.md).
Keys supplied by network configuration are trusted by that configuration.
A valid aggregate over the wrong round or key list is not a valid block certificate.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
