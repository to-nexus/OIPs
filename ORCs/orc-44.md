---
orc: 44
title: Wallet and Paymaster Interfaces
description: Batch-call capabilities, sponsorship negotiation, and prepared-operation confirmation for ONEchain wallets.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 40, 42, 43
---

# ORC-44: Wallet and Paymaster Interfaces

## Abstract

This proposal defines a ONEchain integration profile for [EIP-5792](https://eips.ethereum.org/EIPS/eip-5792) wallet calls and [ERC-7677](https://eips.ethereum.org/EIPS/eip-7677) paymaster requests.
It adds account/chain binding and preparation rules while distinguishing implemented wallet capabilities from proposed service interoperability.

## Motivation

Applications submit intent through a wallet, while the wallet coordinates a bundler, a paymaster, and a signing account.
The user must confirm the actual operation after sponsorship and authorization requirements are known.

## Specification

### Wallet Calls and Capabilities

Adopt the upstream wallet methods, request schemas, status model, and error conventions by reference.
The inspected provider uses version `2.0.0`, validates chain and authorized account, requires a boolean `atomicRequired`, and returns a batch identifier.
A conforming wallet MUST return an unpredictable identifier as EIP-5792 requires; the sample returns the UserOperation hash.
It advertises atomic execution and exposes `wallet_getCapabilities`, `wallet_sendCalls`, `wallet_getCallsStatus`, and `wallet_showCallsStatus`.
Capabilities MUST describe supported behavior for the requested account and chain.
An unsupported mandatory capability MUST fail; optional capabilities may be declined under the upstream rules.
Try-mode execution that permits individual failures MUST NOT be advertised as an atomic batch under [ORC-40](orc-40.md).

EIP-5792 requests atomic execution through `atomicRequired`, not through a request capability.
The sample accepts a request capability named `atomic` whether or not it is optional and ignores other optional capabilities it does not support.
Its use of a wallet-configured paymaster does not establish support for an arbitrary application-selected paymaster service.
Adding the ERC-7677 `paymasterService` capability requires explicit service trust, authorization, and capability implementation.

### Sponsorship Negotiation

Use `pm_getPaymasterStubData` for estimation fields and `pm_getPaymasterData` for final sponsorship according to ERC-7677 and the selected EntryPoint version.
ERC-7677 was in Review when consulted and defines operation fields for EntryPoint v0.6 and v0.7; for v0.8 and v0.9 the reference sends the packed operation fields, including `eip7702Auth` when present, as a ONEchain extension.
Both requests MUST bind the operation, chain ID, EntryPoint, and declared context.
The ordinary inspected flow is stub data, gas estimation, final sponsorship, account signing, then submission.
A paymaster whose signature covers gas fields, such as the [ORC-43](orc-43.md) paymaster, MUST NOT mark stub data as final, and wallets MUST request final data after gas estimation for it.

For token payment, the request context uses `token` for the payment token address, an optional `permit` object with hex `amount`, `deadline`, and `signature`, and optional service-defined `policyId` and `providerId` strings.
The service selects the [ORC-43](orc-43.md) payment mode and returns it in the paymaster data.
Permit and approval requests follow [ORC-42](orc-42.md).
Wallets MUST decode the returned paymaster data and reject a result that changes the user-approved owner, spender, chain, token, payment mode, or maximum charge.
The reference service reports a required permit with error code `-32002` and a required approval with `-32003`, whose data can set `separateTransaction`.
These codes overlap the [EIP-1474](https://eips.ethereum.org/EIPS/eip-1474) meanings of `-32002` and `-32003`, so the interoperable codes and error-data schema remain a Review decision; this Draft allocates no wallet capability identifier.

### Prepare, Confirm, and Submit

The proposed wallet integration has these stages:

1. Validate the account, chain, EntryPoint version, targets, values, and required capabilities.
2. Prepare calls and sponsorship without submitting an account operation or silently signing a token approval.
3. Surface any validated permit or approval requirement for a separate user decision, then prepare again if necessary.
4. Present the complete operation, native value, fee token, maximum token charge, and authority changes for confirmation.
5. Sign and submit those reviewed fields without silently replacing the quote, calls, paymaster, or authorization.

The SDK's prepared object contains `userOperation`, `entryPoint`, and `chainId`, with an empty operation signature.
Before signing, it checks sender and EntryPoint consistency, chain compatibility, and that empty signature.
If nonce, sponsorship validity, fees, or authority have become stale, an integration MUST fail or obtain fresh preparation and confirmation.
Wallets MUST refresh an expired or materially changed token quote before asking for confirmation.
A prepared object is not a nonce reservation or an inclusion guarantee.
Gas sponsorship does not cover native value in the calls.

### Status and Retry

Batch identifiers MUST remain bound to their submitting wallet context and operation.
An accepted RPC response is pending, not proof of successful execution.
The inspected provider maps pending, successful, and failed operations to upstream status values 100, 200, and 500 and includes available receipts.
Conforming wallets MUST include the receipt logs that EIP-5792 requires and MUST report dropped operations with status 400; the sample returns empty logs and keeps dropped operations at 100.
Clients MUST reconcile status before resubmitting an uncertain operation; a transport timeout is not evidence that nothing was submitted.
A wallet MUST retain the identifier of a submission whose response was lost so that it can be reconciled; the sample discards it on a transport error.
The wallet MUST NOT silently retry a non-idempotent payment under a fresh identifier.

## Rationale

Standard methods provide common transport, while preparation and binding rules protect the user's reviewed intent across several services.
Separating configured sponsorship from application-selected sponsorship prevents false capability claims.

## Backwards Compatibility

Existing applications can continue using supported wallet methods and wallet-configured sponsorship.
An unsupported mandatory paymaster capability remains an error until implemented.
Node JSON-RPC and the GasAbs interface retain their scope in [OIP-14](../OIPs/oip-14.md) and [OIP-16](../OIPs/oip-16.md).
Bundler methods follow [ERC-7769](https://eips.ethereum.org/EIPS/eip-7769); the SDK also uses the nonstandard `eth_getUserOperationNonce`.

## Test Cases

| Case | Expected result |
| --- | --- |
| Wrong chain or unauthorized sender | Reject before signing or submission. |
| Unsupported mandatory capability | Reject instead of silently dropping it. |
| Sample receives mandatory application-selected paymaster capability | Do not claim it is implemented. |
| Signed paymaster returns final stub data | Request final data after estimation instead of using the stub. |
| Returned paymaster data changes the maximum charge | Reject before confirmation. |
| Preparation encounters an approval requirement | Return validated details for user consent without submission. |
| Prepared operation already contains a signature | Reject the send-prepared path. |
| Sponsor or calls change after confirmation | Require renewed preparation and confirmation. |
| Submission response is lost | Reconcile the existing operation before an explicit retry. |

These are interoperability cases; no wallet-to-chain test was run for this Draft.

## Reference Implementation

- [Sample wallet provider](https://github.com/to-nexus/one-account-wallet-sample/blob/654de5e2a4125218555bfb810dcd383a22dec27d/packages/wallet/src/provider.ts) and [paymaster configuration](https://github.com/to-nexus/one-account-wallet-sample/blob/654de5e2a4125218555bfb810dcd383a22dec27d/packages/wallet/src/config.ts).
- [SDK paymaster client](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/paymasterClient.ts), [bundler preparation and submission](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/bundlerClient.ts), and [token authorization handling](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts).

Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-44/verification.md).

## Implementation and Activation

Before Review, pin supported upstream schemas and service versions, define token context/error fields, and verify final confirmation with actual wallet and paymaster deployments.
Application-selected sponsorship is additional integration work, not a capability established by the inspected sample.
This Draft makes no service deployment or availability claim.

## Security Considerations

Remote service responses, quoted prices, sponsorship URLs, and approval instructions are untrusted input until validated against the user's intent and configured trust policy.
Cross-chain confusion, stale nonces, replayed approvals, and retries can cause unintended charges or duplicate actions.
Capability discovery and successful simulation are not authorization to sign changed transaction fields.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
