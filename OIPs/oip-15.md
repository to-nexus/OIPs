---
oip: 15
title: Checkpoint Merkle Proof RPC
description: A JSON-RPC method returning a Merkle proof that a block hash belongs to a checkpoint range of canonical blocks.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Interface
created: 2026-10-28
---

# OIP-15: Checkpoint Merkle Proof RPC

## Abstract

This proposal specifies the `cross_getCheckpointProof` JSON-RPC method.
Given a block number and an inclusive range of block numbers, the method returns a Merkle proof that the block's hash is a leaf of a tree built over the canonical block hashes of that range.
It defines the parameters, range limits, the exact tree construction, including its padding rule, and an algorithm that verifiers can use to recompute the tree root.
The method does not return the root; verifiers obtain it separately.

## Motivation

Applications on other chains need to check that a ONEchain block hash belongs to a range of blocks that a checkpoint has already committed to.
A checkpoint records one root for many blocks, so a verifier needs a short membership proof for an individual block instead of every header in the range.

The tree construction is not a standard Merkle tree format.
Block hashes are used as leaves without further hashing, children are sorted before hashing, and the padding to a power of two is handled differently at the leaf level and above it.
A verifier written for a common sorted-pair format derives a different root for some proofs.
Clients, checkpoint producers, and verifiers therefore need a precise shared definition.

## Specification

### Conventions and Scope

`keccak256` denotes Keccak-256, and `||` denotes byte concatenation.
`Z` denotes 32 zero bytes, and `⊥` denotes an empty value.
For 32-byte values `a` and `b`, `min(a, b)` and `max(a, b)` compare the values as unsigned big-endian byte strings.
A *block hash* is the block hash defined by [OIP-5](oip-5.md).

This proposal defines the RPC method and the tree it proves against.
How a checkpoint root is produced, signed, or recorded on another chain is outside this proposal.

### Method

```text
cross_getCheckpointProof(blockNumber, startBlock, endBlock) -> proof
```

The method belongs to the `cross` namespace.
All three parameters MUST be JSON strings containing hexadecimal quantities with a `0x` prefix and no leading zeros, as for Ethereum block numbers.
Block tags such as `latest`, `pending`, `safe`, `finalized`, and `earliest` are not accepted.

The parameters MUST satisfy:

```text
0 <= startBlock < endBlock
startBlock <= blockNumber <= endBlock
endBlock - startBlock < 86400
```

The range is inclusive, so it contains `c = endBlock - startBlock + 1` blocks, with `2 <= c <= 86400`.
Every block in the range MUST be present in the serving node's canonical chain.

The result is a JSON array of hexadecimal byte strings.
Each element is either the empty string `"0x"` or a 32-byte value.
The method does not return the root, the range, or the leaf index.

A request that violates these rules returns a JSON-RPC error.
This proposal does not standardize error codes or messages.
The reference client reports a tag or negative value as `invalid block number`, an ordering or containment violation as `invalid range`, an oversized range as `range too large`, and a missing canonical header as `header N not found`.
A parameter that is not a valid hexadecimal quantity fails parameter decoding.

### Tree Construction

Let `h_0, ..., h_(c-1)` be the block hashes of `startBlock` through `endBlock`, in ascending block-number order.
Let `P` be the smallest power of two that is at least `c`.
The leaf level is `L_0 = [h_0, ..., h_(c-1), ⊥, ..., ⊥]`, with `P - c` trailing `⊥` values.
Leaves are the block hashes themselves and are not hashed again.

Each level `L_(k+1)` is built from `L_k` by combining consecutive pairs `(L_k[2j], L_k[2j+1])` with:

```text
combine(a, ⊥) = a     if a != ⊥
combine(⊥, ⊥) = Z
combine(a, b) = keccak256(min(a, b) || max(a, b))     if b != ⊥
```

The root is the single value of the last level, `L_d` with `d = log2(P)`.

Padding values occur only at the end of the leaf level, so `combine(⊥, b)` with `b != ⊥` never arises.
At the leaf level, a block hash paired with `⊥` is carried up unchanged, and two `⊥` values become `Z`.
No level above the leaf level contains `⊥`; `Z` values there are ordinary 32-byte values and are hashed like any other.

### Proof Construction

Let `i = blockNumber - startBlock` be the leaf index.
The proof has exactly `d` elements `e_0, ..., e_(d-1)`.
Element `e_k` is the sibling of the target's ancestor at level `k`:

```text
e_k = L_k[(i >> k) XOR 1]
```

A `⊥` sibling is encoded as `"0x"`, and every other sibling as its 32 bytes.
Elements are ordered from the leaf level toward the root.

As a consequence, `e_0` is empty exactly when `blockNumber = endBlock` and `endBlock - startBlock` is even, which is when `c` is odd and the target is the last leaf.
No other element is ever empty.
An element equal to `Z` appears wherever the target's sibling subtree contains only padding.

### Proof Verification

A verifier needs the root of the range from a trusted source, together with `startBlock` and `endBlock`.
A conforming verifier recomputes the root from the claimed block hash `h` and the proof:

```text
node = h
for k in 0 .. d-1:
    if e_k is empty: node = node
    else:            node = keccak256(min(node, e_k) || max(node, e_k))
accept if node == root
```

Before accepting, a conforming verifier MUST also check that:

1. The proof has exactly `d = log2(P)` elements for the range's `c`.
2. Every non-empty element is exactly 32 bytes.
3. Only `e_0` is empty, and only when the claimed block is `endBlock` and `endBlock - startBlock` is even; in that case `e_0` MUST be empty.

A successful verification shows that `h` is one of the leaves of the range.
Because pairs are sorted before hashing, the proof does not establish which position `h` occupies, and so it does not establish the block number of `h`.
A verifier that needs to bind a block number to a block hash MUST establish that binding separately, for example by checking the `number` field of a header that hashes to `h`.

### Availability

The reference client registers the `cross` namespace as a public API.
It is available over IPC and is available over HTTP or WebSocket only when the operator includes `cross` in the enabled modules, which by default contain only `net` and `web3`.
The method reads up to `86,400` canonical headers per request from the serving node's local chain.

## Rationale

Using block hashes directly as leaves lets a checkpoint producer build the tree from headers it already has, and lets a verifier check a block hash without hashing it again.
Sorting each pair before hashing removes left and right flags from the proof, so each element is a single 32-byte value except for the leaf-level padding case.
The cost is that the proof no longer binds the leaf position, which the verification rules make explicit.

The construction matches the reference client's Merkle library with hash sorting enabled and leaf hashing disabled.
That library carries a node without a sibling up unchanged and fills a missing pair with zero bytes, which produces the asymmetric padding rule.
This proposal records that behavior so that independent producers and verifiers can match existing roots and proofs.

The 86,400-block limit bounds the work per request and the proof length at 17 elements.
Requiring explicit numbers rather than tags keeps the range stable across requests while the head advances.

## Backwards Compatibility

This proposal records the existing method and changes no block, transaction, or existing result.
The `cross` namespace retains its historical name.

Proofs are not compatible with generic sorted-pair verifiers in two cases.
A verifier that cannot represent an empty element, such as one that decodes every element as a fixed 32-byte value, cannot accept the proof of the last block of an odd-sized range.
A verifier that substitutes `Z` for the empty element derives a different root.
Consumers of the method must implement the verification rule above to verify every block of a range.

## Test Cases

### Vectors

The vectors use synthetic 32-byte values in place of block hashes: `h_j` is the byte `j + 1` repeated 32 times, so `h_0 = 0x0101…01` and `h_4 = 0x0505…05`.
They were computed with the reference client's tree and proof functions, and the verification algorithm above reproduces each root from every proof.

For `c = 2`:

```text
root = 0x346d8c96a2454213fcc0daff3c96ad0398148181b9fa6488f7ae2c0af5b20aa0
i = 0: ["0x0202020202020202020202020202020202020202020202020202020202020202"]
```

For `c = 3`, the last leaf is carried up unchanged:

```text
root = 0x1d614fa3c8de62938b0948972494f9a3858575db69ce1d34c77926f30732c981
i = 2: ["0x", "0x346d8c96a2454213fcc0daff3c96ad0398148181b9fa6488f7ae2c0af5b20aa0"]
```

For `c = 5`, the tree has `P = 8` leaves and proofs have three elements:

```text
root = 0x87a1549615a817527af1266eecdda4c1f6353f5e4e775f54f0583ab3e6b5d0a6
i = 0: ["0x0202020202020202020202020202020202020202020202020202020202020202",
        "0x15812c763262dabc33411aff2c78af2cfcf55d57327737349ab4a7321a3dca59",
        "0x6058e7e36e6d807291a58f9f6f173224084011363f98bbed90b888762d5587b9"]
i = 2: ["0x0404040404040404040404040404040404040404040404040404040404040404",
        "0x346d8c96a2454213fcc0daff3c96ad0398148181b9fa6488f7ae2c0af5b20aa0",
        "0x6058e7e36e6d807291a58f9f6f173224084011363f98bbed90b888762d5587b9"]
i = 4: ["0x",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x0b242b9a6559f2d9f8563485a0697b746ec58ce879e0e5ac94d4c8a250723121"]
```

In the `i = 4` proof, the second element is `Z` and is hashed normally.
Replacing its empty first element with `Z` and hashing every element yields `0xb1501fee68977e657a472b5ebee485f0ce74e28d4e2ca6e78dc36dde0732411f`, which does not match the root.

### Request Cases

| `blockNumber`, `startBlock`, `endBlock` | Expected result |
| --- | --- |
| `5`, `5`, `5` | Error: `startBlock` is not below `endBlock`. |
| `4`, `5`, `9` or `10`, `5`, `9` | Error: `blockNumber` outside the range. |
| `0`, `0`, `86399` | Proof of 17 elements over 86,400 blocks, if all are canonical locally. |
| `0`, `0`, `86400` | Error: range too large. |
| `latest`, `0`, `10` | Error: tags are not accepted. |
| `"10"` without the `0x` prefix | Parameter decoding error. |
| `endBlock` above the serving node's head | Error: header not found. |
| `9`, `5`, `9` | `e_0` is empty, because the range has five blocks and the target is the last. |
| `8`, `5`, `8` | No empty element, because the range has four blocks. |

### Verification Cases

| Case | Expected result |
| --- | --- |
| Vector proof for `c = 5`, `i = 2`, with the stated root | Accepted. |
| Same proof with one element removed or an extra element appended | Rejected: wrong length. |
| Proof with an empty element other than `e_0` | Rejected. |
| Proof with an empty `e_0` for a claimed block other than `endBlock` | Rejected. |
| Valid proof of `h_1` presented as the hash of block `startBlock` | Membership succeeds; the block number binding requires a separate header check. |

Reproducible client tests for the request cases remain pending.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Method, range checks, tree, and proof](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/crossapi.go).
- [Namespace registration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/backend.go).
- [Console binding](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/web3ext/web3ext.go).
- [Merkle library `github.com/xsleonard/go-merkle` v1.1.0](https://github.com/xsleonard/go-merkle/blob/v1.1.0/merkle.go), used with hash sorting enabled and leaf hashing disabled.

## Implementation and Activation

The method is an RPC interface and requires no network activation.
The reference client has provided it since the `cross` namespace was introduced.
Providers that offer it must enable the `cross` module on the relevant transports.
Changing the tree construction would invalidate roots already computed with it and requires coordination with every checkpoint producer and verifier.

## Security Considerations

The RPC provider is not trusted for correctness.
A proof is only meaningful against a root that the verifier obtains from a trusted checkpoint source, together with the range that root covers.
A provider that is out of sync or serves another chain produces proofs that fail against such a root.

Leaves are not hashed, so a leaf and an internal node are both unlabeled 32-byte values.
A generic verifier that accepts any proof length can be given an internal node as if it were a leaf, with a shorter proof.
Requiring exactly `d` elements and allowing an empty element only in the specified position prevents this substitution.

Sorted-pair hashing does not bind a leaf to its position.
A valid proof shows that a hash belongs to the range, not that it is the hash of a particular block number.
Verifiers that act on a block number must bind it to the hash independently.

The root does not commit to `startBlock`, `endBlock`, or `c`.
Verifiers must take the range from the same trusted record as the root and must not infer it from the proof.

Each request can read up to 86,400 headers and build a tree of up to 131,072 leaves.
Providers should apply request limits or restrict the `cross` namespace to trusted clients.

## References

- [OIP-5](oip-5.md).
- [`github.com/xsleonard/go-merkle` v1.1.0](https://github.com/xsleonard/go-merkle/tree/v1.1.0).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
