# OIP-27 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-27](../../OIPs/oip-27.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/vm/contracts.go][core-vm-contracts-go] | The Breakpoint precompile map containing `0xc0`, input checks, output, required gas, and the warmed address set. |
| [params/protocol_params.go][params-protocol-params-go] | Gas constants. |
| [crypto/bls/bls.go][crypto-bls-bls-go] | The compressed BLS backend. |
| [core/vm/evm.go][core-vm-evm-go] | Gas consumption on a precompile execution error. |
| [core/vm/contracts_test.go][core-vm-contracts-test-go] | Precompile harness coverage, which omits `0xc0`. |

## Calculation Checks

The required gas values `4500` and `8000` and the length checks at `128`, `176`, `177`, and `224` bytes were checked by hand.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

The single-key vector file was not run, and no aggregate vector was produced.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-vm-contracts-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go
[params-protocol-params-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
[crypto-bls-bls-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/crypto/bls/bls.go
[core-vm-evm-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/evm.go
[core-vm-contracts-test-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts_test.go
