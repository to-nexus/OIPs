# OIP-36 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-36](../../OIPs/oip-36.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Optional system call handling, the BreakpointBravo condition, and trial execution with snapshot revert. |
| [consensus/istanbul/engine/consensus_test.go][consensus-istanbul-engine-consensus-test-go] | Existing omission cases. |

## Verification Limits

No omission or trial-rollback case was replayed at an activation boundary.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[consensus-istanbul-engine-consensus-test-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus_test.go
