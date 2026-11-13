# OIP-25 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-25](../../OIPs/oip-25.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

References to `to-nexus/cross-contracts` are [internal verification sources](../../README.md#verification-sources) and require access to the cited repositories.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/state_transition.go][core-state-transition-go] | Crediting the effective gas price and blob fee to the coinbase under PoSA. |
| [consensus/istanbul/engine/consensus.go][consensus-istanbul-engine-consensus-go] | Fee sums and the `distributeReward` call. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Call order and abort on reward failure. |
| [internal/ethapi/api.go][internal-ethapi-api-go] | The `eth_beneficiary` result under PoSA. |
| [contracts/upgrade.go][contracts-upgrade-go] | The RewardHub source revision named by the registry. |

## Contract Sources

| Source | Inspected behavior |
| --- | --- |
| [RewardHub.sol at 373dfdd][rewardhub-sol-373dfdd] | Per-block checkpoint, tip clamp, burn transfer and retention, reward table, commission, and the pool call. |
| [DelegationPool.sol at 373dfdd][delegationpool-sol-373dfdd] | Handling of a zero operator, inactive PoSA, and no stake. |
| [StakeHub.sol at 5cbc608][stakehub-sol-5cbc608] | `validatorToActiveOperator`. |

## Calculation Checks

The fee totals `F = 252000` and `T = 42000` and the commission formula in the proposal were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

The DelegationPool and reserve versions in use on any network were not established.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Contract sources are those named by the client's installation registry. They were not rebuilt to prove byte-for-byte agreement with the embedded runtime, and no deployment inventory was verified.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-state-transition-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[consensus-istanbul-engine-consensus-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[internal-ethapi-api-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go
[contracts-upgrade-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go
[rewardhub-sol-373dfdd]: https://github.com/to-nexus/cross-contracts/blob/373dfdd9ec4b53f7f3efc0516a7b7cfaa7cab0f6/src/RewardHub.sol
[delegationpool-sol-373dfdd]: https://github.com/to-nexus/cross-contracts/blob/373dfdd9ec4b53f7f3efc0516a7b7cfaa7cab0f6/src/DelegationPool.sol
[stakehub-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol
