# OIP-23 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-23](../../OIPs/oip-23.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/types/istanbul.go][core-types-istanbul-go] | Extra-data fields, optional trailing elements, bitset encoding, and filtered-header hashing under the original digest prefix. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Certificate decoding against the snapshot, quorum, aggregate verification, epoch list checks, and seal assembly. |
| [consensus/istanbul/core/commit.go][consensus-istanbul-core-commit-go] | COMMIT handling with inner BLS seals. |
| [crypto/bls/bls.go][crypto-bls-bls-go] | Backend selection and key and signature sizes. |

## Contract Sources

| Source | Inspected behavior |
| --- | --- |
| [StakeHub.sol at 5cbc608][stakehub-sol-5cbc608] | Signature check on key registration and key update. |

## Verification Limits

The domain separation tag was read from the Prysm v5.3.2 source used by the client.
No independent aggregate-signature vector was produced.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Contract sources are those named by the client's installation registry. They were not rebuilt to prove byte-for-byte agreement with the embedded runtime, and no deployment inventory was verified.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-types-istanbul-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[consensus-istanbul-core-commit-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/commit.go
[crypto-bls-bls-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/crypto/bls/bls.go
[stakehub-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol
