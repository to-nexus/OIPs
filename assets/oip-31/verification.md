# OIP-31 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-31](../../OIPs/oip-31.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/state_processor.go][core-state-processor-go] | The parent-hash call before ordinary transactions and its error handling. |
| [miner/worker.go][miner-worker-go] | The same call during block assembly. |
| [contracts/upgrade.go][contracts-upgrade-go] | Installation of the history runtime during finalization. |
| [params/protocol_params.go][params-protocol-params-go] | History address, window, and runtime. |
| [params/config.go][params-config-go] | The boundary predicate that is false for a fork active at genesis. |

## Verification Limits

The first Prague block was not reproduced from an actual parent state.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-state-processor-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_processor.go
[miner-worker-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go
[contracts-upgrade-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go
[params-protocol-params-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
