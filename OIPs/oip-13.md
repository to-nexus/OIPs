---
oip: 13
title: Fee Delegation JSON-RPC Extensions
description: JSON-RPC submission and result formats for fee-delegated transactions and their simulation support boundaries.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Interface
created: 2026-10-28
requires: 2
---

# OIP-13: Fee Delegation JSON-RPC Extensions

## Abstract

This proposal specifies the JSON-RPC representation and submission of fee-delegated dynamic fee transactions defined by [OIP-2](oip-2.md).
It defines the sender and payer fields exposed by transaction and receipt queries, raw-submission behavior, and the boundary between optional sponsorship services and transaction validity.
It also records the reference client's current transaction-construction and gas-estimation limitations.
This proposal documents go-cross at commit `4c0838f828f3a6300a1bd09fc70fec474a07a156` and does not change consensus rules.

## Motivation

Wallets, sponsoring services, and indexers need to distinguish the sender who authorizes an operation from the account that pays its execution gas.
They also need consistent transaction identity across submission, pending queries, and inclusion receipts.
A shared RPC specification avoids treating payer fields in responses as supported signing or simulation inputs.

The interface can evolve independently of the transaction encoding and block-validity rules.
Keeping it separate allows RPC additions to be reviewed without redefining the transaction format.
Service-specific sponsorship eligibility remains an implementation policy rather than a network validity requirement.

## Specification

### Scope and Notation

OIP-2 defines the transaction type, signed inner transaction `S`, authorization rules, transaction hash, gas payment, and consensus receipt encoding.
Those rules are referenced rather than redefined here.
The symbols `K`, `RLP`, and `||` use the notation defined in OIP-2.
In this document, `c` denotes the inner transaction's maximum fee per gas and `p` denotes its effective execution gas price at the inclusion block.
JSON-RPC fields do not add fields to the consensus transaction or receipt encodings.

### Transaction Results

Transaction objects returned by `eth_getTransactionByHash`, the block-and-index transaction lookup methods, and block queries with full transactions MUST expose the signed wrapper as a flat JSON object.
They MUST NOT nest the sender fields under `SenderTx` or `S`.
The ordinary destination, value, nonce, gas, calldata, and access-list fields describe the inner sender transaction.

Integer fields use hexadecimal quantities with a `0x` prefix, no leading zeroes, and `0x0` for zero.
Addresses use 20-byte hexadecimal data, and hashes use 32-byte hexadecimal data.
Thus the JSON transaction type is `"0x7"`, while the first byte of a raw transaction is `0x07`.

| JSON field | Required meaning for type `0x7` |
| --- | --- |
| `type` | `"0x7"`. |
| `hash` | The shared transaction hash `K(0x02 || RLP(S))`. |
| `from` | The recovered sender, not the fee payer. |
| `chainId`, `maxFeePerGas`, `maxPriorityFeePerGas` | The inner transaction's chain ID and fee caps. |
| `v`, `r`, `s` | The sender signature; `v` is `0x0` or `0x1`, without an EIP-155 adjustment. |
| `feePayer` | The declared and authorized fee payer address. |
| `fv`, `fr`, `fs` | The fee payer signature; `fv` is `0x0` or `0x1`. |
| `gasPrice` | The effective price `p` for an included transaction with a known block base fee; otherwise the fee cap `c`. |

The reference client omits `yParity` for this transaction type; consumers MUST obtain the sender parity from `v` and the payer parity from `fv`.
For a pending transaction, `blockHash`, `blockNumber`, and `transactionIndex` are `null`.
Fee payer fields are omitted for ordinary transactions that have no wrapper.

Raw transaction lookup methods MUST return the complete stored encoding, including the `0x07` type byte and payer signature when the stored transaction is a wrapper.
Because the inner transaction and its wrappers share a hash, lookup by hash does not select a particular sponsorship variant.
The returned transaction describes the version present in the canonical chain or the node's pool; it need not be the exact variant a caller previously submitted.

### Receipt Results

A JSON-RPC receipt for an included wrapper MUST contain `type: "0x7"`, its shared `transactionHash`, the sender in `from`, and the payer address in `feePayer`.
The standard `gasUsed`, `cumulativeGasUsed`, `effectiveGasPrice`, `status`, logs, and contract-creation fields retain their usual meanings.
The execution gas charge to the payer is `gasUsed * effectiveGasPrice`; this excludes independent value transfers or other balance changes.
Receipts do not contain `fv`, `fr`, or `fs`; these are available from the transaction object.

These rules apply to `eth_getTransactionReceipt` and other methods that return the same receipt representation.
A pending transaction has no inclusion receipt.
If the ordinary inner transaction was included instead, its receipt has type `0x2` and no `feePayer`, even though its hash matches the submitted wrapper.
Clients MUST inspect the returned transaction or receipt to determine whether sponsorship actually occurred.

### Raw Submission and Optional Sponsorship

`eth_sendRawTransaction` accepts the complete signed transaction as its single hexadecimal-data argument.
Submitting a `0x07` wrapper requires both signatures to be present; this method is not a fee payer signing API.
The node MUST decode the wrapper, validate its payer authorization, and apply its normal transaction admission checks before reporting acceptance.
The success result is the shared transaction hash, not the Keccak-256 hash of the submitted raw bytes.
Acceptance does not establish inclusion or successful EVM execution.

The reference client's optional `eth_sendRawTransactionSync` uses the same submission path and returns an inclusion receipt when available.
A timeout after submission does not cancel or remove the transaction.

When a GasAbs service is configured, the reference client also applies an optional sponsorship policy to raw submissions:

- An eligible signed `0x02` transaction can be sent to the service and returned as a signed `0x07` wrapper before pool submission.
- An existing `0x07` wrapper is not re-signed by this automatic wrapping path.
- A non-eligible transaction continues through ordinary submission unless a separate policy check rejects it.
- Blacklisted sender or destination addresses can cause rejection, including for an already signed wrapper.
- A successful service response can return the original `0x02` transaction without sponsorship; ordinary sender-funded admission then applies.
- If the service request returns an error, that submission attempt stops rather than locally falling back to the original transaction.

[OIP-16](oip-16.md) specifies the service methods, policy synchronization, and the reference server's retry behavior.
In particular, a repeated request can receive the original transaction successfully after a prior policy error; an RPC success alone does not establish sponsorship.

With no GasAbs client configured, the raw submission path does not add sponsorship.
Service-specific signing methods, approval lists, and availability are not requirements for validating an independently signed wrapper.
RPC fee limits, local policy, and pool reservations can reject a transaction that would satisfy block execution rules.
Submission failures use JSON-RPC errors; this proposal does not assign new fee-delegation-specific error codes or require exact error messages.

### Construction, Calls, and Gas Estimation

The pinned client's `TransactionArgs` input schema has no `feePayer`, `fv`, `fr`, or `fs` fields and does not construct type `0x07`.
The transaction result schema above MUST NOT be treated as a supported signing or simulation request schema.
Adding those fields to an argument object does not provide a supported way to select a sponsor.

| Method | Reference behavior |
| --- | --- |
| `eth_sendTransaction` | Constructs and signs a supported ordinary transaction with the node's sender account; it does not invoke the raw-submission sponsorship path. |
| `eth_fillTransaction` | Fills ordinary transaction defaults and returns the unsigned transaction; it does not create or sign a payer wrapper. |
| `eth_signTransaction` | Signs an ordinary transaction with the sender account; it does not obtain a payer signature. |
| `eth_call` | Simulates the ordinary call arguments; no payer authorization is supplied or checked through those arguments. |
| `eth_estimateGas` | Estimates the ordinary sender-funded call; it does not contact GasAbs or validate a proposed sponsor's balance or signature. |

For nonzero fee caps, the reference estimator limits the gas allowance using the sender's available balance after subtracting the requested value.
The execution message built from these arguments has no fee payer.
A sender with insufficient gas funds can therefore receive an estimation error even when a separate payer could fund a valid wrapper.
Gas estimation, any state overrides, and optional sponsorship approval are separate operations; none guarantees admission or inclusion of the signed transaction.
Support for payer-aware construction or estimation would require additional specified input and execution semantics and is not asserted by this proposal.

## Rationale

A flat transaction object preserves the familiar dynamic fee fields while exposing the payer authorization through separate fields.
Keeping `from` as the sender maintains the distinction between execution identity and payment responsibility.
The shared transaction hash allows applications to track an operation before and after sponsorship, while the returned transaction and receipt identify the variant actually stored or included.

The response schema and construction schema serve different purposes.
Documenting their current differences avoids implying that an output field is accepted as an input or that estimation can authorize sponsorship.
Optional GasAbs integration is described separately from required transaction and receipt representations so that independently signed wrappers do not depend on a particular service.

## Backwards Compatibility

Ordinary transaction and receipt representations retain their existing meanings and omit the payer fields when no wrapper is present.
Consumers of type `0x7` must distinguish the sender signature from the payer signature and use the transaction hash defined by OIP-2.
The pending `gasPrice` value is a fee cap rather than a confirmed execution price.

This proposal does not add payer-aware arguments to the reference client's construction or simulation methods.
Any future input extension must define its authorization, balance, and failure semantics explicitly.
RPC changes described here do not modify OIP-2's transaction encoding, signatures, or block-validity rules.

## Test Cases

The cases below reuse the [OIP-2 deterministic encoding vector](../assets/oip-2/fee-delegation.json).
Its fixed keys are public test fixtures and MUST NOT be used to hold funds.
They provide a common signed transaction for comparing the Core encoding with the RPC representation.

The following is an excerpt of a pending transaction lookup response for the deterministic encoding vector.
Other ordinary transaction fields and pending block-location fields are omitted from this excerpt.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "type": "0x7",
    "hash": "0xac2a8784b106520e45e30c066700012e39f6253a5fd721b03becf8dc58bcbed9",
    "from": "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf",
    "feePayer": "0x2b5ad5c4795c026514f8317c7a215e218dccd6cf",
    "chainId": "0x956d7",
    "gasPrice": "0x4a817c800",
    "maxFeePerGas": "0x4a817c800",
    "maxPriorityFeePerGas": "0x77359400",
    "v": "0x0",
    "fv": "0x1",
    "fr": "0x2d97380d6cd4aa6cdfce9eade2e832873e41d030383aad29da9b49064f3c7f1f",
    "fs": "0xa3c74e5eb6cd6aa1d78813ce5b98b4662b8ee914134d9df3259a9d0803b7889"
  }
}
```

| RPC case | Expected result |
| --- | --- |
| Submit the vector's `raw_transaction` with sufficient sender and payer funding, an available sender nonce, and permissive local policy | Return the vector's `transaction_hash`; do not return `outer_envelope_keccak256`. |
| Query a pending wrapper | Return sender and payer separately, both signatures, fee-cap `gasPrice`, and null block-location fields. |
| Query the wrapper after inclusion | Return the same hash and authorization fields, block location, and effective `gasPrice`. |
| Query an included wrapper's receipt | Include `feePayer` and type `0x7`; omit payer signature fields. |
| Query a receipt after the ordinary inner transaction was included | Return type `0x2` without `feePayer`; the matching hash alone does not establish sponsorship. |
| Submit a wrapper with a mismatched payer signature | Return an error rather than an acceptance hash. |
| Submit an ordinary transaction without a configured sponsorship service | Preserve ordinary sender-funded submission. |
| Estimate with a sender lacking gas funds while a separate payer is funded | The pinned estimator can fail because it does not accept a payer through `TransactionArgs`. |
| Add `feePayer` to fill, sign, call, or estimation arguments | Do not treat the extra field as supported sponsorship authorization. |

During preparation of this proposal, temporary checks against the reference revision verified the response excerpt, pending and included price fields, receipt fields, raw-submission hash and payer rejection, and construction of simulation arguments without a payer.
The submission checks used a capturing backend and did not exercise real pool admission or mining.
The existing [TestEstimateGas](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api_test.go#L722) also passed; it can be run with `go test ./internal/ethapi -run '^TestEstimateGas$' -count=1`.
The optional sponsorship-service cases require separate integration tests with the configured service; the encoding vector does not verify them.

## Reference Implementation

The reference revision is [go-cross `4c0838f828f3a6300a1bd09fc70fec474a07a156`](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

| Area | Source |
| --- | --- |
| RPC submission, transaction objects, receipts, and estimation entry point | [api.go](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go) |
| Construction and simulation argument schema | [transaction_args.go](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/transaction_args.go) |
| Sender-balance limits during gas estimation | [gasestimator.go](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/gasestimator/gasestimator.go) |
| Optional sponsorship-service client and eligibility checks | [gasabs/client.go](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/gasabs/client.go) |

## Implementation and Activation

The reference client implements the transaction and receipt fields and raw-submission paths described above.
Its argument schema does not implement payer-aware transaction construction or gas estimation.
Optional GasAbs behavior depends on the node's service configuration and local policy.

Affected components are RPC clients and servers, wallets, sponsoring services, and indexers.
This interface depends on OIP-2 support but does not introduce a new consensus activation condition.
Publication of this proposal does not establish deployment on a particular RPC endpoint or network.
Future interface additions require client coordination and separate verification of the advertised method behavior.

## Security Considerations

RPC clients should compare the submission result with the signed inner transaction's hash and inspect the included transaction or receipt for the actual payer.
An estimation result does not authenticate a sponsor or establish that its funds are available.
Optional sponsorship-service policies and failures must remain distinct from consensus authorization and validity.

The same transaction hash can identify the ordinary inner transaction or a sponsored wrapper.
A matching hash alone does not prove which account paid for inclusion.
Raw transaction and receipt queries must remain consistent with the stored or included variant.

Optional signing services are external integrations with their own availability and authorization policies.
Applications should not treat an estimation result, sponsorship eligibility, or an RPC acceptance hash as a guarantee of successful execution.
Service integration and live endpoint behavior have not been verified by the recorded serializer and submission-handler checks.

## References

- [OIP-2: Fee-Delegated Dynamic Fee Transactions](oip-2.md).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
