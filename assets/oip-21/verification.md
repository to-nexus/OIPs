# OIP-21 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-21](../../OIPs/oip-21.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [contracts/upgrade.go][contracts-upgrade-go] | Registry entries, chain-ID-0 fallback, Prague before Breakpoint, PoSA gating of the whole Breakpoint entry, code and storage writes, nonce on new accounts, and initializer arguments. |
| [contracts/const.go][contracts-const-go] | System addresses, the ERC-1967 implementation slot, and the disabled-initializer slot and value. |
| [core/types/istanbul.go][core-types-istanbul-go] | Normalization of configured BLS keys to 48 bytes. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Registry application and initialization calls during finalization and block assembly. |
| [params/config.go][params-config-go] | The `IsOnPrague` and `IsOnBreakpoint` boundary predicates. |
| [contracts/upgrade_test.go][contracts-upgrade-test-go] | Existing Breakpoint runtime code-hash checks. |

## Contract Sources

| Source | Inspected behavior |
| --- | --- |
| [ValidatorSet.sol at 5cbc608][validatorset-sol-5cbc608] | `initialize` arguments. |
| [StakeHub.sol at 5cbc608][stakehub-sol-5cbc608] | `initialize` arguments. |
| [RewardHub.sol at 373dfdd][rewardhub-sol-373dfdd] | `initialize` arguments. |
| [ValidatorSlash.sol at 5cbc608][validatorslash-sol-5cbc608] | `initialize` arguments. |

## Verification Limits

Initializer argument vectors and runtime hashes were not reproduced for any network.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Contract sources are those named by the client's installation registry. They were not rebuilt to prove byte-for-byte agreement with the embedded runtime, and no deployment inventory was verified.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[contracts-upgrade-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go
[contracts-const-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/const.go
[core-types-istanbul-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[contracts-upgrade-test-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade_test.go
[validatorset-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/ValidatorSet.sol
[stakehub-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/StakeHub.sol
[rewardhub-sol-373dfdd]: https://github.com/to-nexus/cross-contracts/blob/373dfdd9ec4b53f7f3efc0516a7b7cfaa7cab0f6/src/RewardHub.sol
[validatorslash-sol-5cbc608]: https://github.com/to-nexus/cross-contracts/blob/5cbc608bd77ef186120308ec8219a016197efba2/src/ValidatorSlash.sol
