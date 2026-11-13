---
oip: 25
title: PoSA Fee Routing and Reward Distribution
description: PoSA fee collection, RewardHub settlement, reserve-funded rewards, and retained-payment behavior.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 2, 11, 19
---

# OIP-25: PoSA Fee Routing and Reward Distribution

## Abstract

This proposal records the PoSA reward path from transaction fees to RewardHub and its configured DelegationPool.
For PoSA blocks it replaces the recipient and block-reward rules of [OIP-11](oip-11.md), which continue to apply to blocks before PoSA activation.

## Motivation

Fee collection, contract transfers to a burn address, reserve-funded rewards, and validator commissions are different accounting steps.
Documenting only the EVM beneficiary omits the finalization settlement that determines their recipients.

## Specification

### Execution Fee Collection

When PoSA is active, the execution beneficiary is the block coinbase rather than the non-PoSA configured beneficiary.
The `eth_beneficiary` method of OIP-11 still returns the configured beneficiary and does not identify this recipient.
Credit the full effective execution gas price, including base fee, and any blob fee to that account during transaction execution.
[OIP-2](oip-2.md) determines whether sender or payer funds a fee-delegated transaction.

For ordinary transactions with receipts, calculate:

```text
T = sum(receipt.gasUsed * effectiveGasTip)
F = sum(receipt.gasUsed * (baseFee + effectiveGasTip)
        + receipt.blobGasUsed * receipt.blobGasPrice)
```

Omit the blob term when absent.
Do not include the system-transaction suffix in either sum.
After the optional slash call, execute `RewardHub.distributeReward(coinbase, T)` with value `F` through [OIP-19](oip-19.md).
This call is mandatory even when the fee sum is zero; a failure aborts finalization.

### Referenced RewardHub Behavior

The fork registry identifies RewardHub source revision `373dfdd9ec4b53f7f3efc0516a7b7cfaa7cab0f6`.
At that revision, distribution checkpoints the current block and rejects another distribution in the same block.
It clamps the requested tip to `msg.value`, recording an anomalous-tip event if necessary.
It sends `msg.value - tip` to the configurable burn address with a 30000-gas stipend; failed transfers remain in RewardHub and produce a retention event.
This is a contract transfer, not the execution layer's automatic destruction of base fees.
Blob fees are included in `F` but not `T`, so they enter that non-tip amount.

Select the greatest reward-table start height not greater than the current height; before the first entry the reward is zero.
Initialization sets an initial per-block amount of `9.5129376 * 10^18` wei and ten tiers, each separated by 31536000 blocks and halving the amount.
The initial commission rate is 500 out of 10000; the administrator can change it up to 5000.
For reward `R`, the base commission is `floor(R * commissionRate / 10000)`.
When `R` plus the tip is zero, RewardHub records an unsuccessful distribution without calling the pool.
Otherwise call the configured pool with the tip as value, the reward amount `R`, the pool commission (base commission plus tip), and the operator that `StakeHub.validatorToActiveOperator` returns for the validator.
That lookup returns zero for a jailed, suspended, revoked, or blacklisted validator; the DelegationPool source at the same revision then sends the commission and tip to the protocol reserve.
The pool funds the scheduled reward from its reserve integration; RewardHub does not create native currency.

If the pool call reverts, RewardHub catches the revert and retains the tip rather than refunding it to the proposer.
If the pool call returns without reverting but reports failure, the tip has already been transferred; the DelegationPool source at the same revision credits it to the reserve when PoSA is inactive there or no stake exists.
The contract records pooled, commission, fee, burned, unpaid, and success results.
Live pool/reserve versions and their full settlement behavior remain to be pinned; the installed RewardHub source is not proof of their deployment.

## Rationale

Separating collection from settlement avoids calling every non-tip wei an execution-layer burn.
Recording retained payments and pool outcomes prevents event consumers from treating attempted distribution as completed payment.

## Backwards Compatibility

Non-PoSA blocks retain OIP-11 behavior; its statements about block rewards and blocks without transactions apply only to those blocks.
Administrator-controlled parameters and proxy upgrades must be read at the historical state being executed.
The initialization schedule is not a claim about current reward rates or circulating supply.

## Test Cases

| Case | Expected result |
| --- | --- |
| Gas 21000, base fee 10, tip 2, no blobs | Collect F=252000 and pass T=42000 to RewardHub. |
| Blob fee present | Add it to F, not T. |
| Zero-fee PoSA block | Still execute the reward distribution call. |
| Second distribution in the same block | Reject at RewardHub. |
| Burn-address call fails | Retain that amount and record retention. |
| Pool call reverts | Retain the tip and record the unsuccessful settlement without inventing a refund. |
| Proposer's validator is jailed | Pass a zero operator; the referenced pool sends commission and tip to the reserve. |
| Reward tier boundary | Use the entry active at the current block height. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

References to `to-nexus/cross-contracts` are [internal verification sources](../README.md#verification-sources) and require access to the cited repositories.

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Execution beneficiary and fee credits](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go).
- [Fee sums and mandatory system call](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go).
- [Beneficiary query](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go).
- [Installation revision](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go).
- [Existing distribution tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus_test.go).
- [Referenced RewardHub source](https://github.com/to-nexus/cross-contracts/blob/373dfdd9ec4b53f7f3efc0516a7b7cfaa7cab0f6/src/RewardHub.sol).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-25/verification.md).

## Implementation and Activation

PoSA selects the coinbase collection and RewardHub call.
Reward start height, table entries, administrator, pool, burn address, and commission are contract/configuration data rather than a new activation decision in this Draft.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Match the embedded RewardHub bytecode to the cited build and pin pool/reserve implementations and their funding rules.
- Run balance-conservation, retained-payment, fee-delegation, and historical reward-tier integration tests.

## Security Considerations

Confusing proposer, payer, operator, pool, and reserve can double-count fees or misassign funds.
Failed contract payments can leave retained balances; source-level distribution success does not establish that every downstream reward was paid.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
