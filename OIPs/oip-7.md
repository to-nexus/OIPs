---
oip: 7
title: Istanbul Consensus Protocol
description: The istanbul/100 devp2p subprotocol, its message encodings, and the validator message exchange used by Istanbul consensus.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Networking
created: 2026-10-28
---

# OIP-7: Istanbul Consensus Protocol

## Abstract

This proposal specifies the devp2p subprotocol that ONEchain validators use to agree on blocks with Istanbul consensus.
It defines the `istanbul/100` capability, the encodings of the PRE-PREPARE, PREPARE, COMMIT, and ROUND-CHANGE messages, message signing and authorization, relay among validators, and the validity and round rules that peers must follow to interoperate.
Block header contents, committed seal verification inside blocks, and the `eth` wire protocol are specified separately.
Local denial-of-service limits of the reference client are described as informative guidance.

## Motivation

ONEchain finalizes each block through a message exchange among the current validators before the block is distributed to other nodes.
The reference client derives this exchange from the QBFT implementation in [GoQuorum](https://github.com/ConsenSys/quorum), which evolved from Istanbul Byzantine fault tolerance ([EIP-650](https://eips.ethereum.org/EIPS/eip-650)).
ONEchain keeps the GoQuorum capability name, version, and message codes, but adds optional blob sidecar elements and additional validity rules.

An independent validator client must produce and accept byte-compatible messages, recover the same signers, and apply the same quorum, proposer, and round-change rules.
Matching only the capability name and message codes is not sufficient, so a shared specification is needed.

## Specification

### Conventions and Scope

`RLP(x)` denotes canonical Recursive Length Prefix encoding, `keccak256(x)` denotes Keccak-256, and `||` denotes byte concatenation.
Integers are encoded as RLP integers: big-endian without leading zero bytes, with zero encoded as the empty string `0x80`.

The *sequence* `s` is the number of the block being decided, and the *round* `r` starts at `0` for each sequence.
`V(s)` is the validator set for sequence `s`, as determined by Istanbul consensus from the chain up to block `s - 1`.
For `N = |V(s)|`, the quorum is `Q = ceil(2N / 3)` and the fault bound is `F = ceil(N / 3) - 1`.
A *validator address* is the Ethereum address derived from the secp256k1 public key of the node's devp2p identity.

This proposal does not define the following, which are linked where relevant:

- Block header and extra-data layout, block hash, committed-seal hash, and committed-seal validity inside blocks, in [OIP-5](oip-5.md).
- The `eth` wire protocol that carries finalized blocks to all nodes, in [OIP-12](oip-12.md).
- Blob sidecar contents and availability rules, defined by [OIP-10](oip-10.md).
- Validator peer admission.

### Capability and Message Codes

The subprotocol uses capability name `istanbul`, version `100`, and a message-code space of `22`.
Codes in this section are relative to the capability's devp2p code offset.

| Code | Message |
| --- | --- |
| `0x12` | PRE-PREPARE |
| `0x13` | PREPARE |
| `0x14` | COMMIT |
| `0x15` | ROUND-CHANGE |

Code `0x11` is reserved for the legacy Istanbul message wrapper.
Implementations MUST NOT send it, and receivers MUST NOT process its contents as a consensus message.
Implementations MUST NOT send other codes in the capability's space; receivers ignore them.

A peer offering `istanbul/100` MUST also run the `eth` protocol on the same connection.
The reference client starts consensus message handling only after the `eth` handshake registers the peer.

Each message's devp2p payload is the RLP item defined below, with no additional byte-string wrapper.
A message larger than `10,485,760` bytes is invalid, and the receiver MAY disconnect the sending peer.

### Message Encoding

```text
prepared     = [] | [preparedRound, preparedDigest]
signedRC     = [[sequence, round, prepared], signature]

PREPARE      = [[sequence, round, digest], signature]
COMMIT       = [[sequence, round, digest, commitSeal], signature]
ROUND-CHANGE = [signedRC, preparedBlock, prepareJustification, (sidecarElement)]
PRE-PREPARE  = [[[sequence, round, block], signature],
                [roundChangeJustification, prepareJustification],
                (sidecarElement)]
```

The fields are:

| Field | Encoding |
| --- | --- |
| `sequence`, `round`, `preparedRound` | RLP integers whose values MUST fit in 64 bits. |
| `digest`, `preparedDigest` | 32-byte block hash. |
| `block`, `preparedBlock` | The block encoding used by the `eth` protocol: header, transactions, uncles, and, when present, withdrawals. |
| `signature` | 65-byte secp256k1 signature `r || s || v`, with `v` equal to `0` or `1`. |
| `commitSeal` | Byte string holding the sender's committed seal, described below. |
| `prepareJustification` | List of complete PREPARE messages; the empty list when there are none. |
| `roundChangeJustification` | List of `signedRC` items, without prepared blocks or their justifications. |
| `sidecarElement` | Optional one-element list containing the blob sidecar list of the proposed or prepared block. |

`prepared` MUST be the empty list when the sender has no prepared block.
Otherwise it contains the round in which the sender became prepared, which may be `0`, and the prepared block's hash.

In ROUND-CHANGE, `preparedBlock` is the empty list `0xc0` when the sender has no prepared block.
When present, its hash MUST equal `preparedDigest`.
An empty `prepareJustification` is likewise encoded as `0xc0`.

`sidecarElement` is present only when the block in the message has blob sidecars.
Receivers MUST accept messages with and without it.
The sidecar encoding and its validity are outside this proposal.

`commitSeal` is a 65-byte secp256k1 signature of the committed-seal hash of the proposed block for the message's round, as defined by [OIP-5](oip-5.md).
The 32-byte hash is signed directly without further hashing.

### Signing and Authorization

The sender signs `keccak256(P)` with its devp2p identity key, where `P` is the signing payload for the message code:

```text
PRE-PREPARE:  P = RLP([0x12, [sequence, round, block]])
PREPARE:      P = RLP([0x13, [sequence, round, digest]])
COMMIT:       P = RLP([0x14, [sequence, round, digest, commitSeal]])
ROUND-CHANGE: P = RLP([0x15, [sequence, round, prepared]])
```

The *source* of a message is the address recovered from its signature.
Each `signedRC` item and each PREPARE in a justification has its own signature, recovered with codes `0x15` and `0x13`.
The signature does not cover justifications, `preparedBlock`, or `sidecarElement`.
`preparedBlock` is bound to the signed payload through `preparedDigest`.

A receiver MUST discard a message whose signature cannot be recovered or whose source is not in `V(s_local)`, where `s_local` is the receiver's current sequence.
The same rule applies to every justification entry.
The peer that delivered a message need not be its source, because validators relay each other's messages.

### Transport and Relay

A validator sends each message it creates to every connected peer whose validator address is in its current validator set, excluding itself.
It also processes its own message locally.

After successfully processing a message, a validator MUST relay the identical payload to the same set of peers.
It SHOULD skip peers already known to have the message.
Messages that fail processing MUST NOT be relayed.

A receiver MUST ignore consensus messages from a connected peer whose validator address is not in the validator set for the block after its current head.
The reference client drops such messages without disconnecting the peer, because a newly elected validator can send messages before the receiver imports the block that elects it.
Non-validator nodes neither receive nor relay consensus messages; they obtain finalized blocks through the `eth` protocol.

### Message Validity

Before processing a message, a receiver MUST discard it if decoding fails, its source is unauthorized, or `sequence` or `round` does not fit in 64 bits.
Let `(s, r)` be the receiver's current sequence and round.
Views are ordered first by sequence, then by round.

For PRE-PREPARE, PREPARE, and COMMIT:

- A message with a view below `(s, r)` is discarded.
- A message with a view above `(s, r)` is a future message, which a receiver MAY buffer and process when its view is reached.
- At view `(s, r)`, the receiver accepts PRE-PREPARE only before accepting a proposal, PREPARE only after accepting a proposal and before becoming prepared, and COMMIT only after becoming prepared and before committing.
  An earlier message type is discarded, a later message type is a future message, and all three are discarded after committing.

A ROUND-CHANGE with sequence `s` and round `r` or higher is processed at any point in the round.
A ROUND-CHANGE with a lower view is discarded, and one with a higher sequence is a future message.

A PRE-PREPARE is valid only if all of the following hold:

1. Its source is the proposer for `(s, round)`.
2. The proposed block's number equals `sequence`, and the block is valid for sequence `s`.
3. In round `0`, both justification lists are empty.
4. In a round greater than `0`, it carries a justification as specified below.

A receiver that finds the proposed block's timestamp in the future MAY defer the PRE-PREPARE until that time.

A PREPARE or COMMIT is valid only if its digest equals the hash of the proposal accepted in the current round.
The `commitSeal` is checked when the committed block's header is verified.

Each justification list MUST contain at most `N` entries.
Within each list, every entry MUST have sequence `s` and a distinct source in `V(s)`.

A round-`r'` PRE-PREPARE justification, for `r' > 0`, MUST satisfy the following:

1. `roundChangeJustification` holds at least `Q` entries, each with round `r'`.
2. `prepareJustification` is either empty or holds at least `Q` PREPAREs, all with one round `pr` and a digest equal to the proposed block's hash.
3. If `prepareJustification` is empty, at least `Q` round-change entries carry an empty `prepared`.
   A `prepared` value with round `0` and a zero digest also counts as empty.
4. Otherwise, at least `Q` round-change entries carry an empty `prepared` or a prepared round at most `pr`.
   At least one of those entries carries prepared round `pr` and the proposed block's hash.

ROUND-CHANGE carries the sender's prepared certificate.

- If `prepareJustification` is non-empty, `prepared` and `preparedBlock` MUST also be present.
- When all three are present, the prepared block's number MUST equal `sequence`.
- `prepareJustification` MUST then hold at least `Q` PREPAREs from distinct validators.
- A ROUND-CHANGE that fails these checks is discarded.

The certificate counts as a prepared value only if every PREPARE has round `preparedRound` and digest `preparedDigest`.
Otherwise the receiver still counts the message as a round change but ignores its prepared value.

### Round Flow

#### Proposer Selection

Validators in `V(s)` are ordered by ascending byte-wise comparison of their 20-byte addresses.
Let `L` be the coinbase of block `s - 1`, or the zero address when `s = 1`, and let `i` be the index of `L` in the ordered set, or `0` when `L` is not a member.
The proposer for `(s, r)` is the validator at the following index:

| `proposerPolicy` | Index |
| --- | --- |
| `0`, round-robin | `r mod N` when `L` is the zero address; otherwise `(i + r + 1) mod N`. |
| `1`, sticky | `r mod N` when `L` is the zero address; otherwise `(i + r) mod N`. |

The reference presets use policy `0`.

#### Normal Case

When block `s - 1` becomes the head, a validator moves to sequence `s` and round `0`.

1. When the validator's block producer supplies a proposal for `s`, the validator starts the round timer.
   If it is the proposer for `(s, 0)`, it broadcasts a PRE-PREPARE without justifications.
2. On accepting a valid PRE-PREPARE, a validator restarts the round timer and broadcasts a PREPARE with the proposal hash.
3. On holding valid PREPAREs from at least `Q` distinct validators, a validator becomes prepared.
   It records the round, the block, and those PREPAREs as its prepared certificate, then broadcasts a COMMIT with its committed seal.
4. On holding valid COMMITs from at least `Q` distinct validators, a validator assembles the committed seals into the block as specified by [OIP-5](oip-5.md) and imports it.
   If the assembled block fails verification, the validator broadcasts a ROUND-CHANGE for round `r + 1`.

#### Round Change

When the timer of round `r` expires, a validator moves to round `r + 1`, keeps any prepared certificate, starts the new round's timer, and broadcasts a ROUND-CHANGE for `r + 1`.

When the number of distinct validators that sent ROUND-CHANGEs for rounds above `r` reaches `F + 1`, a validator moves to the smallest such round.
It then broadcasts its own ROUND-CHANGE for that round.

A validator holding ROUND-CHANGEs for its current round `r > 0` from at least `Q` distinct validators proposes again if it is the proposer for `(s, r)` and has not yet sent a PRE-PREPARE in round `r`.

- If any of those ROUND-CHANGEs carries a valid prepared certificate, the proposal is the block with the highest prepared round, and `prepareJustification` is that certificate.
- Otherwise, the proposal is the validator's own pending block, and `prepareJustification` is empty.
- `roundChangeJustification` contains the signed payloads of the ROUND-CHANGEs held for round `r`.

#### Timeouts

The timer of round `r` lasts `T(r) = min(B * 2^r, M)` when `M > 0`, and `B * 2^r` otherwise.
`B` is the configured `requesttimeoutseconds`, or 10 seconds when it is unset, and `M` is `maxRequestTimeoutSeconds`.
Both take the values of the latest Istanbul transition at or below sequence `s`, if any.
The mainnet and ZoneZero presets use `B = 5` seconds and `M = 60` seconds.

#### Invalid Blocks

A validator records blocks that fail verification or import as bad blocks.
It MUST NOT propose or re-propose a block it has recorded as bad, and it omits such a block from its own ROUND-CHANGE.
When evaluating a justification, it MAY treat a round-change entry whose prepared digest identifies a recorded bad block as one with an empty `prepared`.

### Informative Local Limits

The reference client applies the following local limits.
They are not interoperability requirements, but implementations SHOULD bound comparable resources without discarding messages that honest validators need for progress.

| Limit | Reference behavior |
| --- | --- |
| Far-future messages | A message with sequence above `s + 1` is dropped, and so is a non-ROUND-CHANGE message for sequence `s` with round above `r + 12`. The drop is removed from the duplicate cache so a later relay can deliver the message. |
| Future-message buffer | At most 128 messages and 32 MiB per source, replayed in view order when the state advances. |
| Future ROUND-CHANGEs | For each validator, only the ROUND-CHANGE with the highest future round is retained. |
| Per-peer rate | 100 messages per second with a burst of 200, and 16 MiB per second with a burst of 20 MiB; excess traffic is delayed rather than dropped. |
| Duplicate suppression | Payloads already seen, identified by Keccak-256 of their RLP byte-string encoding, are not processed again. |

## Rationale

A separate subprotocol keeps consensus traffic among validators while finalized blocks reach every node through the `eth` protocol.
Keeping the GoQuorum capability name, version, and message codes preserves continuity with the implementation from which the reference client is derived.

Each signature covers only its message's core fields.
Justification entries are separately signed, the prepared block is bound through its digest, and blob sidecars are validated against the block's transactions.
Appending sidecars as an optional trailing element lets receivers decode messages for blocks without blob data unchanged.

Relaying every successfully processed message among validators lets messages reach validators that lack a direct connection.
Silently dropping messages from non-validator peers avoids disconnecting validators that have just joined the set.

Byte-wise address ordering is independent of the textual address form.
Ordering by checksummed text can differ, because uppercase hexadecimal letters sort before lowercase ones; see [Test Cases](#test-cases).

Justification lists are bounded by `N` because each validator contributes at most one entry.
Rejecting unused justifications and bounding their length limits signature recovery work for each message.

Treating a known-invalid prepared block as unprepared lets a round proceed with a new proposal instead of repeatedly re-proposing a block that honest validators reject.

## Backwards Compatibility

This proposal records the protocol implemented by the reference client and changes no message or rule.

A client implementing only the upstream QBFT encoding negotiates the same capability.
It can decode messages without sidecar elements, but it does not implement ONEchain's additional validity rules.
Validators on one network must therefore run implementations of this specification.

The legacy `0x11` wrapper used by earlier Istanbul versions is not processed.
Any change to message encodings, codes, quorum, or proposer selection requires coordinated deployment among validators and a new capability version where the encoding changes.

## Test Cases

### Message Vectors

The vectors use the publicly known secp256k1 test key `0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318`, whose address is `0x2c7536E3605D9C16a7a3D7b1898e529396a65c23`.
This key must never be used on a live network.

PREPARE with sequence `1`, round `0`, and digest `0x11` repeated 32 times:

```text
P          = 0xe513e30180a01111111111111111111111111111111111111111111111111111111111111111
keccak256  = 0x611bb7151a72a3d81074f3f6203e5743710670e22b389bb4e1939bb07aa83557
signature  = 0xc9a4fb0bb46b279871dff3f01ea2df3453ae098b99432f1d60e24c85d45f196339bab83d9e9009023c3fcd2134636c3a1cd63ba332ad4c268b737146c9a3023801
payload    = 0xf867e30180a01111111111111111111111111111111111111111111111111111111111111111b841c9a4fb0bb46b279871dff3f01ea2df3453ae098b99432f1d60e24c85d45f196339bab83d9e9009023c3fcd2134636c3a1cd63ba332ad4c268b737146c9a3023801
```

ROUND-CHANGE with sequence `1`, round `1`, and no prepared block:

```text
P          = 0xc515c30101c0
keccak256  = 0x834d3ecc779a1fe0ecb76fde2b3c50a8d549fb838f4b5469ad0a52565c94b3ce
signature  = 0xcaf6c11ba40dd98b01d1d7242e406cfe21fb7f4e782a80552119800a700a9b431683f1c507191a2d00b00589904e9894eb353c4dd60c8fc4da7894f9f307a7ec00
payload    = 0xf84bf847c30101c0b841caf6c11ba40dd98b01d1d7242e406cfe21fb7f4e782a80552119800a700a9b431683f1c507191a2d00b00589904e9894eb353c4dd60c8fc4da7894f9f307a7ec00c0c0
```

Decoding each payload with the reference client and recovering the signer over `P` yields the test key's address.

### Quorum and Proposer Cases

| `N` | `Q` | `F` |
| --- | --- | --- |
| 1 | 1 | 0 |
| 4 | 3 | 1 |
| 7 | 5 | 2 |
| 21 | 14 | 6 |

For four validators `A < B < C < D` in byte order under policy `0`:

| Previous block's coinbase | Round | Proposer |
| --- | --- | --- |
| Zero address (`s = 1`) | `0` | `A` |
| `B` | `0` | `C` |
| `B` | `1` | `D` |
| `B` | `3` | `B` |
| Not in the set | `0` | `B` |

For the addresses `0xab00000000000000000000000000000000000000` and `0xAC00000000000000000000000000000000000000`, byte order places `0xab…` first, while comparison of the checksummed strings places `0xAC…` first.
Proposer selection MUST use the byte order.

### Validity Cases

Unless stated otherwise, the receiver is a validator at sequence `s`, round `r`, and the message is otherwise valid.

| Case | Expected result |
| --- | --- |
| Valid signature, but the source is not in `V(s)` | Discarded and not relayed. |
| Message delivered by a peer whose address is not in the next block's validator set | Ignored; the peer is not disconnected. |
| Message delivered by a validator peer but signed by another validator | Processed with the signer as source. |
| PRE-PREPARE whose source is not the proposer for `(s, r)` | Discarded. |
| Round-`0` PRE-PREPARE carrying any justification entry | Discarded. |
| Round-`r'` PRE-PREPARE with `Q - 1` round-change entries | Discarded. |
| PRE-PREPARE with two round-change entries from the same validator | Discarded. |
| Any justification list with `N + 1` entries | Discarded. |
| ROUND-CHANGE with a non-empty `prepareJustification` but an empty `prepared` | Discarded. |
| ROUND-CHANGE whose `preparedBlock` hash differs from `preparedDigest` | Fails decoding; discarded. |
| PREPARE with a digest different from the accepted proposal | Discarded. |
| PREPARE for `(s, r)` received before the PRE-PREPARE | Buffered and processed after the PRE-PREPARE is accepted. |
| Message with `sequence = 2^64` | Discarded. |
| Message payload of `10,485,761` bytes | Discarded; the peer may be disconnected. |
| Message with code `0x11` | Not processed as a consensus message. |

Reproducible client tests for the validity cases remain pending.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Capability registration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/backend_istanbul.go) and [subprotocol handler](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/handler_istanbul.go).
- [Message encodings](https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/protocols).
- [Peer filtering and relay](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/handler.go) and [gossip and signing](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/backend.go).
- [Message handling and justification checks](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/handler.go), [view and buffer rules](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/backlog.go), and [justification predicates](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/justification.go).
- [Round state and timers](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/core.go) and [round changes](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/roundchange.go).
- [Quorum and proposer selection](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/validator/default.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-7/verification.md).

## Implementation and Activation

The reference client uses this protocol on every Istanbul network from genesis.

This specification records existing behavior and schedules no new fork.
A second implementation requires validator coordination and interoperability testing against the reference client before joining a network.

## Security Considerations

Message authenticity rests on the source signature and validator membership, not on the identity of the delivering peer.
Implementations must recover and authorize every signature, including each justification entry, before counting a message.

With `Q = ceil(2N / 3)`, any two quorums share at least `ceil(N / 3) = F + 1` validators, so at least one honest validator is in both when at most `F` validators are faulty.
Safety across round changes depends on proposers honoring prepared certificates through the justification rules.

Signing payloads contain no chain identifier.
A ROUND-CHANGE without a prepared block, for example, is valid on any network where the same key is a validator at the same sequence.
Validator node keys must not be shared across networks.

`sidecarElement`, `preparedBlock`, and justification lists are not covered by the message signature and can be large.
Receivers must bound message size and justification length before performing expensive verification, and must validate unsigned content before relying on it.

Bad-block records are local state.
Validators that disagree about whether a block is invalid can evaluate the same justification differently, so block validation must be deterministic across implementations.

## References

- [EIP-650: Istanbul Byzantine Fault Tolerance](https://eips.ethereum.org/EIPS/eip-650).
- [GoQuorum](https://github.com/ConsenSys/quorum).
- [The RLPx Transport Protocol](https://github.com/ethereum/devp2p/blob/master/rlpx.md).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
