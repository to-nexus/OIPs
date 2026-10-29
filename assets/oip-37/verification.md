# OIP-37 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-37](../../OIPs/oip-37.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [params/config.go][params-config-go] | The BreakpointBravo predicate, preset values, fork identifier inputs, and blob schedule mapping. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Digest selection and the omission check. |

## Verification Limits

No combined boundary replay was performed.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
