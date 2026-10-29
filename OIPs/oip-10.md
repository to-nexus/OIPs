---
oip: 10
title: Blob Execution and Availability in Istanbul
description: EIP-4844 execution, sidecar verification, and transaction-admission limits on Istanbul chains.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-10: Blob Execution and Availability in Istanbul

## Abstract

This proposal documents the Istanbul integration of [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844) and [EIP-7516](https://eips.ethereum.org/EIPS/eip-7516).
It specifies the initial blob execution profile, sidecar availability checks before voting and import, and sidecar RPC behavior.
The reference client rejects public blob transaction admission through the Istanbul transaction pool even though its block-processing paths contain blob support.
This proposal preserves that restriction and does not activate a public blob service.

## Motivation

Blob support spans execution, block validity, consensus messages, storage, and RPC.
An opcode or transaction decoder alone does not establish an operational blob network.
Validators must obtain and validate sidecars before voting for a recent proposal, while historical synchronization must account for finite data retention.
Applications also need a clear distinction between retrievable sidecars and accepted transaction submissions.

## Specification

### Scope and Activation

This proposal covers Istanbul consensus with the initial Cancun blob schedule.
It adopts EIP-4844 transaction, commitment, and execution semantics except for the ONEchain differences stated below, and EIP-7516's `BLOBBASEFEE` instruction.
Subsequent blob schedules, fee-formula revisions, and alternative data-availability schemes require separate specifications.

The reference execution predicate is:

```text
CancunActive(n, t) = LondonActive(n) and CancunTime is configured and t >= CancunTime
```

An active, valid blob schedule must also be available in chain configuration.
Adventure activation alone does not activate these blob rules.
This proposal sets no network activation timestamp and makes no deployed-service claim.

### Execution and Headers

When the profile is active, EIP-4844 defines blob transaction type `0x03`, versioned blob hashes, `BLOBHASH` at `0x49`, and the point-evaluation precompile at address `0x0a`.
EIP-7516 defines `BLOBBASEFEE` at `0x4a`.
The opcode stack behavior, gas costs, precompile input/output, and cryptographic validation follow those EIPs.
Contracts can access versioned hashes, not the blob payload itself.

The initial default parameters are:

| Parameter | Value |
| --- | --- |
| Blob payload size | `131,072` bytes. |
| Blob gas per blob | `131,072`. |
| Target blobs per block | `3`. |
| Maximum blobs per block | `6`. |
| Minimum blob base fee | `1` wei per blob gas. |
| Blob base fee update fraction | `3,338,477`. |

The target, maximum, and update fraction come from the configured Cancun schedule; the table records reference defaults, not verified deployed values.
`blobGasUsed` and `excessBlobGas` must be present after activation.
`blobGasUsed` must be a multiple of the gas per blob, equal the total blob count in the body's transactions times that value, and not exceed the configured maximum.

For parent excess `E`, parent blob gas used `U`, and the child's configured target blob gas `T`:

```text
child.excessBlobGas = max(0, E + U - T)
```

A parent without blob fields contributes zero excess and zero usage.
The blob base fee uses EIP-4844's integer `fake_exponential` calculation with minimum price `1`, the child's excess, and the configured update fraction.
Blob gas is accounted separately from the ordinary execution gas limit and base fee.

Before activation, blob gas fields and sidecars are not permitted, and blob execution is not enabled.
For non-genesis Istanbul headers after activation, the withdrawal commitment is the empty withdrawal root and `parentBeaconBlockRoot` is the zero hash.
The withdrawal body is empty; these compatibility fields do not introduce a Beacon Chain or Ethereum validator withdrawals.

Blob transactions must have a destination, a nonempty list of valid version-`0x01` hashes, and a blob fee cap sufficient for the block's blob base fee.
Sender balance checks include the maximum blob-fee liability in addition to ordinary execution liability and value.
The actual blob charge is blob gas used times the blob base fee.
On Istanbul chains, that charge is credited to the configured fee beneficiary, falling back to the execution coinbase when no override is configured.
It is not burned as in Ethereum's EIP-4844 accounting.

### Public Transaction Admission

The reference transaction-pool validator rejects type `0x03` on an Istanbul chain even after the execution predicate is active.
The Istanbul-specific rejection wraps the unsupported-transaction-type error; earlier type, size, or fork checks may reject the request first.
Consumers must not infer consensus-level rejection from that pool error's wording.

Conversely, the presence of block-execution and availability code is not permission to bypass pool admission or evidence that public providers accept blob transactions.
Removing the restriction, changing transaction propagation, or promising blob submission support requires a separate reviewed change and operational validation.
[OIP-2](oip-2.md) wraps a dynamic-fee transaction and does not define a fee-delegated blob transaction.

### Sidecar Structure and Validation

Transactions stored in a block body must not embed their transaction-network sidecar wrapper.
The reference client carries sidecars separately as block metadata, one sidecar per blob transaction, in the same order as those transactions appear in the block.
Each sidecar identifies the block number and block hash, transaction hash, and transaction index, and carries corresponding arrays of blobs, commitments, and proofs.

For a block subject to availability verification, the client must check:

1. Sidecar count equals the number of blob transactions.
2. Each sidecar's block number and hash identify that block, and its transaction hash and index identify the corresponding transaction.
3. Blob, commitment, and proof counts each equal that transaction's versioned-hash count.
4. Each commitment's EIP-4844 versioned hash equals the corresponding transaction hash entry.
5. Every blob passes KZG blob-proof verification against its commitment and proof.
6. The total blob count does not exceed the configured per-block maximum.

An empty block may have no sidecars; a recent block with blob transactions may not omit them.
An otherwise valid execution payload does not excuse an invalid or missing required sidecar.

### Consensus and Historical Availability

The reference proposal verifier calls the data-availability check before a validator votes for a proposal.
Block import also performs availability checks.
[OIP-7](oip-7.md) defines the optional sidecar element carried by PRE-PREPARE and ROUND-CHANGE messages.
That element is outside the message's signed payload; the block's transaction commitments and the sidecar checks above provide the content binding.
A valid message signature alone is insufficient to accept it.

At the reference revision, the local availability window is `1,572,480` seconds, or `18.2` days, measured from the block timestamp against the verifying node's wall clock.
The historical branch is selected only when:

```text
block.timestamp + 1,572,480 < localUnixTime
```

For an older block, the reference client clears the attached sidecars and skips their availability verification.
At equality, it still verifies availability.
This historical exception does not bypass header, transaction, or state validation.
It does not establish permanent retention or guarantee that any particular peer can serve old blobs.
Local clocks and retention policy therefore affect data availability even when the immutable execution commitments agree.

### Sidecar RPC

The following methods expose locally available sidecars:

| Method | Arguments | Result |
| --- | --- | --- |
| `eth_getBlobSidecars` | Block number or hash selector, optional `fullBlob` | Array of sidecar objects, or `null` when the header/data cannot be retrieved. |
| `eth_getBlobSidecarByTxHash` | Transaction hash, optional `fullBlob` | Matching canonical transaction sidecar, or `null`. |

`fullBlob` defaults to `true`.
Each sidecar object contains `blockHash`, `blockNumber`, `txHash`, `txIndex`, and `blobSidecar`.
The number and index use hexadecimal quantities.
`blobSidecar` contains arrays named `blobs`, `commitments`, and `proofs`.

With `fullBlob: false`, each entry in `blobs` is only the first 32 bytes of the original blob.
It is not a blob hash or a substitute for the full payload when verifying a proof.
Commitments and proofs remain present in full.

The block method returns an empty array if its backend provides a non-null empty sidecar list; it returns `null` for a missing list or retrieval error.
The transaction method uses the canonical transaction index and does not search pending transactions.
Its missing block, absent sidecar, or retrieval-error paths return `null`.
Because these paths collapse into `null`, that result alone cannot prove that a known block never contained blobs.

## Rationale

Adopting the upstream execution and commitment formats allows reuse of existing encoders and cryptographic verification.
Checking sidecars before voting prevents validators from committing a recent block whose required data they cannot import.
The bounded historical check permits synchronization after local sidecar retention expires.
Documenting the pool restriction separately avoids overstating what imported execution code makes available to applications.

## Backwards Compatibility

This proposal changes neither pool admission nor the existing consensus message envelope.
Blocks before activation must retain their earlier field rules.
Clients must not assume Ethereum fee burning, unlimited blob history, or that a shortened RPC blob can be verified as full data.
Any change to the availability window, schedule, or admission policy requires an explicit compatibility review.

## Test Cases

| Case | Expected result |
| --- | --- |
| Pre-activation block contains sidecars or blob gas fields | Reject the incompatible content. |
| Active block omits a required blob gas field | Reject the header. |
| Parent excess `0`, usage `786,432`, target `393,216` | Child excess is `393,216`. |
| Active recent block has a missing, reordered, or mismatched sidecar | Reject availability verification before voting and import. |
| Commitment matches the versioned hash but the blob proof is invalid | Reject the sidecar. |
| Block age equals the availability window | Still require valid sidecars. |
| Block age exceeds the availability window | Clear sidecars and skip historical availability verification; retain ordinary block checks. |
| Otherwise valid type-`0x03` submission to the Istanbul pool | Reject public admission. |
| Blob RPC uses `fullBlob: false` | Return the first 32 payload bytes with full commitments and proofs. |
| Valid executed blob transaction in this profile | Credit the actual blob fee to the selected fee beneficiary. |

These are required compatibility cases; they are not claims of executed KZG, consensus, or live-service tests.

## Reference Implementation

Reference implementation: [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Blob header and fee rules](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go).
- [Availability validation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/data_availability.go).
- [Pool admission restriction](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go).
- [Sidecar RPC methods](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-10/verification.md).

## Implementation and Activation

Execution code, consensus availability checks, local storage, and RPC retrieval exist in the inspected revision.
The Istanbul pool rejection remains in place.
No deployed blob transaction, historical retention guarantee, provider readiness, or independent-client agreement was verified for this proposal.
Network operators must establish those facts before offering a blob service or changing the admission policy.

## Security Considerations

Availability is distinct from commitment correctness: a valid hash cannot recover a withheld payload.
Validators must validate recent sidecars before locking or committing proposals, including prepared proposals carried through round changes.
Clock skew can change which side of the historical window a node applies.
Large sidecars also require bounded message handling, storage, and RPC resource use.
Truncated RPC data and a `null` retrieval result are not cryptographic evidence about a blob's validity or historical existence.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
