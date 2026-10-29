---
oip: 24
title: PoSA Random Reveal
description: BLS random reveals, parent-mixed randomness, and the EVM random value for Istanbul PoSA.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 8, 23
---

# OIP-24: PoSA Random Reveal

## Abstract

This proposal describes the PoSA replacement for the ECDSA random reveal in [OIP-8](oip-8.md).
It specifies the signed payload, parent mixing, and the unchanged EVM hash mapping.
The digest prefix change from BreakpointBravo is specified in [OIP-35](oip-35.md).

## Motivation

The same PREVRANDAO opcode can expose values derived by different consensus profiles.
Implementers need the exact byte construction and fork selection to reproduce headers and contract execution.

## Specification

### Reveal Authorization

Use the activation and validator-key profile of [OIP-23](oip-23.md).
Construct the signed payload as `minimal_big_endian(blockNumber) || minimal_big_endian(chainID)`, without a separator or fixed-width padding.
A PoSA proposer signs that payload with its BLS key; the reveal is exactly 96 bytes.
The payload is signed directly, without prior hashing, under the ciphersuite of OIP-23.
Verify it against the authorized proposer's BLS public key in the snapshot used to validate the block.
Do not substitute an Ethereum Beacon RANDAO message, a block hash, or the ECDSA signature used before PoSA.

### Digest Construction

Let `r = keccak256(reveal)` and let `p` be the parent's 32-byte `mixDigest`.
For `i = 0..15`, set `tail[i] = p[16+i] XOR r[i]`.
The new digest is `prefix || tail`, where `prefix` is the 16 bytes `0x43726f737320497374616e62756c2e20` defined by OIP-8.
A non-PoSA block continues using the ECDSA reveal and unchained derivation of OIP-8.

The EVM value remains `keccak256(mixDigest)` over all 32 bytes.
The validator MUST recompute and compare the complete digest; recognizing the prefix alone is insufficient.

### Deterministic Construction Example

If the parent's tail is sixteen `0x11` bytes and the first sixteen bytes of the reveal hash are `0x22`, the new tail is sixteen `0x33` bytes.
This example checks only byte mixing; it is not a valid BLS signature vector.
The signed payload for block `1` and mainnet chain ID `612055` is `0x010956d7`.

## Rationale

Mixing the previous tail carries forward prior block input without changing the fixed prefix layout.
Preserving the original payload encoding is necessary for historical signature verification even though a new design could choose stronger explicit domain separation.

## Backwards Compatibility

PoSA does not reinterpret historical ECDSA reveals.
Applications must not infer Beacon-chain randomness guarantees from opcode compatibility.

## Test Cases

| Case | Expected result |
| --- | --- |
| Valid reveal under the proposer key and expected parent | Accept the recomputed digest. |
| Reveal signed by another council key | Reject. |
| Correct reveal with the wrong parent tail | Reject the digest. |
| First PoSA block | Mix the BLS reveal hash into the parent's ECDSA-derived tail. |
| Parent tail 0x11; reveal-hash prefix 0x22 | Produce tail 0x33 byte by byte. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Reveal payload, verification, and parent mixing](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Digest constants and helper](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go).
- [EVM random value](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go).
- [Existing mixing tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine_test.go).
- [Existing digest tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-24/verification.md).

## Implementation and Activation

BLS reveals and parent mixing follow PoSA activation.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Publish actual BLS reveal, digest, and PREVRANDAO vectors across the PoSA activation boundary.
- Confirm the key-registration assumptions of OIP-23 against the deployed contracts.

## Security Considerations

A proposer can influence participation and block publication; this construction is not an unbiased random oracle for applications.
The concatenated variable-length payload has no explicit length delimiter, so cross-network signing domains need careful analysis rather than assuming universal replay separation.
Reveals, commit seals, and key-registration proofs share one signing domain and are distinguished only by message content and length.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
