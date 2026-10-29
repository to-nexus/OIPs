# OIP-38 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-38](../../OIPs/oip-38.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [params/protocol_params.go][params-protocol-params-go] | The `2^24` cap. |
| [core/state_transition.go][core-state-transition-go] | The ordinary precheck and `SkipTransactionChecks`. |
| [core/txpool/validation.go][core-txpool-validation-go] | Pool admission. |
| [core/txpool/legacypool/legacypool.go][core-txpool-legacypool-legacypool-go] | Removal of over-cap transactions under Osaka. |
| [miner/worker.go][miner-worker-go] | The cap during block assembly. |
| [eth/gasestimator/gasestimator.go][eth-gasestimator-gasestimator-go] | The estimation limit. |
| [internal/ethapi/transaction_args.go][internal-ethapi-transaction-args-go] | `SkipTransactionChecks` for `eth_call`. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | The system call path outside the ordinary precheck. |

## Verification Limits

No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[params-protocol-params-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
[core-state-transition-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[core-txpool-validation-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go
[core-txpool-legacypool-legacypool-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/legacypool/legacypool.go
[miner-worker-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go
[eth-gasestimator-gasestimator-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/gasestimator/gasestimator.go
[internal-ethapi-transaction-args-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/transaction_args.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
