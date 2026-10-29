# OIP-35 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-35](../../OIPs/oip-35.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/types/istanbul.go][core-types-istanbul-go] | Digest prefixes and filtered-header hashing under both digest versions. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | Digest selection by the BreakpointBravo predicate and the genesis prefix. |
| [params/config.go][params-config-go] | The BreakpointBravo predicate and fork identifier inputs. |

## Calculation Checks

The prefix bytes `Cross Istanbul. ` and `Cross Istanbul.2` were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

No digest, filtered-header hash, or PREVRANDAO vector was produced across the activation boundary.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-types-istanbul-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
