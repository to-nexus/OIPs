# OIP-34 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-34](../../OIPs/oip-34.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [params/config.go][params-config-go] | Breakpoint and PoSA predicates, fork order, and preset timestamps. |
| [core/vm/jump_table.go][core-vm-jump-table-go] | The Breakpoint instruction table. |
| [core/vm/contracts.go][core-vm-contracts-go] | The Breakpoint precompile map. |
| [core/types/transaction_signing.go][core-types-transaction-signing-go] | The Breakpoint transaction signer. |
| [consensus/misc/eip4844/eip4844.go][consensus-misc-eip4844-eip4844-go] | The Prague blob schedule entry under Breakpoint. |
| [contracts/upgrade.go][contracts-upgrade-go] | The Breakpoint registry entry. |
| [consensus/istanbul/engine/engine.go][consensus-istanbul-engine-engine-go] | PoSA finalization and system transaction gas reservation. |
| [consensus/istanbul/backend/engine.go][consensus-istanbul-backend-engine-go] | Snapshot handling at the boundary block. |
| [core/vm/instructions.go][core-vm-instructions-go] | SELFDESTRUCT implementations under the Adventure and Cancun-derived tables. |
| [core/state/statedb.go][core-state-statedb-go] | Account deletion state. |
| [core/evm.go][core-evm-go] | The transfer hook that emits native transfer logs. |
| [params/protocol_params.go][params-protocol-params-go] | EIP-2537 gas constants and discount tables. |
| [core/vm/contracts_test.go][core-vm-contracts-test-go] | EIP-2537 operation fixtures at test-only addresses. |

## Calculation Checks

The preset timestamps were converted to UTC: `1780282800` is 2026-06-01 03:00 and `1778814000` is 2026-05-15 03:00.
These are arithmetic checks, not output from running the reference client.

## Verification Limits

No combined boundary replay was performed.
No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[params-config-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[core-vm-jump-table-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go
[core-vm-contracts-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go
[core-types-transaction-signing-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction_signing.go
[consensus-misc-eip4844-eip4844-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go
[contracts-upgrade-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go
[consensus-istanbul-engine-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[consensus-istanbul-backend-engine-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go
[core-vm-instructions-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/instructions.go
[core-state-statedb-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state/statedb.go
[core-evm-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go
[params-protocol-params-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
[core-vm-contracts-test-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts_test.go
