# OIP-30 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-30](../../OIPs/oip-30.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/state_transition.go][core-state-transition-go] | Floor calculation, refunds, and fee credit. |
| [core/txpool/validation.go][core-txpool-validation-go] | Pool floor check. |
| [params/protocol_params.go][params-protocol-params-go] | Gas constants. |

## Calculation Checks

The floor values `21000`, `25000`, and `22000` in the proposal were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-state-transition-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[core-txpool-validation-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go
[params-protocol-params-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
