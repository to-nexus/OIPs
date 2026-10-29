# OIP-32 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-32](../../OIPs/oip-32.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [params/config.go][params-config-go] | Blob schedule defaults and the mapping of Breakpoint and BreakpointBravo to the Prague entry. |
| [consensus/misc/eip4844/eip4844.go][consensus-misc-eip4844-eip4844-go] | Schedule selection and the excess formula. |
| [core/txpool/validation.go][core-txpool-validation-go] | Rejection of blob transactions on Istanbul. |
| [internal/ethapi/api.go][internal-ethapi-api-go] | Sidecar version selection in the transaction RPC paths. |
| [miner/worker.go][miner-worker-go] | Sidecar version selection in the pending filter. |

## Calculation Checks

The blob count examples and the excess example in the proposal were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[consensus-misc-eip4844-eip4844-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go
[core-txpool-validation-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go
[internal-ethapi-api-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go
[miner-worker-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go
