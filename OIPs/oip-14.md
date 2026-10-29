---
oip: 14
title: ONEchain RPC Compatibility Profile
description: Ethereum block tags and fee history, and the Istanbul management and inspection interface.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Interface
created: 2026-10-28
requires: 2, 3
---

# OIP-14: ONEchain RPC Compatibility Profile

## Abstract

This proposal specifies ONEchain's JSON-RPC compatibility profile.
It describes block-tag resolution, fee-history calculations, and the inspection and voting methods of the Istanbul namespace.
It distinguishes Ethereum-compatible encodings from the existing Istanbul response formats and documents method-specific errors and limits.

## Motivation

Wallets and indexers cannot infer all ONEchain behavior from Ethereum method names.
In particular, safe and finalized markers come from Istanbul processing, fee history uses ONEchain's base fee rules, and Istanbul methods do not support every Ethereum block tag.
Documenting these differences prevents incorrect finality, fee, and validator-status interpretations.

## Specification

### Scope and Encoding

This profile applies to Istanbul chains and the reference implementation identified below.
Method availability depends on the node's configured transports and enabled RPC namespaces.
Registration of a method does not require every public provider to expose it.

The `eth` namespace retains standard JSON-RPC 2.0 envelopes, hexadecimal data, and hexadecimal quantities without leading zeroes.
[OIP-2](oip-2.md) and [OIP-13](oip-13.md) define delegated transaction fields and submission behavior.
[OIP-3](oip-3.md) defines the native transfer logs returned by receipt and log APIs.
This document adds no transaction type or alternate log format.

Istanbul response objects use the field names and JSON types specified below.
Their integer fields are generally JSON numbers, not Ethereum hexadecimal quantities.
Addresses and hashes remain `0x`-prefixed hexadecimal strings.
Clients must tolerate additional response fields; this profile defines only the fields and methods listed here.

### Ethereum Block Tags

The standard block/header resolver used by `eth` methods behaves as follows:

| Selector | Resolution |
| --- | --- |
| Explicit nonnegative block number | The locally available canonical header or block at that height. |
| `latest` | The current canonical head. |
| `safe` | The node's current safe marker; return an error if unavailable. |
| `finalized` | The node's current finalized marker; return an error if unavailable. |
| `pending` | The miner's pending block; return an error if no pending block is available. |
| `earliest` | The history-pruning cutoff exposed by the backend, which need not be genesis on a pruned node. |

Where a method accepts a block-number-or-hash object, a hash lookup with `requireCanonical: true` must reject a noncanonical block.
Availability of a header does not guarantee availability of its historical state, receipts, or blob data.
Individual methods may retain their own missing-result behavior; for example, the sidecar methods are specified separately below.

After an Istanbul block becomes the canonical head through the normal import path, the reference client updates both the safe and finalized markers to that block.
These markers express the client's imported Istanbul consensus state; they do not require Ethereum Beacon finality.
They commonly coincide with `latest` after processing, but callers must not assume equality across separate requests or during startup and recovery.

### Fee History

`eth_feeHistory(blockCount, newestBlock, rewardPercentiles)` uses [OIP-9](oip-9.md) for ONEchain's next-block execution base fee.
For `m` returned blocks, the result contains:

| Field | Meaning |
| --- | --- |
| `oldestBlock` | Actual first returned block number, as a hexadecimal quantity. |
| `baseFeePerGas` | `m + 1` hexadecimal quantities: each block's base fee followed by the calculated next base fee. |
| `gasUsedRatio` | `m` JSON numbers, each `header.gasUsed / header.gasLimit`. |
| `reward` | When percentiles are requested, `m` rows of hexadecimal priority-fee quantities in requested percentile order. |

Requested percentiles must be strictly increasing and lie between `0` and `100`, inclusive.
The reference client limits the percentile count and caps history length according to its configured header/block history limits.
The returned range may be shorter than requested; callers must use the returned `oldestBlock` and array lengths.
An empty percentile list omits reward rows.
A zero block count returns no history.

For each block's reward row:

1. Derive each transaction's effective priority fee relative to that block's base fee.
2. Exclude transactions whose fee cap is below the base fee and for which the reference calculation reports `ErrGasFeeCapTooLow`.
3. Pair each remaining priority fee with that transaction receipt's gas used and sort by priority fee ascending.
4. Let `W` be the sum of those included gas weights, and select each percentile at the first cumulative weight reaching `floor(W * percentile / 100)`.
5. If no transactions remain, return zero for every requested percentile.

The reference implementation evaluates the percentile threshold using floating-point arithmetic before conversion to an unsigned integer.
The weighting total is the included receipt gas, not the header's gas used when some transactions were filtered out.
`gasUsedRatio` continues to describe the whole block.
The name `reward` denotes effective priority-fee statistics; it does not specify the amount credited to ONEchain's fee beneficiary or imply base fee burning.

Fee history has its own pending-block behavior.
If `newestBlock` is `pending` but no pending block exists, the reference client falls back to the canonical head and reduces the requested count by one.
It does not use the ordinary block resolver's pending-unavailable error in this case.
An explicitly requested future height is an error.

Blob fee-history fields, when returned, do not imply that public blob transaction submission is enabled.
[OIP-10](oip-10.md) defines that distinction.

### Istanbul Inspection Methods

The namespace is `istanbul`, registered with version `1.0`.
For the number-based inspection methods, an omitted argument or `latest` resolves to the current head.
Use an explicit nonnegative height for historical queries.
`earliest`, `pending`, `safe`, and `finalized` are not supported aliases in these methods; the reference implementation does not route them through the Ethereum block-tag resolver.

| Method | Arguments | Result |
| --- | --- | --- |
| `istanbul_nodeAddress` | None | The local node's ECDSA validator address. |
| `istanbul_getSnapshot` | Optional block number | Validator and vote snapshot after that block. |
| `istanbul_getSnapshotAtHash` | Block hash | Snapshot after the identified block. |
| `istanbul_getValidators` | Optional block number | Sorted validator addresses in that block's resulting snapshot. |
| `istanbul_getValidatorsAtHash` | Block hash | The corresponding validator address list. |
| `istanbul_getSignersFromBlock` | Optional block number | The block's number, hash, author, and committed-seal signers. |
| `istanbul_getSignersFromBlockByHash` | Block hash | The same signer information for the identified block. |
| `istanbul_getConfig` | Optional block number | Effective configuration at that height. |
| `istanbul_isValidator` | Optional block number | Whether the local node belongs to the resulting validator set. |

Unknown blocks normally return an error for these inspection methods.
One reference-client exception is `istanbul_isValidator`: it suppresses a validator-lookup error and returns `false`.
Clients needing to distinguish nonmembership from an unavailable block must use a snapshot or validator-list lookup instead.

A snapshot contains `epoch`, `number`, `hash`, `votes`, `tally`, `validators`, and `policy`.
Each vote contains `validator`, `block`, `address`, and `authorize`; each address-keyed tally contains `authorize` and `votes`.
The `number`, epoch, policy, block, and vote-count values are JSON numbers; authorization values are booleans.
An empty vote list may be `null`.
Snapshot membership applies to the next block, while signers-from-block methods describe the certificate of the queried block itself.

Signer responses preserve the exact capitalized keys `Number`, `Hash`, `Author`, and `Committers`.
`Number` is a JSON number; `Committers` is an array of recovered validator addresses.
These keys must not be silently rewritten to Ethereum-style lowercase fields.

The configuration fields in this profile are:

| Fields | Unit or interpretation |
| --- | --- |
| `requestTimeout` | Milliseconds. |
| `blockPeriod`, `emptyBlockPeriod`, `allowedFutureBlockTime`, `maxRequestTimeout` | Seconds. |
| `proposerPolicy`, `epoch`, `validators` | Policy ID, vote-reset interval in blocks, and validator address list. |
| `gasLimit`, `elasticityMultiplier`, `baseFeeChangeDenominator` | Effective execution fee parameters at the queried height. |
| `minBaseFee`, `maxBaseFee` | Decimal JSON numbers in wei, or `null` when not configured. |

The different timeout units are intentional compatibility details.
Large decimal values require a JSON decoder that preserves integer precision.

### Local Voting Requests and Activity

`istanbul_candidates()` returns a map of candidate addresses to booleans, where `true` requests addition and `false` requests removal.
`istanbul_propose(address, authorize)` records local voting intent, and `istanbul_discard(address)` removes that local intent.
These mutating methods return no value and do not immediately change the canonical validator set.
[OIP-6](oip-6.md) defines the block votes and majority required for a membership change.

`istanbul_status(startBlock, endBlock)` returns `sealerActivity`, an address-to-count map, and `numBlocks`, a JSON number.
It counts block authors, not the validators participating in each block's commit certificate.
The interval is `[startBlock, endBlock)`, excludes genesis, and must end at or before the current head.
Both arguments must be supplied together, with `startBlock <= endBlock` and an explicit range of at most `86,400` blocks.
Use explicit nonnegative block numbers for this method.

With both arguments omitted, the interval is the preceding 64 blocks ending before the current head, shortened to exclude genesis when necessary.
An explicit start of zero is likewise normalized to one.
The result initializes validators from the end-height snapshot with zero counts, and also counts authors encountered in the interval even if they are absent from that snapshot.
Missing headers or request cancellation return an error rather than a partial activity report.

## Rationale

Preserving existing field casing, units, and missing-result behavior avoids breaking deployed consumers.
Separating Ethereum and Istanbul block resolution prevents clients from treating namespace-specific tags as interchangeable.
The fee-history weighting rule keeps filtered transactions from distorting the percentile population.

## Backwards Compatibility

This proposal records existing interfaces and enables no namespace or endpoint by itself.
Changing timeout units, signer field casing, percentile weights, or activity interval semantics requires an explicit compatibility decision.
Applications should use standard `eth` methods where appropriate and opt into Istanbul-specific methods when they need consensus information.

## Test Cases

| Case | Expected result |
| --- | --- |
| `eth` safe/finalized marker is missing | Report unavailable marker rather than substituting `latest`. |
| `istanbul_getValidators("safe")` | Do not resolve through the Ethereum safe marker. |
| Included receipt gas weights `30`, `70` with priority fees `2`, `8` | Percentiles `0`, `30`, `31`, `100` return `2`, `2`, `8`, `8`. |
| Add a filtered fee-cap-below-base-fee transaction to that population | Preserve those reward percentiles; still include its execution gas in the block utilization ratio. |
| No eligible transactions | Reward row contains zeroes. |
| Pending fee history requested for one block, with no pending block | Return no history after the one-block reduction. |
| `istanbul_status(10, 20)` | Count ten block authors, heights `10` through `19`. |
| A block has three committers | Increase only its author's activity count by one. |
| A local candidate request has not passed on-chain voting | Canonical validator membership remains unchanged. |

These are compatibility acceptance cases; live RPC behavior was not exercised for this proposal.

## Reference Implementation

Reference implementation: [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Ethereum block resolution](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/api_backend.go).
- [Fee history](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/gasprice/feehistory.go).
- [Istanbul API](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/api.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-14/verification.md).

## Implementation and Activation

No chain activation is required merely to document this interface.
Providers must verify their deployed client revision, namespace exposure, history retention, and transport limits before claiming this profile.
This proposal does not audit any deployed RPC endpoint.

## Security Considerations

Voting methods change local validator behavior and should be restricted to authorized operators.
Snapshot reconstruction and historical queries can be expensive, so endpoint limits remain necessary even for read-only methods.
An activity count is not proof of participation in every quorum, and a local membership result is not proof that the node is online or signing.
Clients must preserve integer precision and treat missing historical data separately from a confirmed empty result where the method allows that distinction.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
