---
oip: 8
title: Validator Random Reveal and PREVRANDAO
description: ECDSA validator reveals, Istanbul mix digest construction, and the EVM random value.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-8: Validator Random Reveal and PREVRANDAO

## Abstract

This proposal specifies the ECDSA random-reveal mechanism used by ONEchain's Istanbul validators and the value exposed through `PREVRANDAO`.
It records the signed message, header commitment, and adaptation of [EIP-4399](https://eips.ethereum.org/EIPS/eip-4399) to a chain without an Ethereum Beacon Chain.

## Motivation

Validators must agree on the bytes signed for a reveal and on the resulting header digest.
Applications must distinguish ONEchain's header-derived value from Ethereum's Beacon randomness.
The opcode name alone does not identify the entropy source, predictability, or proposer influence.

## Specification

### Scope and Notation

This specification applies to Istanbul consensus as described by [OIP-6](oip-6.md).
`K(x)` denotes Keccak-256, not standardized SHA3-256; `||` denotes byte concatenation.
`BE(x)` is the minimal unsigned big-endian encoding of a nonnegative integer, with no leading zero bytes; `BE(0)` is empty.
Byte slices use zero-based, end-exclusive offsets.

### Reveal Message and Signature

For block number `n` and execution chain ID `c`, construct:

```text
message = BE(n) || BE(c)
messageHash = K(message)
reveal = secp256k1_sign(messageHash, validatorPrivateKey)
```

`reveal` is a 65-byte recoverable ECDSA signature encoded as `r[32] || s[32] || recoveryId[1]`, with recovery ID `0` or `1`.
There is no RLP encoding, fixed-width integer padding, personal-message prefix, EIP-712 domain, parent digest, timestamp, or round in this signed message.
The reference signer emits canonical low-`s` signatures.
This statement about signature generation must not be confused with a separately verified low-`s` rejection rule in every recovery path.

The reveal is stored in the `randomReveal` field of the Istanbul header extra-data.
For a non-genesis block, recover the address from `messageHash` and `reveal`.
Recovery must succeed, the recovered address must equal the header's proposer address in `coinbase`, and that address must belong to the validator set used to authorize the block.
The block's quorum certificate and other header checks remain independently required.

### Header Mix Digest

Let `prefix` be the following 16 bytes, including its final ASCII space:

```text
prefix = 0x43726f737320497374616e62756c2e20
seed = K(reveal)
mixDigest = prefix || seed[0:16]
```

The 32-byte header `mixDigest` must equal this construction exactly.
Checking only the prefix is insufficient.
The construction does not combine the reveal with a parent random value.
Genesis has no proposer reveal to verify and retains its configured Istanbul digest.

### EVM Value

For an Istanbul execution context, the reference client sets:

```text
randomValue = K(header.mixDigest)
```

When the active instruction table defines `PREVRANDAO` at opcode `0x44`, the instruction pushes this value as a 256-bit word and charges the EIP-4399 instruction gas cost.
It returns neither the header difficulty nor `mixDigest` directly.
Adventure inherits this instruction through its Shanghai execution table.
The execution-fork and no-Merge integration is described by [OIP-4](oip-4.md).

The value concerns the executing block's header-derived reveal.
It must not be described as Ethereum's previous Beacon RANDAO mix or as requiring a Beacon Chain.

## Rationale

A recoverable signature associates the reveal with the authorized proposer without adding another public-key registry.
The fixed prefix identifies Istanbul headers, while the remaining 16 bytes bind the reveal hash.
Hashing the whole digest produces the EVM value without exposing the fixed prefix directly as its upper half.
It does not increase the underlying entropy or remove proposer influence.

The existing minimal-integer concatenation is preserved for compatibility.
Changing to fixed-width encoding, adding round or parent data, or adopting another signature format would change headers and requires a separate protocol revision.

## Backwards Compatibility

This proposal documents the existing random-reveal mechanism and activates no new randomness scheme.
Changing the signed message, truncation, prefix, or final hash changes both the header and contract-visible execution results.
Consumers relying on Ethereum's direct `mixHash` interpretation must use ONEchain's specified derivation instead.

## Test Cases

| Input or mutation | Expected result |
| --- | --- |
| `n = 1`, `c = 1` | Message bytes `0x0101`. |
| `n = 256`, `c = 1` | Message bytes `0x010001`; no fixed-width padding. |
| `(n, c) = (1, 258)` and `(257, 2)` | Both encode as `0x010102`; the encoding does not delimit the integers. |
| Valid proposer signature | Recover the header proposer and construct `prefix || K(reveal)[0:16]`. |
| Valid signature from another validator with unchanged `coinbase` | Reject the proposer mismatch. |
| Correct prefix with a modified digest suffix | Reject the mix-digest mismatch. |
| Same proposer, height, and chain ID with another round | Signed message is unchanged; round is not an input. |
| Valid Istanbul execution context | `PREVRANDAO` equals `K(mixDigest)`, not `mixDigest` or difficulty. |
| Genesis | Apply configured genesis rules without requiring a non-genesis reveal. |

Tests must additionally cover malformed signatures, changed height and chain ID, and unauthorized signers.
These are expected results; runtime signature and execution coverage is tracked separately.

## Reference Implementation

Reference implementation: [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Reveal generation and verification](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [ECDSA signing](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/backend.go).
- [EVM block context](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-8/verification.md).

## Implementation and Activation

[OIP-17](oip-17.md) includes this proposal as an inherited Istanbul rule.
No new activation is scheduled.
Its application to a network must be established from that network's historical consensus configuration.
Deployed activation history and cross-client agreement remain unverified by this proposal.

## Security Considerations

The proposer knows its own reveal before publishing the block and may withhold proposals or influence which proposer succeeds.
The message does not include a parent hash or round, and the digest retains only 128 bits of the reveal hash before the final hash.
Applications must not use this value alone as an unbiased or unpredictable draw for valuable outcomes.

Minimal-integer concatenation is ambiguous across some height/chain-ID pairs, as the test vector demonstrates.
The reveal must not be reused as a general-purpose, unambiguously domain-separated authorization signature.
Hashing and prefix checks do not replace proposer membership, signature recovery, or committed-seal verification.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
