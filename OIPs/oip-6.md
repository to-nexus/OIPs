---
oip: 6
title: Istanbul QBFT Consensus
description: Validator authorization, quorum certificates, round changes, and header voting of Istanbul consensus.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-6: Istanbul QBFT Consensus

## Abstract

This proposal specifies ONEchain's Istanbul QBFT consensus.
It defines the validator set that authorizes a block, quorum certificates, proposer and round rules, and changes to validator membership through header votes.
It uses the Istanbul digest prefix and individual secp256k1 signatures.

## Motivation

An independent client must derive the same validator set and verify the same certificate before accepting a block.
Transport compatibility and decodable extra-data alone do not establish block validity.
Validator election also uses a different threshold from block commitment, which must be specified explicitly.

## Specification

### Scope and Related Specifications

Istanbul consensus uses ECDSA validator addresses, individual committed seals, and header-vote membership changes.
It introduces no new activation or validator-selection mechanism.
The following proposals supply related details:

- [OIP-5](oip-5.md), for the header fields, extra-data layout, block hash, and committed seals.
- [OIP-7](oip-7.md), for the message exchange and round rules.
- [OIP-8](oip-8.md), for proposer authentication and the digest suffix.
- [OIP-9](oip-9.md), for execution gas limits and base fees.
- [OIP-4](oip-4.md), for the execution-engine boundary.

`K` denotes Keccak-256, and `RLP` denotes canonical Recursive Length Prefix encoding.

### Validator Set and Quorum

For block number `n > 0`, let `V(n)` be the validator snapshot obtained after applying its parent.
Every proposer, message authorization check, and committed seal for block `n` uses this set.
Membership changes carried by block `n` first affect block `n + 1`.

At genesis, a nonempty configured validator list supplies the initial set; otherwise the list comes from genesis extra-data.
Validator addresses are ordered by their raw 20-byte values, not by checksummed address strings.
A usable configuration requires a nonempty validator set and a consistent genesis across participants.

For `N = |V(n)|`, define:

```text
quorum Q = ceil(2 * N / 3)
fault bound F = ceil(N / 3) - 1
```

Only distinct members of `V(n)` count toward a quorum.
Do not replace `Q` with `2F + 1` for arbitrary validator counts.

### Header and Certificate

A non-genesis block must identify a known parent at height `n - 1`, use difficulty `1`, and contain no uncles.
Its timestamp must be at least the parent timestamp plus the configured block period at height `n`.
The reference client also applies its configured local future-time allowance.
The header's `coinbase` identifies an authorized validator and must agree with the recovered random-reveal signer.
Its `mixDigest` is the 16-byte Istanbul prefix followed by the reveal-derived suffix specified in [OIP-8](oip-8.md).

The extra-data produced by Istanbul consensus is:

```text
RLP([vanity, validators, vote, round, committedSeals, randomReveal])
```

`round` fits in 32 bits; each committed seal and the reveal is a 65-byte recoverable secp256k1 signature.
Producers write the sorted active validator list in `validators`.
The imported list does not replace the parent snapshot: the reference verifier does not independently compare this field with the active set outside genesis initialization.
Likewise, producers normally use 32 vanity bytes, but the reference verifier does not require that length.

Let `H[r]` be a copy of the header with the extra-data round set to `r` and committed seals cleared.
For this six-element extra-data:

```text
blockHash(H) = K(RLP(H[0]))
sealHash(H, r) = K(RLP(H[r]))
```

The block hash excludes the committed seals and the actual round.
All other header fields, including the reveal and vote, remain committed.
Each committed seal signs `sealHash(H, extra.round)` directly, without hashing that 32-byte digest a second time.

Final header verification must recover every seal successfully, reject unauthorized or duplicate signers, and require at least `Q` distinct validators.
A proposal exchanged before commitment has no completed quorum certificate; final block acceptance must not reuse that relaxed proposal check.
The message sender's signature and the committed seal are separate signatures with separate signing inputs.

### Proposals and Round Changes

Each sequence decides one block height, beginning at round `0`.
For a last proposer at index `j` in the sorted validator set, round `r` selects:

| Policy | Selected index |
| --- | --- |
| Round robin, ID `0` | `(j + r + 1) mod N` |
| Sticky, ID `1` | `(j + r) mod N` |

With an empty last-proposer address, both policies select `r mod N`.
If a nonempty last proposer is no longer in the set, the reference selection function uses `j = 0`.

The designated proposer broadcasts a PRE-PREPARE for the current sequence and round.
Validators verify its source, block number, proposal validity, and any round-change justification before preparing it.
A quorum of matching PREPARE messages establishes a prepared value; a quorum of matching COMMIT messages provides the certificate used to finalize the proposal.
At final block verification, the certificate must satisfy the committed-seal checks above.

Timeouts initiate a ROUND-CHANGE, and `F + 1` messages for higher rounds allow a validator to advance toward a higher round.
A new proposer requires a quorum of round-change messages for its target round.
Every entry in that justification must name the target round of the enclosing PRE-PREPARE; a certificate for another target round is invalid even when the block digest matches.
A prepared certificate may come from an older round and must not be rejected merely because its round differs from the target round.

Justification validation must check distinct authorized sources, sequence, signatures, and matching prepared digests and rounds.
With a prepared value, the proposer must preserve the highest prepared value supported by the valid justification; without one, it may propose a new valid block.
The detailed certificate selection and treatment of invalid prepared values follow [OIP-7](oip-7.md).
Local timeout lengths and buffering limits do not replace certificate validation or alter the block hash.

### Validator Votes

The extra-data vote is empty for no explicit vote, or contains `[recipient, voteType]`:

| `voteType` | Meaning |
| --- | --- |
| `0xff` | Authorize the recipient as a validator. |
| `0x00` | Remove the recipient from the validator set. |

Other vote types are invalid when applying the header to the snapshot.
The vote belongs to the block author, whose authorization is checked against the parent snapshot.
Each author has at most one counted vote for a given recipient; a new vote for that recipient first removes the author's preceding vote.
Only adding a nonmember or removing an existing member is a meaningful vote.

After counting the current vote, its recipient changes membership if its tally is strictly greater than `floor(N / 2)` for the current snapshot.
This is a strict-majority election rule, not the block commitment quorum.
The membership change clears all votes about that recipient.
Removing a validator also removes votes that validator cast about other recipients and adjusts their tallies.
The reference transition evaluates the current recipient; changing the set size does not automatically execute every other pending tally.

At a block whose number is a multiple of the configured positive `epoch`, pending votes and tallies are cleared before applying that block's vote.
The active validator set is retained.
An epoch value of zero disables this periodic vote reset.

Local candidate requests made through the RPC interface in [OIP-14](oip-14.md) express voting intent only.
They change membership only after inclusion in blocks and passage of the on-chain voting threshold.

## Rationale

Using the parent snapshot prevents a newly elected validator from authorizing the block that elects it.
Distinct-signer checks prevent repeated signatures from manufacturing a quorum.
Separating the round-independent block identity from the round-bound committed seal allows a prepared block to survive a round change without reusing its commit certificate for a different round.
Explicit voting rules allow membership to be reconstructed from genesis and canonical headers.

## Backwards Compatibility

This proposal records existing Istanbul consensus behavior without changing its wire format or activation schedule.
Applying a different sort order, quorum formula, hash filter, or snapshot timing can split consensus.
Genesis validator lists, proposer policy, epoch, and block-period transitions must match the network configuration used for replay.

## Test Cases

| Case | Expected result |
| --- | --- |
| Validator counts `4`, `5`, `6`, `7` | Commitment quorums `3`, `4`, `4`, `5`. |
| A repeated signer or a nonmember among committed seals | Reject the certificate even if its list length reaches quorum. |
| Change only the round or committed seals | Preserve block hash; a changed round changes the seal hash. |
| A round-change justification for round `4` attached to a round-`5` PRE-PREPARE | Reject the target-round mismatch. |
| Round-`5` justification carrying a valid prepared certificate from round `2` | Permit the older prepared round if all justification rules hold. |
| Five validators voting on membership | Three votes pass, while block commitment still requires four seals. |
| A block elects a new validator | Verify that block with the old set; use the new set for the next block. |
| One author repeats a vote for the same recipient | Count at most one vote from that author. |
| Epoch boundary with pending votes | Clear pending votes, retain membership, then process the current vote. |

These are acceptance criteria, not a report of executed consensus or multi-node tests.

## Reference Implementation

Reference implementation: [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Header and seal verification](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Snapshot derivation and voting](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go).
- [QBFT state machine](https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-6/verification.md).

## Implementation and Activation

[OIP-17](oip-17.md) references this proposal as an inherited consensus baseline.
This proposal assigns no activation height, timestamp, minimum release, or new validator set.
Historical replay, interoperability, and deployed configuration verification remain required before claiming network-wide conformance.

## Security Considerations

Safety depends on the quorum's honest intersection and validators not signing conflicting values in violation of the protocol.
Progress additionally depends on enough reachable validators and suitable timing conditions.
A quorum certificate proves agreement under these assumptions, not correctness of an unverified execution result.

Validator voting grants the current set administrative control over future membership.
Unsafe removals or unavailable additions can halt progress.
Neither membership voting nor a valid message signature removes the need to verify the full block and its final certificate.
Random-reveal unpredictability has separate limits described in [OIP-8](oip-8.md).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
