# OIP-39 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-39](../../OIPs/oip-39.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [params/config.go][params-config-go] | The Osaka predicate, fork order, and preset values. |
| [core/vm/jump_table.go][core-vm-jump-table-go] | Osaka instruction table inheritance. |
| [core/vm/eips.go][core-vm-eips-go] | CLZ definition. |
| [core/vm/contracts.go][core-vm-contracts-go] | MODEXP bounds and pricing, P-256, the Osaka precompile map with `0xc0`, and map precedence. |
| [params/protocol_params.go][params-protocol-params-go] | Gas constants and the block size limit. |
| [core/block_validator.go][core-block-validator-go] | The EIP-7934 block size check. |
| [consensus/misc/eip4844/eip4844.go][consensus-misc-eip4844-eip4844-go] | The Osaka blob schedule entry and the Istanbul EIP-7918 exclusion. |
| [internal/ethapi/api.go][internal-ethapi-api-go] | Sidecar version selection after Osaka. |

## Verification Limits

No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[core-vm-jump-table-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go
[core-vm-eips-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/eips.go
[core-vm-contracts-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go
[params-protocol-params-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
[core-block-validator-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/block_validator.go
[consensus-misc-eip4844-eip4844-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go
[internal-ethapi-api-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go
