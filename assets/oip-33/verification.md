# OIP-33 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-33](../../OIPs/oip-33.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Header field checks for withdrawals, the parent beacon root, and the requests hash. |
| [core/state_processor.go][core-state-processor-go] | Skipped BeaconRoots call and request processing on Istanbul. |
| [core/block_validator.go][core-block-validator-go] | Body withdrawals and the requests-hash commitment. |
| [params/config.go][params-config-go] | Active system contracts on Istanbul. |
| [miner/worker.go][miner-worker-go] | Header construction, including the requests hash. |
| [core/genesis.go][core-genesis-go] | The genesis withdrawal commitment. |

## Verification Limits

No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[core-state-processor-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_processor.go
[core-block-validator-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/block_validator.go
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[miner-worker-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go
[core-genesis-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/genesis.go
