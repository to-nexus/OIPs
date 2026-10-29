# OIP-28 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-28](../../OIPs/oip-28.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [eth/protocols/eth/permission.go][eth-protocols-eth-permission-go] | Admission decision, the static-dial exception, and bootnode logging. |
| [eth/protocols/eth/handshake.go][eth-protocols-eth-handshake-go] | Admission before the status exchange. |
| [eth/handler.go][eth-handler-go] | Policy enablement and the revalidation sweep. |
| [consensus/istanbul/backend/backend.go][consensus-istanbul-backend-backend-go] | Snapshot-first eligibility. |
| [consensus/istanbul/engine/consensus.go][consensus-istanbul-engine-consensus-go] | StakeHub lookups and caches. |
| [p2p/dial.go][p2p-dial-go] | The static-dial connection flag. |

## Contract Sources

| Source | Inspected behavior |
| --- | --- |
| [StakeHub.sol at 5cbc608][stakehub-sol-5cbc608] | Operator and validator mappings, blacklist, minimum stake, and revocation. |

## Verification Limits

No connection to a live peer was made, and cache expiry was not exercised.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Contract sources are those named by the client's installation registry. They were not rebuilt to prove byte-for-byte agreement with the embedded runtime, and no deployment inventory was verified.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[eth-protocols-eth-permission-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/permission.go
[eth-protocols-eth-handshake-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth/handshake.go
[eth-handler-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/handler.go
[consensus-istanbul-backend-backend-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/backend.go
[consensus-istanbul-engine-consensus-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go
[p2p-dial-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/p2p/dial.go
[stakehub-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol
