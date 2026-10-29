# OIP-29 Implementation Verification

This record describes source inspection performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-29](../../OIPs/oip-29.md), not a definition of protocol requirements or proof of network activation.
The source was inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/types/tx_setcode.go][core-types-tx-setcode-go] | Transaction and authorization encoding. |
| [core/types/tx_feedelegate_dynamic_fee.go][core-types-tx-feedelegate-dynamic-fee-go] | The fee-delegated wrapper and its empty authorization list. |
| [core/state_transition.go][core-state-transition-go] | Authorization check order, application, and refund. |
| [core/txpool/validation.go][core-txpool-validation-go] | Pool admission before and after Prague. |
| [core/txpool/legacypool/legacypool.go][core-txpool-legacypool-legacypool-go] | Limits for delegated senders and pending authorities, and fee payer budgets. |
| [core/vm/eips.go][core-vm-eips-go] | CALL-family gas changes. |
| [core/vm/evm.go][core-vm-evm-go] | Delegated code resolution under the Prague rules. |
| [core/types/transaction_signing.go][core-types-transaction-signing-go] | Signer selection under Breakpoint. |

## Verification Limits

No Go or Solidity test was run for this record; linked test files are starting points for verification, not a reported passing run.
Adopted EIP behavior was compared with go-ethereum v1.16.9 source and the cited EIP text; upstream conformance tests were not run.
No historical replay, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-types-tx-setcode-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/tx_setcode.go
[core-types-tx-feedelegate-dynamic-fee-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/tx_feedelegate_dynamic_fee.go
[core-state-transition-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[core-txpool-validation-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go
[core-txpool-legacypool-legacypool-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/legacypool/legacypool.go
[core-vm-eips-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/eips.go
[core-vm-evm-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/evm.go
[core-types-transaction-signing-go]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction_signing.go
