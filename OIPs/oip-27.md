---
oip: 27
title: BLS Signature Verification Precompile
description: The ONEchain 0xc0 compressed BLS signature verification interface and gas schedule.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
---

# OIP-27: BLS Signature Verification Precompile

## Abstract

This proposal specifies the ONEchain-specific precompile at address `0x00000000000000000000000000000000000000c0`.
It verifies a single or aggregate BLS signature using compressed keys and is distinct from the EIP-2537 operation precompiles.

## Motivation

Contracts must know the exact byte layout, output length, failure mode, and active gas schedule.
Treating this precompile as a Solidity ABI boolean or as an EIP-2537 pairing call gives incompatible results.

## Specification

### Availability and Input

The reference Breakpoint precompile map adds `0xc0` to the Prague precompiles; [OIP-39](oip-39.md) specifies its retention in the Osaka map.
Availability follows the selected EVM precompile map, not merely the presence of a PoSA council.
The ordinary Prague map does not include this ONEchain extension.
Transaction preparation MUST warm the complete selected map, including `0xc0`.

```text
input = message[32] || signature[96] || publicKey[48] * N
N >= 1
```

There is no ABI selector, dynamic-array offset, length word, or implicit message hashing before the supplied 32 bytes reach the BLS verifier.
Reject inputs of at most 128 bytes or whose remaining length is not a multiple of 48.
Deserialize keys and signature through the reference BLS backend.
For one key, run signature verification over the 32-byte message.
For multiple keys, use same-message fast aggregate verification.

### Output and Failure

| Outcome | Returned data | Call outcome |
| --- | --- | --- |
| Valid signature | `0x01` | Success. |
| Well-formed but nonmatching signature | Empty bytes | Success. |
| Invalid input length, undecodable signature, or undecodable key | No successful result | Precompile execution error. |

The result is not a 32-byte ABI-encoded boolean.
A caller MUST check call success, returned length, and returned bytes; an absent precompile can also return empty data.

### Gas and Authorization

For structurally sized input, required gas is `1000 + 3500 * N`.
Malformed length has a required gas of `1000`.
As for other precompiles, an execution error consumes all gas supplied to the call, not only the required gas.

Verification does not establish that supplied keys belong to validators, are distinct, or have proven possession.
The reference call itself does not query council membership or deduplicate keys.
Applications requiring aggregate authorization MUST establish those conditions in their own registration and verification protocol.
The EIP-2537 curve-operation precompiles, adopted by reference in [OIP-34](oip-34.md), use uncompressed field and point encodings rather than this compressed layout.

## Rationale

A fixed packed layout avoids decoding overhead, while explicit result lengths preserve the existing interface.
Keeping authorization separate prevents a cryptographically valid signature from being mistaken for validator approval.

## Backwards Compatibility

This Draft preserves the baseline address and gas schedule.
Changing pricing, return encoding, key policy, or activation would change contract behavior and is not authorized here.

## Test Cases

| Case | Expected result |
| --- | --- |
| Valid single-key input, length 176 | Required gas 4500; successful verification returns one byte 0x01. |
| Valid two-key input, length 224 | Required gas 8000; apply aggregate verification. |
| Input length 128 or 177 | Required gas 1000; the call fails and consumes all supplied gas. |
| Well-formed signature for another message | Successful call with empty output. |
| Malformed compressed key | Precompile execution error consuming all supplied gas. |
| Call before an applicable precompile map is active | Do not interpret empty return data as a verified signature. |
| Breakpoint transaction preparation | Warm `0xc0` together with the Prague precompiles. |
| Prague map without Breakpoint | Do not expose `0xc0`. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Precompile maps and implementation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go).
- [Gas constants](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go).
- [Compressed BLS backend](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/crypto/bls/bls.go).
- [Single-key vector](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/testdata/precompiles/blsSignatureVerification.json); the [precompile test harness](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts_test.go) does not currently run it.

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-27/verification.md).

## Implementation and Activation

Breakpoint map selection is the source-defined activation condition.
This Draft does not infer a deployed activation timestamp from them.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Run the existing vector through the precompile test harness.
- Add independent single-key and aggregate vectors under the ciphersuite of [OIP-23](oip-23.md).
- Test malformed, infinity, subgroup, duplicate-key, insufficient-gas, and inactive-address behavior.

## Security Considerations

Fast aggregate verification requires trusted key provenance and appropriate proof-of-possession protections.
Duplicate or attacker-selected keys must not be counted as independent voting authority.
Incorrect empty-return handling can turn verification failure into an authorization success.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
