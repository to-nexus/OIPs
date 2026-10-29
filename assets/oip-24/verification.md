# OIP-24 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-24](../../OIPs/oip-24.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Reveal payload, BLS reveal verification, and parent mixing. |
| [core/types/istanbul.go][core-types-istanbul-go] | The original digest prefix. |
| [core/evm.go][core-evm-go] | The EVM random value derived from the mix digest. |

## Calculation Checks

The signed payload `0x010956d7`, the prefix bytes, and the XOR mixing example in the proposal were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

No BLS reveal, digest, or PREVRANDAO vector was produced across the PoSA activation boundary.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[core-types-istanbul-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[core-evm-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go
