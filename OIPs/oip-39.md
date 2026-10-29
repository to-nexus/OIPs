---
oip: 39
title: Osaka Execution Profile
description: Osaka execution changes adopted on Istanbul chains and the upstream Osaka features they exclude.
author: ONEchain Contributors
status: Draft
type: Meta
created: 2026-10-29
requires: 27, 32, 34, 38
---

# OIP-39: Osaka Execution Profile

## Abstract

This Meta proposal lists the Osaka execution changes in the reference client for Istanbul chains.
It records the upstream changes adopted by reference, the ONEchain precompile kept in the Osaka map, and the upstream Osaka features that Istanbul chains exclude.

## Motivation

Importing upstream Osaka code does not imply adopting every associated feature on a chain without an Ethereum consensus layer.
Opcode availability, cryptographic call costs, input bounds, block size, and blob fees affect validity and historical replay, so the adopted set must be explicit.

## Specification

### Activation

Osaka is active when London is active, `osakaTime` is configured, and the block timestamp is at least that value.
The reference Istanbul rule builder permits it without a proof-of-stake transition.
In the reference fork order, Osaka follows Breakpoint and BreakpointBravo when those are configured.
The mainnet and ZoneZero presets leave `osakaTime` unset; this Draft does not describe other source presets.

### Included Changes

Upstream EIPs listed without a separate ONEchain proposal are adopted by reference, subject to this activation condition.

| Specification | Change | Reference behavior |
| --- | --- | --- |
| [EIP-7939](https://eips.ethereum.org/EIPS/eip-7939) | CLZ | Opcode `0x1e` returns the number of leading zero bits in a 256-bit word; zero returns 256. |
| [EIP-7823](https://eips.ethereum.org/EIPS/eip-7823) | MODEXP bounds | Each declared base, exponent, and modulus length is limited to 1024 bytes, even when the supplied data is shorter. |
| [EIP-7883](https://eips.ethereum.org/EIPS/eip-7883) | MODEXP pricing | The Osaka multiplication and iteration calculation, with a minimum cost of 500 gas. |
| [EIP-7951](https://eips.ethereum.org/EIPS/eip-7951) | P-256 verification | Address `0x100`, 6900 gas, and a 160-byte input `hash || r || s || publicKeyX || publicKeyY`. |
| [OIP-38](oip-38.md) | Transaction gas limit cap | `2^24` for ordinary transactions, with the system transaction exception. |
| [EIP-7934](https://eips.ethereum.org/EIPS/eip-7934) | Block size limit | An RLP-encoded block larger than 8,388,608 bytes is invalid. |

The Osaka instruction table inherits Prague and adds CLZ.
MODEXP remains at address `0x05`; its Osaka instance enables both the input bound and the new pricing.
A valid P-256 signature returns a 32-byte word equal to one; a wrong input length or failed verification returns empty data, and the gas cost applies regardless of validity.

### Precompile Map

The Osaka map inherits the earlier precompiles, adds P-256, and retains the [OIP-27](oip-27.md) `0xc0` BLS signature verifier at its existing gas schedule.
It includes `0xc0` even on a configuration without Breakpoint.
The reference selector gives the Osaka map precedence over the Breakpoint map when both predicates hold.
Transaction preparation MUST warm the same complete map that execution uses.

### Blob Schedule and Exclusions

The Osaka blob schedule default is a target of 6 blobs, a maximum of 9, and a base-fee update fraction of 5007716; BPO entries are configuration-dependent and are not activated here.
Istanbul chains do not adopt the [EIP-7918](https://eips.ethereum.org/EIPS/eip-7918) reserve-price adjustment: the reference disables it when Istanbul consensus is configured, and the excess formula of [OIP-32](oip-32.md) continues to apply.
Istanbul chains do not adopt [EIP-7594](https://eips.ethereum.org/EIPS/eip-7594) PeerDAS; the full sidecars of [OIP-10](oip-10.md) remain, with no custody, cell-sampling, or data-column protocol.
The reference transaction RPC paths and the block producer keep selecting sidecar version `0` after Osaka, while `eth_signTransaction`, unchanged from upstream, selects version `1`.

## Rationale

The Osaka changes share one activation condition but keep their upstream algorithms by reference.
Retaining `0xc0` avoids treating an upstream-only precompile map as ONEchain runtime behavior.
Listing the exclusions prevents inherited Ethereum helpers from being mistaken for enabled ONEchain services.

## Backwards Compatibility

The changes apply only from activation; historical execution keeps the earlier instruction tables, gas schedules, and blob fee formula.
MODEXP calls with oversized operands or older gas budgets, transactions above the gas cap, and blocks above the size limit can fail after activation.

## Test Cases

| Case | Expected result |
| --- | --- |
| CLZ inputs 0, 1, and 2^255 | Return 256, 255, and 0 respectively. |
| MODEXP declared operand length 1024 or 1025 | Allow the bounded input subject to other checks; reject the oversized one. |
| MODEXP call at the old gas budget | Apply the Osaka pricing. |
| Valid 160-byte P-256 input | Return a 32-byte one and charge 6900 gas. |
| Malformed P-256 input | Return empty data. |
| Osaka map selection | Keep `0xc0` active and warm alongside the upstream addresses. |
| Block whose RLP encoding exceeds 8,388,608 bytes | Reject. |
| Istanbul Osaka block with a high execution base fee | Do not apply the EIP-7918 reserve-price branch. |
| Istanbul blob transaction submission after Osaka | Select sidecar version 0. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Osaka predicate and fork order](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Instruction tables](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go).
- [CLZ definition](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/eips.go).
- [MODEXP, P-256, and precompile maps](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go).
- [Gas and size constants](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go).
- [Block size limit](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/block_validator.go).
- [Blob schedule and EIP-7918 exclusion](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go).
- [Sidecar version selection](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-39/verification.md).

## Implementation and Activation

No public network preset activates this profile, and this Draft proposes no activation time.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Run upstream CLZ, MODEXP, P-256, and block-size vectors on both sides of activation.
- Verify the full active and warm address set and the `0xc0` pricing in the Osaka map.
- Run blob fee and sidecar-version cases under an Istanbul configuration with Osaka active.

## Security Considerations

Incorrect operand bounds or gas pricing can expose denial-of-service costs.
Signature callers must validate return length and value and must not confuse empty output with a successful verification.
Accidentally enabling the excluded blob fee branch changes header validity and can split clients.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
