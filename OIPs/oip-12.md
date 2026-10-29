---
oip: 12
title: eth Wire Protocol Profile
description: The eth/68 profile used by ONEchain peers for status exchange, block propagation, sidecar transport, and synchronization without a beacon chain.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Networking
created: 2026-10-28
---

# OIP-12: eth Wire Protocol Profile

## Abstract

This proposal specifies how ONEchain execution clients use the devp2p `eth` protocol.
ONEchain peers negotiate only `eth/68`, exchange real total difficulty in the Status handshake, and propagate blocks with `NewBlockHashes` and `NewBlock`, which upstream post-merge clients reject.
`NewBlock` messages and block bodies may carry an optional trailing list of blob sidecars.
Chain synchronization selects peers by total difficulty and uses no consensus-layer interface.
The fork identifier includes ONEchain fork timestamps, and discovery filtering by fork identifier is described as local policy.

## Motivation

Ethereum execution clients stopped propagating blocks and exchanging total difficulty after the transition to proof of stake, because a beacon chain distributes blocks and directs synchronization.
Upstream go-ethereum v1.16 sends a zero total difficulty in `eth/68` Status messages, disconnects peers that send `NewBlockHashes` or `NewBlock`, and prefers `eth/69`, which removes total difficulty from the handshake.

ONEchain has no beacon chain, as described in [OIP-4](oip-4.md).
Its execution clients must distribute blocks among themselves and choose synchronization targets without external guidance.
Independent implementations therefore need a shared profile of protocol versions, handshake fields, block propagation, and optional message elements.
Without it, a client that follows upstream defaults would disconnect ONEchain peers or never select them as synchronization targets.

## Specification

### Conventions and Scope

This profile applies to every ONEchain network that uses Istanbul consensus.
Message encodings not changed here follow the devp2p [`eth` protocol specification](https://github.com/ethereum/devp2p/blob/master/caps/eth.md) for version 68.
`TD` denotes total difficulty as defined by [OIP-4](oip-4.md), where `TD(B) = number(B) + 1`.
List notation `[a, b]` denotes an RLP list.

Block header and seal validity are defined by [OIP-5](oip-5.md).
The `istanbul` consensus subprotocol that runs alongside `eth` on the same connection is defined by [OIP-7](oip-7.md).
Validator peer admission, which can refuse a connection during the handshake, is outside this proposal.
[OIP-10](oip-10.md) defines sidecar contents, availability rules, and retention; this proposal defines how sidecars are carried.

### Protocol Version

Clients MUST offer the `eth` capability at version 68, which uses message codes `0x00` through `0x10`.
Clients MUST NOT offer `eth/69` or a later version on a ONEchain network.
Because devp2p selects the highest version that both peers offer, a single client offering `eth/69` would remove total difficulty and block propagation from its connections with other such clients.
A later proposal MAY define a ONEchain profile for a newer version.

Transaction announcement and retrieval messages are unchanged.
Typed transactions, including the fee-delegated type `0x07` of [OIP-2](oip-2.md), are carried as opaque [EIP-2718](https://eips.ethereum.org/EIPS/eip-2718) envelopes.

### Status Handshake

The Status message is the `eth/68` message:

```text
Status = [version, networkid, td, head, genesis, forkid]
```

The fields have the following values:

| Field | Value |
| --- | --- |
| `version` | `68`. |
| `networkid` | The network identifier. The reference presets use the chain ID: `612055` for ONEchain mainnet and `612044` for ZoneZero. |
| `td` | `TD` of the sender's current head block. Senders MUST NOT send zero in place of the actual value. |
| `head` | Hash of the sender's current head block. |
| `genesis` | Hash of the genesis block. |
| `forkid` | The [EIP-2124](https://eips.ethereum.org/EIPS/eip-2124) fork identifier described below. |

A receiver MUST disconnect the peer if `version` differs from the negotiated version, `networkid` or `genesis` differs from its own, or its fork identifier filter rejects `forkid`.
A receiver MUST also disconnect the peer if `td` has a bit length greater than 100.
The received `td` and `head` are the peer's initial advertised head and are used only for synchronization target selection.

### Fork Identifier

The fork identifier follows EIP-2124 over every fork activation field of the chain configuration.
This includes the upstream block-numbered and timestamp-scheduled forks and ONEchain fork timestamps such as `adventureTime`.
Activation values are sorted and deduplicated.
Block-numbered forks at block `0` and timestamp-scheduled forks at or before the genesis timestamp are excluded.

`terminalTotalDifficulty` and the block-numbered Istanbul `transitions` overrides are not fork activation fields and do not affect the fork identifier.

As a result, a ONEchain fork scheduled after genesis changes the fork identifier at its activation.
After that point, peers whose identifiers do not announce the fork are rejected by the EIP-2124 filter.
A fork activated at or before genesis, such as Adventure in the reference presets, does not appear in the identifier.

### Block Propagation

Clients MUST accept `NewBlockHashes` (`0x01`) and `NewBlock` (`0x07`) and MUST NOT disconnect a peer only for sending them.

```text
NewBlockHashes = [[hash, number], ...]
NewBlock       = [block, td] or [block, td, sidecars]
```

In `NewBlock`, `td` is the `TD` of `block`, calculated as the sender's `TD` of the parent plus the block's difficulty.
A receiver MUST disconnect the peer if `td` has a bit length greater than 100 or if any included sidecar names a block number or block hash different from `block`.
It MUST also disconnect the peer if a sidecar's numbers of blobs, commitments, and proofs differ.
The advertised `td` is not authenticated and serves only to update the peer's advertised head to the block's parent.

A client MUST validate a block header under Istanbul consensus rules before relaying the block.
It MUST NOT relay a block whose header fails that validation, including a header with a difficulty other than `1`.
It MUST NOT propagate a full block unless its withdrawals element is either absent with no withdrawals root or an empty list with the empty-list root.
It also MUST NOT propagate a full block whose sidecars fail the rules in [OIP-10](oip-10.md).

After validating the header, a client sends the full block to a subset of peers that are not known to have it.
After importing the block, it announces the block hash to the remaining peers that are not known to have it.
A block producer follows the same two steps for each new block it seals.
The reference client sends full blocks to `floor(sqrt(n))` of the `n` eligible peers; the subset size is local policy.

On receiving `NewBlockHashes`, a client retrieves unknown blocks with `GetBlockHeaders` and `GetBlockBodies`.
The reference client ignores announcements and blocks more than 7 blocks behind or 32 blocks ahead of its head, and discards propagated blocks until its initial synchronization completes; these limits are informative.

### Optional Sidecar Elements

A block body in `BlockBodies` is one of the following lists:

```text
body = [transactions, uncles]
     | [transactions, uncles, withdrawals]
     | [transactions, uncles, withdrawals, sidecars]
```

`NewBlock` carries the same `sidecars` list as an optional third element.
A sidecar list has the following encoding:

```text
sidecars = [sidecar, ...]
sidecar  = [[blobs, commitments, proofs], blockNumber, blockHash, txIndex, txHash]
```

| Field | Encoding |
| --- | --- |
| `blobs` | List of 131,072-byte strings. |
| `commitments` | List of 48-byte KZG commitments. |
| `proofs` | List of 48-byte KZG proofs. |
| `blockNumber` | Block number as an RLP integer. |
| `blockHash` | 32-byte hash of the block that includes the transaction. |
| `txIndex` | Index of the blob transaction in the block, as an RLP integer. |
| `txHash` | 32-byte hash of the blob transaction. |

The sidecar has no version element and carries only version-0 proofs as defined by [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844).

Senders MUST omit the `sidecars` element when a block has no sidecars, so ordinary messages keep the standard `eth/68` encoding.
A body that carries `sidecars` MUST include the `withdrawals` element before it.
Receivers MUST accept every form above and MUST treat an empty `sidecars` list the same as an omitted one.
A peer serving bodies includes the sidecars it has stored for each block and MAY omit sidecars it no longer retains.

Sidecars are not committed to by the block hash or any header field.
Which blocks must carry sidecars, how they are verified, and how long they are retained are outside this proposal.

### Synchronization

Clients select synchronization targets by advertised `TD`.
A peer is a target when its advertised `TD` is greater than the `TD` of the local head, and the reference client chooses the peer with the highest advertised `TD`.
The client then retrieves headers, bodies, and receipts from the target with `eth/68`, in full synchronization or in snap synchronization, which also retrieves state with the snap protocol.
Every retrieved header is validated as specified in [OIP-4](oip-4.md).

Clients MUST NOT require a consensus-layer client, the engine API, or beacon light synchronization to follow a ONEchain network.
The reference client does not register the engine API.

The following reference client values are informative:

- A synchronization cycle starts with at least 5 peers, or with 1 peer after a 10-second wait.
- When the best peer is only one `TD` unit ahead, the client waits 3 seconds and re-checks its own head before synchronizing.
- When serving snap storage ranges, the client processes at most 1,024 requested accounts.

### Discovery

This section is informative and describes local policy of the reference client.

Nodes publish an `eth` entry in their node record containing `[forkid]`, updated when the head changes, as in upstream clients.
Discovery v4 is enabled and discovery v5 is disabled by default.
Dial candidates must carry an `eth` entry accepted by the local fork identifier filter.

The reference client also removes nodes from its discovery routing tables when their `eth` entry is rejected by that filter.
It keeps nodes without an `eth` entry, rejects nodes whose entry cannot be decoded, and checks stored records again during revalidation because the result can change after a fork.
Other clients MAY apply different routing-table policies without affecting interoperability.

## Rationale

Without a beacon chain, block propagation over `eth` is the only general mechanism for distributing new blocks to non-validator nodes.
Retaining `eth/68` with its total-difficulty field and block propagation messages reuses the pre-merge behavior that upstream clients previously implemented.
`eth/69`, specified in [EIP-7642](https://eips.ethereum.org/EIPS/eip-7642), removes total difficulty from the Status message, and the reference client's `eth/69` handler set does not process `NewBlockHashes` or `NewBlock`.

Total difficulty on Istanbul chains is the block number plus one, so it reflects chain length rather than work.
It remains a convenient ordering for synchronization targets, but header validation and Istanbul finality, not advertised `TD`, establish validity.
The 100-bit limit bounds the cost of handling advertised values while leaving ample room for real chains.

Placing sidecars in a trailing optional element keeps ordinary messages byte-identical to `eth/68` and lets blocks without blobs remain compatible with decoders that do not know the element.
BNB Smart Chain's implementation of BEP-336 uses the same trailing-element placement for `NewBlock` and block bodies.

Including ONEchain forks in the fork identifier lets peers detect, at connection time, that another node has not scheduled a fork that the network has activated.

## Backwards Compatibility

This proposal records the existing networking behavior of the reference client and changes no message used by current ONEchain nodes.

Clients that implement only upstream post-merge `eth` behavior cannot participate.
They advertise a zero total difficulty and are never selected as synchronization targets, and they disconnect ONEchain peers that propagate blocks.

A decoder that does not know the optional `sidecars` element rejects a `NewBlock` message or block body that carries it, because the list has too many elements.
The reference client's transaction pool currently rejects blob transactions, so blocks on current networks carry no sidecars.
Before blob transactions are admitted on a network, every client on that network needs to accept the optional element.

## Test Cases

### Fork Identifiers

The following identifiers were computed with the reference client's fork identifier implementation and default network configurations.

| Network | Genesis hash | Genesis time | Initial identifier | After the next scheduled fork |
| --- | --- | --- | --- | --- |
| ONEchain mainnet | `0x675a5d7c97cc1be3bf061635d31206966ef7ae0205a45890a4bab931456a8348` | `1739496247` | `{hash: 0xc5b18145, next: 1780282800}` | `{hash: 0x3950beda, next: 0}` |
| ZoneZero | `0xcd8ce15999597691045f5f9675debfe4e0a7e5dca94b866e01df6b5b9d4263aa` | `1739496247` | `{hash: 0x7464a126, next: 1778814000}` | `{hash: 0xc529eb1f, next: 0}` |

Shanghai and Adventure at `0` are excluded, and forks scheduled at the same timestamp, such as Cancun and Prague, form one entry.
The RLP encoding of the mainnet identifier after that fork is `0xc6843950beda80`.

For a mainnet node whose head is at or after timestamp `1780282800`, the filter produces these results:

| Remote fork identifier | Result |
| --- | --- |
| `{0x3950beda, 0}` | Accepted. |
| `{0xc5b18145, 1780282800}` | Accepted; the remote has scheduled the fork and is still synchronizing. |
| `{0xc5b18145, 0}` | Rejected; the remote has not scheduled the fork. |
| `{0xc5b18145, 1780282801}` | Rejected; the remote scheduled a different fork time. |
| ZoneZero `{0xc529eb1f, 0}` | Rejected. |

For a mainnet node whose head is before that timestamp, `{0x3950beda, 0}` and `{0xc5b18145, 0}` are accepted, and an unknown hash such as `{0x01020304, 0}` is rejected.

### Handshake and Propagation

| Case | Expected result |
| --- | --- |
| Status with `td` of bit length 100 | Accepted. |
| Status with `td` of bit length 101 | Peer disconnected. |
| Status with a different `networkid` or `genesis` | Peer disconnected. |
| Capability negotiation with a peer offering `eth/69` and `eth/68` | `eth/68` is used. |
| `NewBlockHashes` for an unknown block within the distance limits | No disconnection; the block is retrieved by header and body requests. |
| `NewBlock` with two elements and a valid Istanbul header | Block relayed to a peer subset before import and announced after import. |
| `NewBlock` with a sidecar naming another block hash | Peer disconnected. |
| `NewBlock` whose header has difficulty `0` | Block neither relayed nor imported. |

### Body Encodings

| Body | RLP encoding |
| --- | --- |
| No transactions or uncles | `0xc2c0c0` |
| No transactions or uncles, empty withdrawals | `0xc3c0c0c0` |
| Empty withdrawals and one sidecar | `0xf84fc0c0c0f84af848c3c0c0c001a0010000000000000000000000000000000000000000000000000000000000000080a00200000000000000000000000000000000000000000000000000000000000000` |

The sidecar in the last case has no blobs, `blockNumber = 1`, `blockHash = 0x01` followed by 31 zero bytes, `txIndex = 0`, and `txHash = 0x02` followed by 31 zero bytes.
It tests encoding only and would not satisfy availability rules.
A decoder with only the three upstream body fields rejects that encoding with a "too many elements" error.

Reproducible client tests for the handshake and propagation cases remain pending.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Protocol versions, messages, and packets](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/protocol.go).
- [Status handshake](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/handshake.go).
- [Message handlers and body serving](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/handlers.go).
- [Block propagation and fetcher integration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/handler.go).
- [Synchronization target selection](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/sync.go).
- [Fork identifier](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/forkid/forkid.go).
- [Node record entry and discovery filters](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/discovery.go).

## Implementation and Activation

This profile describes the reference client at the revision above and schedules no network fork.
Changes to it require coordination among all node operators, because peers that disagree on the negotiated version or the optional elements cannot exchange blocks reliably.
In particular, adopting a newer `eth` version or admitting blob transactions requires every client on the affected network to support the new behavior before it is used.

## Security Considerations

Advertised total difficulty is not authenticated, and `TD` on Istanbul chains is easy to claim.
A peer can advertise a high value to become a synchronization target and then serve invalid or incomplete data.
Clients must validate every retrieved header and body, should penalize peers that fail to deliver the chain they advertised, and must not treat advertised `TD` as evidence of validity or finality.

Relaying a block only after its header passes Istanbul validation limits the amplification of invalid blocks through the network.
Sidecars are not committed by the block hash, so a relaying client must check them under the availability rules before propagating a full block.
The bit-length limit, the 10 MiB message size limit, and per-peer announcement limits bound the cost of malformed or excessive messages.

The fork identifier detects misconfiguration but is self-reported and does not authenticate a peer.
Discovery filtering reduces wasted connections to nodes on other chains but does not replace handshake checks.

## References

- [devp2p `eth` protocol specification](https://github.com/ethereum/devp2p/blob/master/caps/eth.md).
- [EIP-2124: Fork identifier for chain compatibility checks](https://eips.ethereum.org/EIPS/eip-2124).
- [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844).
- [EIP-7642: eth/69](https://eips.ethereum.org/EIPS/eip-7642).
- BEP-336 in the [BNB Chain BEPs repository](https://github.com/bnb-chain/BEPs).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
