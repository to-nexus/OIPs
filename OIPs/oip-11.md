---
oip: 11
title: Istanbul Execution Fee Collection
description: Recipient selection and amount of execution and blob fees credited on ONEchain Istanbul chains, without base fee burning.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-11: Istanbul Execution Fee Collection

## Abstract

This proposal specifies how ONEchain Istanbul chains credit the fees paid by transactions.
The full effective gas price, including the base fee, is credited for the gas a transaction is finally charged, so no base fee is burned.
The recipient is a configured beneficiary, which block-keyed transitions can replace, and otherwise the block's `coinbase`.
From Cancun, the blob gas fee is credited to the same recipient, and the Istanbul engine adds no block reward.

## Motivation

[EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) burns the base fee and credits only the priority fee to the block's `coinbase`, and [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844) burns the blob gas fee.
ONEchain Istanbul chains instead credit both fees in full to a network-configured account.
Because the credited balance is part of the state root, every client must select the same recipient and compute the same amount.
Wallets, explorers, and supply trackers also need to know that the base fee is not removed from circulation.

## Specification

### Conventions and Scope

An *Istanbul chain* is defined in [OIP-4](oip-4.md).
For a transaction in a block with number `n`, let `p` be its effective gas price, `g` the gas finally charged to it, `b` its blob gas used, and `f` the block's blob base fee.

The base fee calculation is defined by [OIP-9](oip-9.md).
Blob transaction rules and the blob base fee are defined by [OIP-10](oip-10.md).
Which account pays a transaction's fees is defined by the applicable transaction rules, including [OIP-2](oip-2.md) for fee-delegated transactions.
This proposal defines only who receives the fees and how much.

### Recipient Selection

The *fee recipient* `R(n)` for block `n` is determined as follows:

1. Start with the configured `istanbul.beneficiary` address, if present.
2. Apply each entry of the configured `transitions` list whose `block` is less than or equal to `n`, in list order; an entry that sets a beneficiary replaces the current value.
3. If no address results, `R(n)` is the block's `coinbase`.

The `transitions` list MUST be ordered by ascending `block`.
The reference client stops reading the list at the first entry whose `block` exceeds `n`.
A beneficiary set by a transition at block `n` applies to the transactions of block `n` itself.

In chain configuration JSON, the base value uses the key `beneficiary` inside the `istanbul` object.
The reference client writes the transition key as `Beneficiary`; its JSON decoder matches keys case-insensitively and also reads `beneficiary`.
Implementations SHOULD accept both spellings in transition entries.

`R(n)` changes only the fee recipient.
The `coinbase` header field, the `COINBASE` instruction, and the warm `coinbase` address of [EIP-3651](https://eips.ethereum.org/EIPS/eip-3651) continue to refer to the block's `coinbase`.

### Execution Fee

After a transaction executes and its unused gas is returned, the client MUST add `g * p` wei to the balance of `R(n)`.

- `p` is the transaction's effective gas price: the legacy gas price, or `min(maxFeePerGas, baseFeePerGas + maxPriorityFeePerGas)` for a dynamic-fee transaction.
- `g` is the gas used after the refund allowed by [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529) and after any gas-floor adjustment of the active execution upgrades.
- The base fee is not subtracted from `p`, so the base fee portion is credited rather than burned.

The payer is debited `gasLimit * p` before execution and receives `(gasLimit - g) * p` afterwards.
The amount credited to `R(n)` therefore equals the execution fee that the payer finally bears.
For an OIP-2 transaction, the payer is the fee payer, while the recipient is still `R(n)`.

### Blob Fee

From Cancun, after the execution fee, the client MUST also add `b * f` wei to the balance of `R(n)` for a transaction with `b > 0`.
The payer is debited the same amount before execution, and it is not refunded or burned.

### Block Rewards and Logs

The Istanbul engine credits no block reward and no uncle reward.
A block without transactions therefore changes no balance through fee collection.

Fee credits are direct balance updates.
They execute no code at `R(n)` and produce no [OIP-3](oip-3.md) transfer log.

### Simulation Exception

This section is informative.
When the reference client simulates a call with base fee checks disabled, as in `eth_call` and `eth_estimateGas`, and both fee caps of the message are zero, it credits no fee.
This exception applies only to simulation and does not affect block execution.

### Beneficiary Query

This section is informative.
The reference client exposes `eth_beneficiary(blockNumber)`, which returns the configured address that `R(n)` resolves to at that block, or `null` when no beneficiary is configured.
A `null` result means that fees go to each block's `coinbase`.
Clients SHOULD call the method by the name `eth_beneficiary`.

## Rationale

Crediting the full effective gas price keeps the EIP-1559 transaction format and base fee mechanism while directing all transaction fees to an account chosen by the network.
A configured recipient, rather than the proposing validator, separates fee revenue from the right to propose blocks.
Block-keyed transitions allow the recipient to change at an agreed height without a new fork.

Keeping `COINBASE` and the EIP-3651 warm address on the block's `coinbase` preserves upstream execution semantics for contracts.
Treating fee credits as balance updates rather than transfers keeps them out of OIP-3 logs, which describe EVM value transfers only.

## Backwards Compatibility

This proposal records the existing fee accounting of ONEchain Istanbul chains and changes no block.

Tools that assume Ethereum's rules derive incorrect values on Istanbul chains.
In particular, `baseFeePerGas * gasUsed` is not a burned amount, the priority fee is not the only fee revenue, and blob fees are not burned.
Supply accounting must include fee credits to `R(n)` and must not subtract a base fee burn.

Changing the recipient, its transitions, or the credited amount changes state roots and requires coordinated configuration among all nodes.

## Test Cases

Unless stated otherwise, the configured beneficiary is `B0`, a transition at block `100` sets beneficiary `B1`, the block's `coinbase` is `C`, the base fee is `1,000,000,000` wei, and London is active.

| Case | Expected credit |
| --- | --- |
| Block `99`, dynamic-fee transaction with `maxPriorityFeePerGas = 2,000,000,000`, `maxFeePerGas = 5,000,000,000`, gas limit `100,000`, execution gas `60,000`, refund counter `10,000` | `p = 3,000,000,000`, `g = 50,000`; `B0` receives `150,000,000,000,000` wei. Ethereum would credit `100,000,000,000,000` wei and burn `50,000,000,000,000` wei. |
| The same transaction in block `100` | `B1` receives `150,000,000,000,000` wei. |
| Block `99`, legacy transaction with gas price `4,000,000,000` and gas used `21,000` | `B0` receives `84,000,000,000,000` wei. |
| No configured beneficiary and no transitions | `C` receives the credit. |
| OIP-2 transaction with the first case's parameters | The fee payer is debited `300,000,000,000,000` wei and refunded `150,000,000,000,000` wei; `B0` receives `150,000,000,000,000` wei; the sender pays no gas. |
| Cancun active, one-blob transaction with blob base fee `1` wei, `p = 3,000,000,000`, gas used `21,000` | `B0` receives `63,000,000,000,000 + 131,072 = 63,000,000,131,072` wei. |
| Block without transactions | No balance changes at `B0` or `C`. |
| Any credited transaction | No OIP-3 transfer log for the fee credit. |
| `COINBASE` executed in block `100` | Returns `C`, not `B1`. |
| `eth_call` with base fee checks disabled and zero fee caps | No credit. |

Reproducible client tests for these cases remain pending.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Fee crediting and refunds](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go).
- [Beneficiary configuration and transitions](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config_istanbul.go).
- [Preset beneficiary addresses](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/cross_params.go).
- [Istanbul author and finalization](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Beneficiary query](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-11/verification.md).

## Implementation and Activation

These rules apply from genesis on ONEchain Istanbul chains.
The reference presets configure the following beneficiaries and no beneficiary transitions:

| Network | Chain ID | Beneficiary |
| --- | --- | --- |
| ONEchain mainnet | `612055` | `0xEB569FfDa1a757938187320866959438Aa61f4c6` |
| ZoneZero | `612044` | `0x579c60A3176C5B588aeAD61a1F878a6A19CCc84E` |

This specification records existing behavior and schedules no new fork.
The reference source settings do not establish the activation history of deployed networks.

## Security Considerations

Whoever controls the beneficiary key receives all transaction fees of the network.
The beneficiary and its transitions are consensus configuration, and a mismatch between nodes produces different state roots.
Operators must distribute identical, correctly ordered configuration and must not set an address whose key is unavailable unless that loss of fees is intended.

Contracts that pay `block.coinbase` reach the proposing validator, not the fee recipient.
Applications must not treat `COINBASE` as the account that collects transaction fees.

Because no base fee is burned, the base fee limits congestion but does not reduce supply.
Economic analyses that rely on Ethereum's burn do not apply to Istanbul chains.

## References

- [EIP-1559: Fee market change for ETH 1.0 chain](https://eips.ethereum.org/EIPS/eip-1559).
- [EIP-3529: Reduction in refunds](https://eips.ethereum.org/EIPS/eip-3529).
- [EIP-3651: Warm COINBASE](https://eips.ethereum.org/EIPS/eip-3651).
- [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
