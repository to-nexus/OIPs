---
orc: 45
title: Signed Token Transfer Authorization
description: An ERC-3009 payment profile with explicit cancellation and consumer authorization boundaries.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 20
---

# ORC-45: Signed Token Transfer Authorization

## Abstract

This proposal extends [ORC-20](orc-20.md) with a signed-payment profile based on [ERC-3009](https://eips.ethereum.org/EIPS/eip-3009).
It proposes consumer checks and cancellation support for payments that should not leave a reusable allowance.
No matching ONEchain token implementation was established.

## Motivation

Some payment flows need authorization for one transfer rather than continuing spending authority.
A dedicated profile can make recipient, amount, expiry, and cancellation visible without conflating a payment signature with gas sponsorship.

## Specification

### Transfer Profile

Conforming tokens MUST meet ORC-20 and adopt ERC-3009's transfer, receive, authorization-state, and event interfaces by reference.
This proposed profile additionally requires its optional signed-cancellation interface.
Tokens MUST list cancellation support in their deployment profile, since ERC-3009 defines no interface identifier.
The baseline uses the upstream EOA signature arguments; contract-owner verification is not implied.
ERC-3009 does not apply to smart contract accounts, so OneAccount owners are outside this profile.
ERC-3009 remains Draft at preparation time, so an implementation MUST pin the adopted revision before review.

Authorization uses an owner-scoped `bytes32` nonce, independently of permit nonces.
The EIP-712 domain MUST include `chainId` and `verifyingContract`; the message binds sender, recipient, raw amount, validity window, and the `bytes32` nonce.
Execution MUST satisfy `validAfter < block.timestamp < validBefore`; ERC-3009 states these strict bounds only in its reference implementation.
Used or cancelled authorization cannot be executed again.

### Consumer Requirements

A wallet MUST present the actual recipient, amount, token, chain, validity window, and payment purpose before signing.
The consuming application MUST bind the signature to its intended order or account credit and reconcile settlement with that same context.
It MUST derive the authorization nonce from that context, for example as the hash of the order identifier, so one authorization cannot settle a different order.
It MUST NOT credit whichever user happens to submit another user's signed payment.
For a contract receiving and processing payment atomically, use the upstream receive path's payee/caller binding and verify the intended beneficiary within the application.
The signature authorizes token movement, not arbitrary relayer fees or a different recipient.

Cancellation and transfer compete for inclusion; a requested cancellation is not final until its state transition is confirmed.
Applications MUST reconcile on-chain authorization state before reporting a payment cancelled or retrying an uncertain submission.
Failed execution MUST NOT be reported as paid merely because a signature was accepted off chain.

### Relationship to Other Payment Flows

[ORC-42](orc-42.md) grants allowance and remains a separate interface.
[ORC-43](orc-43.md) determines sponsorship and gas settlement; this Draft does not supply native fees or make this transfer interface usable by the inspected paymaster.
Smart-account owners can use their account's normal token calls; a byte-signature or ERC-1271 authorization extension would require its own explicit compatibility design.

## Rationale

Requiring cancellation is a proposed ONEchain integration choice for outstanding signed payments.
Separating payment and sponsorship avoids promising that a token signature alone funds execution.

## Backwards Compatibility

Existing ORC-20 and permit interfaces remain unchanged.
An ERC-3009 implementation without cancellation does not meet this additional profile requirement.
No current token is asserted to gain these methods through documentation.

## Test Cases

| Case | Expected result |
| --- | --- |
| Timestamp equals either validity boundary | Reject. |
| Authorization already used or cancelled | Reject replay. |
| Recipient, token, chain, or amount is changed | Reject the modified signed payment. |
| Cancellation and payment race | Only the first valid state transition succeeds. |
| Different user submits a valid payment for an order | Credit only the beneficiary bound by the application. |
| Relayer cannot pay gas | Report submission failure without claiming payment. |

Only validity-boundary arithmetic was checked; signature and token execution tests remain required.

## Reference Implementation

No corresponding ONEchain token contract or payment consumer was selected or validated.
ERC-3009 is the interface reference; no deployed conformance is asserted.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-45/verification.md).

## Implementation and Activation

Before Review, select a payment product, adopt a pinned upstream revision, implement cancellation, and validate payment/order binding with its actual consumers.
Decide whether any smart-account-specific extension is needed rather than assuming signature formats are interchangeable.
This design Draft deploys no token or relayer.

## Security Considerations

Leaked signatures can be submitted by other parties within their intended authority.
Order attribution, cancellation races, uncertain submission outcomes, and unsupported signature schemes must be handled by the payment integration.
A valid signature is not proof of settlement or sufficient token balance at execution time.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
