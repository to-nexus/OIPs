# OIP-19 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-19](../../OIPs/oip-19.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Classification, expected-call order, signing-hash comparison, suffix consumption, direct EVM execution, consumed gas, nonce and receipt handling, optional-call omission, and the leftover check. |
| [consensus/istanbul/engine/consensus.go][consensus-istanbul-engine-consensus-go] | Construction of the slash, reward, mitigation, and council-update calls. |
| [core/state_processor.go][core-state-processor-go] | Separation of the system transaction suffix during import. |
| [contracts/const.go][contracts-const-go] | System contract addresses. |
| [core/state_transition.go][core-state-transition-go] | The ordinary transaction precheck that the system path does not use. |

## Verification Limits

Import, assembly, tracing, and replay of identical blocks were not compared.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[consensus-istanbul-engine-consensus-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go
[core-state-processor-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_processor.go
[contracts-const-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/const.go
[core-state-transition-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
