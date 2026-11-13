# OIP-26 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-26](../../OIPs/oip-26.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

References to `to-nexus/cross-contracts` are [internal verification sources](../../README.md#verification-sources) and require access to the cited repositories.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [consensus/istanbul/engine/consensus.go][consensus-istanbul-engine-consensus-go] | Offline target derivation, the slashed-list query, and the mitigation call. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Optional-call handling and parent-PoSA conditions. |
| [core/types/istanbul.go][core-types-istanbul-go] | Absence of a parent-certificate field. |

## Contract Sources

| Source | Inspected behavior |
| --- | --- |
| [ValidatorSlash.sol at 5cbc608][validatorslash-sol-5cbc608] | Counting, threshold, penalized flag, mitigation, and the uncaught penalty call. |
| [StakeHub.sol at 5cbc608][stakehub-sol-5cbc608] | `penalizeOffline`, jail, `unjail`, and the last-validator guard. |

## Calculation Checks

The mitigation results `50 / 4 = 12`, `20 -> 8`, and removal at `12` were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

Slash amounts recovered from a pool and jail recovery were not executed end to end.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Contract sources are those named by the client's installation registry. They were not rebuilt to prove byte-for-byte agreement with the embedded runtime, and no deployment inventory was verified.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[consensus-istanbul-engine-consensus-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[core-types-istanbul-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[validatorslash-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/ValidatorSlash.sol
[stakehub-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol
