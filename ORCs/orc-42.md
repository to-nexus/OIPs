---
orc: 42
title: Signed Token Approvals
description: Explicit permit profiles for EOA and smart-account token owners on ONEchain.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 20, 40
---

# ORC-42: Signed Token Approvals

## Abstract

This proposal extends [ORC-20](orc-20.md) with explicitly identified signed-approval profiles.
It distinguishes [ERC-2612](https://eips.ethereum.org/EIPS/eip-2612) from [ERC-7597](https://eips.ethereum.org/EIPS/eip-7597), and defines the integration checks needed by ONEchain wallets and token paymasters.

## Motivation

A token exposing one permit selector cannot automatically accept another selector or a smart-account signature.
Wallets need to discover the supported profile before requesting approval, and users need to see the exact spending authority being granted.

## Specification

### Profiles and Compatibility

Conforming tokens MUST satisfy ORC-20 and declare which of the following profiles they implement.
Unchanged behavior is adopted from the referenced ERC; this Draft does not redefine its selectors.

| Profile | Signature arguments | Intended owner support |
| --- | --- | --- |
| ERC-2612 | `uint8 v, bytes32 r, bytes32 s` | EOA verification defined by that ERC. |
| ERC-7597 | `bytes signature` | EOA and [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) contract verification. |

At least one profile MUST be identified; supporting both is optional.
A deployment advertising smart-account permits MUST implement the byte-signature profile and actually invoke the owner's contract verification path.
Both overloads MUST use and increment the same `nonces(owner)` value, as ERC-7597 requires, so a signed approval cannot be applied twice through different selectors.
ERC-7597 was Draft when consulted; deployments MUST pin the adopted revision.

### Signed Authority

The signed approval binds owner, spender, raw token amount, current owner nonce, and deadline through the token's [EIP-712](https://eips.ethereum.org/EIPS/eip-712) domain.
Conforming tokens MUST include `chainId` and `verifyingContract` in that domain and MUST expose it through [ERC-5267](https://eips.ethereum.org/EIPS/eip-5267) `eip712Domain()`.
Applications MUST rebuild the domain separator from those fields, compare it with `DOMAIN_SEPARATOR()`, and verify the owner and trusted spender before signing.
Wallets MUST display the amount that will actually be signed; an estimated gas charge is not the approved allowance.
An expired, invalid, or consumed approval MUST revert without changing the allowance or nonce.
Permit execution changes an allowance; it does not transfer tokens, reserve payment capacity, or provide native gas.

### OneAccount Signature Routing

For the byte-signature profile, smart-account owners MUST use the message-signature envelope of [ORC-40](orc-40.md).
The account verifies the token's typed-data digest, and integrations MUST NOT add a personal-message prefix.
A defensive-rehash profile such as [ERC-7739](https://eips.ethereum.org/EIPS/eip-7739) MAY be used when both the account and the verifier support it, as described in ORC-40.
Validator signatures can have different lengths; the complete envelope MUST NOT be restricted to 65 bytes.
For an owner with an EIP-7702 delegation, ERC-2612 verification recovers the EOA key, whereas an ERC-7597 verifier that dispatches on code size calls the account's ERC-1271 path.
Applications MUST NOT assume that a signature valid under one profile is valid under the other for such an owner.
Deploying or initializing an account before verification remains a separate requirement; this baseline does not include counterfactual verification.

### Discovery and Fallback

Wallets MUST select the overload from a published deployment profile that names the token, chain, supported permit profiles, and EIP-712 domain, or from a verified ABI and tested behavior.
There is no new ERC-165 identifier, and a token name or the existence of `nonces()` alone proves no permit profile.
If permit is unavailable, request an explicit `approve` transaction or an account batch according to [ORC-43](orc-43.md).
A stale nonce requires a new approval decision and signature; clients MUST NOT silently increase an amount, change a spender, or reuse another chain's domain.

## Rationale

Separate profiles preserve existing ERC-2612 callers while making smart-account support explicit.
Routing is shared with other OneAccount messages, but each signature retains its own purpose and digest.

## Backwards Compatibility

ORC-20 tokens do not automatically gain permit support.
The inspected bridge token exposes ERC-2612, whereas the inspected paymaster calls ERC-7597.
Connecting those components requires a compatible token implementation or an approval fallback; byte packing cannot convert one selector into the other.

## Test Cases

| Case | Expected result |
| --- | --- |
| Valid EOA permit on the declared profile | Set allowance, consume the owner nonce, and emit the upstream approval event. |
| Change spender, chain, token, amount, or nonce | Signature verification fails. |
| `DOMAIN_SEPARATOR()` differs from the separator rebuilt from `eip712Domain()` | Refuse to sign. |
| Submit after the deadline or reuse a consumed nonce | Reject without changing approval state. |
| Both overloads enabled; replay through the other selector | Reject after the shared nonce is consumed. |
| Valid variable-length validator signature | Route it without imposing a 65-byte account envelope. |
| ERC-2612-only token selected for byte-signature sponsorship | Select an explicit fallback or report incompatibility. |

These are required verification cases, not a report of passing contract tests.

## Reference Implementation

- [Bridge token interface](https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/ICrossMintableERC20.sol) and [implementation](https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/CrossMintableERC20V2.sol) expose the existing ERC-2612 path.
- [TokenPaymaster](https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/TokenPaymaster.sol) calls the byte-signature permit in pre-operation payment mode.
- [SDK authorization handling](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts) validates request fields, adds rounded-up 1% approval headroom, and prefixes the validator address.

These are integration starting points, not evidence that the combined profile is implemented end to end.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-42/verification.md).

## Implementation and Activation

This Draft activates no contract change.
Before Review, select the supported token implementations, verify both overloads and contract-owner signatures, and record account initialization and fallback behavior.
Pin the adopted upstream revisions and consumer versions; deployed compatibility remains unverified.

## Security Considerations

Permit messages authorize spending and can be submitted by another party.
A routing prefix is not replay protection; the signed domain and owner binding must be checked.
Unlimited or buffered allowances can outlive the intended operation, and a permit may be consumed even if a later action fails.
Contract signature validity can change when the owner's validator configuration changes.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
