---
oip: 5
title: Istanbul Block Format
description: Header fields, extra-data encoding, block hash, and committed seal format of ONEchain Istanbul blocks.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-5: Istanbul Block Format

## Abstract

This proposal specifies the block header format that ONEchain's Istanbul consensus uses.
It defines the rules for Istanbul-specific header fields and the RLP layout of the extra-data field.
It defines the block hash and the commit seal hash, which exclude the committed seals and the round.
It also specifies the ECDSA committed seals that finalize a block.

## Motivation

Istanbul blocks carry consensus data in the header extra-data field and use a block hash that differs from Ethereum's hash of the full header.
Clients, light clients, bridges, and indexers must agree on how this field is encoded, which parts are covered by the block hash, and what a committed seal signs.
Without a shared definition, independent implementations derive different block hashes or accept different sets of committed seals.

## Specification

### Conventions and Scope

An *Istanbul chain* is defined in [OIP-4](oip-4.md).
For a header `H`, let `n` be its number, `t` its timestamp, and `P` its parent header.
`V` denotes the validator set in effect after `P`, ordered ascending by the bytes of each validator address, and `N = |V|`.
`Q = ceil(2N / 3)` denotes the quorum size.
`RLP(x)` denotes canonical Recursive Length Prefix encoding, and `keccak256` denotes Keccak-256.

Related specifications define the following behavior:

- How `V` evolves through validator voting, in [OIP-6](oip-6.md).
- The random reveal signature and the last 16 bytes of `mixDigest`, in [OIP-8](oip-8.md).
- Gas limit and base fee rules, in [OIP-9](oip-9.md).
- Consensus messages, proposer selection, and round flow, defined in [OIP-7](oip-7.md).
- Block propagation, defined in [OIP-12](oip-12.md).

### Header Fields

Istanbul headers use the Ethereum header fields and their RLP encoding.
The following rules apply to every header with `n >= 1`:

| Field | Requirement |
| --- | --- |
| `difficulty` | MUST be `1`, as specified in [OIP-4](oip-4.md). |
| `uncleHash` | MUST be `keccak256(RLP([]))`, and the block MUST NOT contain uncles. |
| `coinbase` | The address of the proposing validator. It MUST be a member of `V`. |
| `nonce` | Producers MUST set it to eight zero bytes. |
| `timestamp` | MUST satisfy `t >= P.timestamp + blockPeriod`, where `blockPeriod` is the configured Istanbul block period at `n`, including transitions. |
| `mixDigest` | The first 16 bytes MUST be the Istanbul prefix. The last 16 bytes are defined by [OIP-8](oip-8.md). |
| `extraData` | MUST decode as Istanbul extra-data under [Extra-Data Encoding](#extra-data-encoding). |

The Istanbul prefix is the ASCII string:

```text
"Cross Istanbul. " = 0x43726f737320497374616e62756c2e20
```

Clients SHOULD defer, rather than reject, a header whose timestamp is ahead of their local clock.
The reference client does not check `nonce` on import; the nonce value is nevertheless part of the block hash.
The `coinbase` membership check does not require the proposer scheduled for the block's round; proposer selection is defined in [OIP-7](oip-7.md).

Fields introduced by execution upgrades follow these rules for Istanbul headers:

- Before Cancun, `blobGasUsed`, `excessBlobGas`, and `parentBeaconRoot` MUST be absent, and `withdrawalsHash` MUST be absent for `n >= 1`.
- From Cancun, `withdrawalsHash` MUST equal the root of an empty withdrawals list, and `parentBeaconRoot` MUST be 32 zero bytes.
- From Prague, `requestsHash` MUST be present.

The genesis header MUST satisfy the `difficulty`, `uncleHash`, and execution-upgrade field rules, MUST use the Istanbul `mixDigest` prefix, and MUST have decodable extra-data.
Genesis is exempt from the parent, timestamp, `coinbase`, random reveal, and seal rules.

### Extra-Data Encoding

The extra-data field is the RLP encoding of a list with six elements:

```text
extraData = RLP([vanity, validators, vote, round, committedSeals, randomReveal])
```

| Element          | RLP type                | Content                                                                                                                         |
| ---------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `vanity`         | Byte string             | Arbitrary producer data, normally 32 bytes. Its content and length are not validated.                                           |
| `validators`     | List of 20-byte strings | The addresses of `V` in ascending byte order.                                                                                   |
| `vote`           | List                    | Either the empty list `0xc0`, meaning no vote, or `[recipient, voteType]` with a 20-byte `recipient` and an integer `voteType`. |
| `round`          | Integer                 | The consensus round at which the block was committed, at most `2^32 - 1`.                                                       |
| `committedSeals` | List of byte strings    | At least one 65-byte committed seal, as specified in [Committed Seals](#committed-seals).                                       |
| `randomReveal`   | Byte string             | The proposer's 65-byte secp256k1 random reveal signature, defined by [OIP-8](oip-8.md).                                         |

A list with any other number of elements is invalid.

Validation does not check `validators`, except that genesis extra-data supplies the initial validator set when the chain configuration lists none.

`voteType` MUST be `0x00`, a vote to remove `recipient`, or `0xff`, a vote to add it.
Vote tallying is defined by [OIP-6](oip-6.md).
The reference client detects an invalid `voteType` when it applies the vote while deriving the validator set for a later block.

### Block Hash and Commit Seal Hash

For a header `H` whose `mixDigest` begins with the Istanbul prefix, define the filtered header `F(H, r)` as a copy of `H` whose extra-data is replaced by:

```text
RLP([vanity, validators, vote, r, [], randomReveal])
```

All other header fields, including `coinbase`, `nonce`, and `mixDigest`, are unchanged.
The block hash and the commit seal hash for round `r` are:

```text
blockHash(H)    = keccak256(RLP(F(H, 0)))
sealHash(H, r)  = keccak256(RLP(F(H, r)))
```

Therefore `blockHash(H) = sealHash(H, 0)`.
The block hash does not depend on `round` or `committedSeals`.
Parent references, transaction and receipt lookups, and the `parentHash` of the next header use `blockHash`.

### Committed Seals

Each committed seal MUST be a 65-byte recoverable secp256k1 signature `r || s || v`, where `v` is the recovery identifier.
The signed digest is `sealHash(H, H.round)`, used directly as the 32-byte message without further hashing or a message prefix.

A block is valid only if:

- Every seal recovers to an address.
- The recovered addresses are pairwise distinct members of `V`.
- The number of seals is at least `Q`.

Seals MAY appear in any order.

## Rationale

The layout follows the Istanbul Byzantine fault tolerant extra-data of [EIP-650](https://eips.ethereum.org/EIPS/eip-650) and its later QBFT form, which keep consensus data inside the header without new header fields.
Excluding committed seals from the block hash lets validators sign an agreed hash before the seals exist.
Setting `round` to zero in the block hash keeps the block identity independent of the round at which it was committed, while the seals sign the actual round.

Each validator contributes its own seal, so a verifier recovers the committing validators directly from the seals without a separate signer list.

The fixed `mixDigest` prefix identifies Istanbul headers.
The vanity field and nonce are retained for compatibility with the inherited header layout and carry no consensus meaning.

## Backwards Compatibility

This proposal records the existing block format of ONEchain networks and changes no block.
The block hash differs from `keccak256(RLP(H))` of the complete header, so tools that compute Ethereum header hashes directly derive different values for Istanbul headers.
Light clients, bridges, and indexers must apply the filtered-header rule to verify parent links and committed seals.

Because `round` and the seals are outside the block hash, copies of the same block can carry different valid seal sets or encodings with the same hash.
Consumers that need a particular commitment must obtain it from a validated block rather than assume that equal hashes imply identical extra-data bytes.

## Test Cases

### Header Vector

The following header has number `100`, timestamp `1745400000`, gas limit `105000000`, gas used `0`, and base fee `1000000000`.
Its parent hash is `0x00…01`, state root `0x00…02`, `coinbase` `0x1111111111111111111111111111111111111111`, the empty uncle, transaction, and receipt roots, a zero bloom, `difficulty` `1`, and a zero nonce.
It has no fields from Shanghai or later upgrades.

```text
mixDigest = 0x43726f737320497374616e62756c2e200123456789abcdef0123456789abcdef
```

The unsealed extra-data has 32 zero bytes of vanity, validators `0x1111…1111` and `0x2222…2222`, no vote, round `0`, no seals, and a 65-byte reveal of `0xaa` bytes:

```text
0xf892a00000000000000000000000000000000000000000000000000000000000000000ea941111111111111111111111111111111111111111942222222222
222222222222222222222222222222c080c0b841aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

The sealed extra-data changes the round to `2` and adds two 65-byte placeholder seals of `0xbb` and `0xcc` bytes:

```text
0xf90119a00000000000000000000000000000000000000000000000000000000000000000ea9411111111111111111111111111111111111111119422222222
22222222222222222222222222222222c002f886b841bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb841cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
ccccccccccccccccccccccccccccccccccccccccccccccccccccb841aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Line breaks above are for presentation only.
With either extra-data value, the hashes are:

```text
blockHash         = 0x88f68ca560cab35aefb8accb4d0cb6d9360e945bc3a1e985b89f3c4df905c56a
sealHash(H, 2)    = 0xe56a9ff8606d9b7907ca4ce194045924f030775f8781d240a8e14cfcf06821a2
keccak256(RLP(H)) = 0xfbb6e9d29e4738aaca62d4a160aa1cd3078e992dbbda68f6ec9199217e8594c2  (sealed header, not the block hash)
```

The seals are placeholders; the vector checks encoding and hashing, not signature validity.

### Validity Cases

| Case | Expected result |
| --- | --- |
| `difficulty` other than `1` | Invalid. |
| Non-empty uncle list or a different `uncleHash` | Invalid. |
| `coinbase` not in `V` | Invalid. |
| `t < P.timestamp + blockPeriod` | Invalid. |
| `mixDigest` without the Istanbul prefix | Invalid. |
| Extra-data that is not an RLP list of six elements | Invalid. |
| `voteType` other than `0x00` or `0xff` | Invalid. |
| Seals with a repeated signer, a non-member signer, or fewer than `Q` signers | Invalid. |
| Changing `round` or `committedSeals` of a valid header | Block hash unchanged. |

Reproducible client tests for these cases remain pending.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Extra-data types, prefix, and filtered headers](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go).
- [Block hash](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/block.go).
- [Header, signer, and seal verification](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Validator snapshot application](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go).
- [Quorum size](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/validator/default.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-5/verification.md).

## Implementation and Activation

This format applies from genesis on ONEchain Istanbul chains.

This specification records existing behavior and schedules no new fork.
The reference source settings do not establish the activation history of deployed networks.

## Security Considerations

The block hash does not commit to the round or the committed seals.
Clients must validate these fields with the seal and validator-set rules before storing or acting on them, and must not assume that a hash identifies a unique extra-data encoding.

Committed seals provide Byzantine fault tolerant finality only while fewer than one third of `V` is faulty.
Seal verification must use `V` from the parent block, not a validator set read from the block being verified.

The vanity field and nonce are not validated and must not be treated as authenticated proposer data.
Implementations decoding extra-data from untrusted peers should bound the resources spent on oversized lists before seal verification.

## References

- [EIP-650: Istanbul Byzantine Fault Tolerance](https://eips.ethereum.org/EIPS/eip-650).
- [OIP-4](oip-4.md).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
