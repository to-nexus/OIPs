---
orc: 43
title: Token-Denominated Gas Payment
description: Token paymaster authorization, byte layouts, charging, and refund accounting for ONEchain accounts.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 20, 40, 42
---

# ORC-43: Token-Denominated Gas Payment

## Abstract

This proposal specifies the inspected ONEchain token-paymaster payment profile for [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) operations.
It defines token units, payment modes, maximum charges, versioned data, and refund ownership, with proposed integration requirements for supported [ORC-20](orc-20.md) assets.

## Motivation

Token gas payment combines an operation signature, service authorization, token allowance, and native EntryPoint gas funding.
Clients need to agree on each boundary so a displayed quote matches the accepted charge and refund behavior.

## Specification

### Scope and Supported Assets

The account pays tokens to a paymaster; the paymaster funds native gas through its EntryPoint deposit.
This does not fund native value transferred by account calls.
It is separate from [OIP-2](../OIPs/oip-2.md) fee delegation and the [OIP-16](../OIPs/oip-16.md) GasAbs service.
Wallet/service negotiation belongs to [ORC-44](orc-44.md), and permits follow [ORC-42](orc-42.md).

The baseline supported-asset profile MUST identify token, chain, paymaster, EntryPoint address/version, and applicable transfer restrictions.
The paymaster MUST hold the EntryPoint stake that [ERC-7562](https://eips.ethereum.org/EIPS/eip-7562) requires for a paymaster that returns a context and reads its own storage.
Tokens MUST meet ORC-20; fee-on-transfer and rebasing behavior require a separate accounting profile and MUST NOT be silently treated as ordinary transfers.

### Payment Data

The inspected layout uses big-endian packed integers with these byte offsets in `paymasterAndData`:

| Bytes, end exclusive | Field |
| --- | --- |
| 0..20 | Paymaster address. |
| 20..36, 36..52 | Verification and post-operation gas limits, each `uint128`. |
| 52..72 | Payment token address. |
| 72..104, 104..136 | Token price and user maximum token cost, each `uint256`. |
| 136..137 | Mode: `0` for PostOp, `1` for PreOp. |
| 137..143, 143..149 | `validUntil` and `validAfter`, each `uint48`. |
| 149..signature suffix | Optional permit amount `uint256`, deadline `uint48`, and nonempty ERC-7597 signature. |

The v0.9 suffix is a 65-byte backend signature, its 2-byte length (`0x0041`), and the 8-byte EntryPoint signature trailer `0x22e325a297439656`.
The v0.8 variant appends only the 65-byte backend signature and rejects the block-range flag in validity fields.
Minimum lengths without permit are therefore 224 bytes and 214 bytes respectively.
Integrations MUST select the layout by the deployed EntryPoint/paymaster variant, not by the apparent length alone.
Validity interpretation, including supported v0.9 block-range semantics, follows that EntryPoint version.
Malformed mode or suffix encoding MUST be rejected.
Permit bytes are decoded and validated only when the PreOp path uses the permit; the account operation signature binds them in either case.
ERC-7597 was Draft when consulted; the adopted revision MUST be pinned.

### Quote and Authorization

`tokenPrice` is raw token units per one native ONE (`10^18` native base units).
For a 6-decimal asset priced at 2,000 tokens per ONE, the price is `2,000,000,000`.
The backend signature is a 65-byte ECDSA signature over the following digest, without an EIP-191 or EIP-712 prefix:

```text
opHash = keccak256(abi.encode(sender, nonce, keccak256(initCode), keccak256(callData),
                              accountGasLimits, preVerificationGas, gasFees,
                              keccak256(paymasterAndData[0:149])))
digest = keccak256(abi.encode(TYPEHASH, opHash, eip7702Delegate, validUntil, validAfter,
                              paymaster, entryPoint, chainId))
TYPEHASH = keccak256("OneTokenPaymaster(bytes32 userOpHash,address eip7702Delegate,uint48 validUntil,uint48 validAfter,address paymaster,address entryPoint,uint256 chainId)")
```

`eip7702Delegate` is the sender's EIP-7702 delegate, or zero for an account without delegation.
Optional permit bytes are outside that backend prefix; the account operation signature binds them.
The markup is read during validation and frozen in the settlement context, rather than being an independently signed field in the prefix.
The user-signed `maxTokenCost` bounds acceptable validation-time charge; client quote handling and confirmation follow ORC-44.

### Charging and Refunds

Let `P` be token price, `M` the validation-time markup in basis points, and `maxCost` the EntryPoint maximum native cost.
The reference calculation is `maximumCharge = floor(maxCost * P * M / (10^18 * 10000))`.
Reject if it exceeds `maxTokenCost`; zero price or missing token postOp-gas configuration also fails.
Freeze price, markup, maximum charge, and charged postOp-gas estimate in the validation context.

PreOp consumes the sender's refund credit first and transfers the remaining maximum charge before account execution.
If allowance is insufficient, it may execute the declared byte-signature permit and recheck allowance.
PostOp does not collect during validation but requires the sender's token balance to cover the maximum charge; it rejects embedded permit data, and its allowance can be established during account execution.
This does not guarantee collection if that execution reverts or later removes funds or allowance.

For gas limit `L` and configured estimate `E`, validation requires `L >= E > 0`.
Charged postOp gas is `E + floor((L-E)*10/100)` when `L-E > 40000`, otherwise `E`.
Final token charge is the same floor conversion of `actualGasCost + chargedPostOpGas * actualUserOpFeePerGas`, capped at `maximumCharge`.
PreOp records the difference as a credit belonging to `(token, sender)`; PostOp transfers the final charge from that sender.
Refunds are credits, not automatic transfers: `refundCredits(token, account)` reads them and `claimRefund(token)` pays the caller.
Owner withdrawals MUST exclude `totalRefundCredits(token)`.

For `maxCost = 10^15`, `P = 2*10^9`, and `M = 11000`, the maximum is `2,200,000` token units.
If total charged native cost is `6*10^14`, the final charge is `1,320,000` and PreOp credit increases by `880,000`.

## Rationale

Versioned byte layouts avoid treating incompatible EntryPoint encodings as interchangeable.
Freezing validation-time values and capping settlement makes the maximum charge and credit ownership reproducible.

## Backwards Compatibility

An ORC-20 token is not automatically enabled for sponsorship, and ERC-2612-only tokens cannot supply the embedded ERC-7597 permit.
The v0.8 layout requires explicit version selection.
Current source behavior is not an assertion of deployed acceptance by any bundler or service.

## Test Cases

| Case | Expected result |
| --- | --- |
| No-permit v0.9/v0.8 payload | Minimum 224/214 bytes with the correct version-specific suffix. |
| Maximum exceeds the user cap | Reject before collecting payment. |
| Numerical quote and charge example above | Maximum 2,200,000; charge 1,320,000; credit 880,000. |
| PreOp credit covers only part of the maximum | Debit credit and transfer exactly the remainder. |
| PostOp payload includes permit bytes | Reject. |
| Account execution reverts after an approval call | Approval rolls back; do not assume PostOp collection succeeds. |
| Admin tries to withdraw reserved refunds | Reject the unavailable amount. |
| Claim is repeated after a successful claim | No double payment. |

Only arithmetic examples were checked for this Draft; the reference repository's EntryPoint integration tests were not run for it.

## Reference Implementation

References to `to-nexus/one-account-sdk` and `to-nexus/one-paymaster-contracts` are [internal verification sources](../README.md#verification-sources) and require access to the cited repositories.

- [TokenPaymaster](https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/TokenPaymaster.sol), [v0.8 variant](https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/TokenPaymasterV08.sol), and [backend signature binding](https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/SignedPaymaster.sol).
- [Existing EntryPoint integration tests](https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/test/TokenPaymasterIntegration.t.sol).
- [SDK permit and approval integration](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts).

Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-43/verification.md).

## Implementation and Activation

This proposal is intended for Final registration under [OIP-1's retrospective path](../OIPs/oip-1.md#documenting-existing-deployed-behavior); requirements that the referenced implementations do not meet must be implemented or moved to a separate proposal before then.
Before that registration, pin supported deployments, EntryPoint versions, service quote fields, asset behavior, and the upstream revision used for validation rules.
Run actual `handleOps` scenarios for successful, reverted, and failed-collection operations, including validation-time permit restrictions and refund claims.
The service's full admission policy and current deployment compatibility were not established.
This Draft authorizes no deployment or token allowlist change.

## Security Considerations

Simulation cannot guarantee that post-operation allowance or balances will remain available.
A service-only allowlist is not a substitute for on-chain backend-signature authorization because third parties can submit directly to EntryPoint.
Tokens with hooks, transfer taxes, rebasing, or administrative freezes can invalidate accounting assumptions.
Refund balances are liabilities, and mutable markup can change a quote within the signed maximum; user confirmation must preserve that bound.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
