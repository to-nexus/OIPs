# OIP-22 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-22](../../OIPs/oip-22.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [consensus/istanbul/engine/consensus.go][consensus-istanbul-engine-consensus-go] | StakeHub reads, council ranking and selection, and ValidatorSet reads at epochs. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Epoch header preparation, epoch list verification, and council-update conditions. |
| [consensus/istanbul/backend/engine.go][consensus-istanbul-backend-engine-go] | Snapshot replacement at the Breakpoint boundary and at epochs. |
| [consensus/istanbul/config.go][consensus-istanbul-config-go] | Council period and validator epoch defaults. |
| [params/config.go][params-config-go] | The PoSA predicate and preset period and epoch values. |

## Contract Sources

| Source | Inspected behavior |
| --- | --- |
| [StakeHub.sol at 5cbc608][stakehub-sol-5cbc608] | `getValidators`, `maxCouncil`, and zero voting power for inactive or under-staked validators. |
| [ValidatorSet.sol at 5cbc608][validatorset-sol-5cbc608] | `updateValidators` and active-validator reads. |

## Calculation Checks

The ranking and tie-break examples and the period and epoch arithmetic in the proposal were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

Registration, jail, and rotation vectors were not executed against the installed contracts.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Contract sources are those named by the client's installation registry. They were not rebuilt to prove byte-for-byte agreement with the embedded runtime, and no deployment inventory was verified.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[consensus-istanbul-engine-consensus-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[consensus-istanbul-backend-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go
[consensus-istanbul-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/config.go
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[stakehub-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol
[validatorset-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/ValidatorSet.sol
