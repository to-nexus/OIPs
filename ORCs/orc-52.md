---
orc: 52
title: Native Asset Vaults
description: A native ONE vault profile with dedicated deposits, tokenized shares, and native asset redemption.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-11-04
requires: 20, 47
---

# ORC-52: Native Asset Vaults

## Abstract

This proposal adapts the accounting and consumer requirements of [ORC-47](orc-47.md) to vaults accepting native ONE through `depositNative` and issuing fungible shares.
It defines a common native asset interface independently of how a vault invests its assets.
Successful withdrawals pay native ONE to the receiver.
Protocol-specific position deposits, position transfers, and withdrawal queues require separate specifications.

## Motivation

A vault can accept native ONE directly while retaining the share accounting, valuation, and preview model used by tokenized vaults.
Applications need to know which calls accept native value, how shares are priced, and whether a completed withdrawal has delivered spendable ONE.
These rules should be reusable across investment strategies without requiring a particular pool, router, or staking permission.

## Specification

### Relationship to ORC-47

This profile adopts ORC-47's accounting and consumer disclosure requirements and its distinction between asset value and available liquidity.
It replaces the ERC-20 underlying asset and deposit flow with the native asset rules below.
It uses a synchronous withdrawal model; ORC-47's optional asynchronous profile is not adopted here.

Except for these explicit changes, the asset/share ABI, conversions, previews, limits, events, and rounding follow [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626) by reference.
Conformance to this proposal MUST NOT be described as unmodified ORC-47 or ERC-4626 conformance.

### Asset and Shares

`asset()` MUST return `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`, identifying native ONE under [ERC-7528](https://eips.ethereum.org/EIPS/eip-7528).
Asset amounts MUST be expressed in wei; one ONE is `10^18` wei.
The marker is an identifier, not an ERC-20 contract, and consumers MUST NOT call token methods on it.

The vault itself MUST expose the share token interface required by [ORC-20](orc-20.md).
Share decimals MUST remain stable and MAY differ from the native asset's 18 decimals.
For example, a virtual share offset can produce 24 share decimals without changing ONE's denomination.
This proposal does not require a particular offset, initial exchange rate, fee schedule, or investment strategy.

### Native Deposit Interface

The vault MUST expose these additional methods:

| Method | Mutability | Returns |
| --- | --- | --- |
| `depositNative(address receiver)` | `payable` | `uint256 shares` |
| `depositNative(address receiver, uint256 minShares)` | `payable` | `uint256 shares` |
| `maxDepositNative(address receiver)` | `view` | `uint256 assets` |

Both deposit methods MUST treat `msg.value` as the entire asset input and mint the resulting shares to `receiver`.
The one-argument method MUST have the same behavior as the two-argument method with `minShares = 0`.
The guarded method MUST revert if the shares actually minted are less than `minShares`.
An implementation MAY reject zero-value deposits and deposits that would mint zero shares.

Pricing MUST use the state before the incoming deposit is credited, including any fee accrual required by the published accounting policy.
In particular, an implementation reading its native balance MUST exclude the current `msg.value` when calculating that pre-deposit state.
Successful deposits MUST emit the ERC-4626 `Deposit` event with the caller, receiver, accepted native amount, and minted shares.
A failed deposit MUST revert its entire value transfer, accounting changes, share issuance, and logs.

`previewDeposit(assets)` MUST quote the native deposit path using ERC-4626's preview rules, with `assets` corresponding to the intended `msg.value`.
`maxDepositNative(receiver)` MUST apply the ERC-4626 deposit-limit rules to that path, including returning zero when deposits for the receiver are disabled.
Any minimum deposit and caller-specific restrictions MUST be disclosed separately; a positive capacity is not a guarantee that every smaller amount or caller is accepted.

The ERC-4626 `deposit(uint256,address)` and `mint(uint256,address)` methods MUST revert, and `maxDeposit(address)` and `maxMint(address)` MUST return zero.
`previewMint(shares)` remains an accounting quote under the ERC-4626 rounding rules, not an executable exact-share deposit route.
Consumers MUST use `maxDepositNative`, rather than `maxDeposit`, when preparing native deposits.

### Native Withdrawal Interface

`withdraw(uint256 assets,address receiver,address owner)` and `redeem(uint256 shares,address receiver,address owner)` retain their ERC-4626 signatures, return values, share authorization, and event requirements.
The underlying asset payment MUST be a native ONE transfer to `receiver` within the same transaction.
Delivering a position, receipt, wrapped token, or pending claim MUST NOT be reported as completion of that native payment.

If the native payment fails, the entire operation MUST revert, including share burns, allowance consumption, accounting changes, and events.
Implementations MUST maintain consistent accounting and prevent repeated spending of the same shares or assets during receiver callbacks.
Rejecting a zero-output exit MAY be supported and MUST be disclosed.

`maxWithdraw` and `maxRedeem` MUST return limits in asset and share units, respectively, capped by the native amount that can actually be delivered during the call and any applicable withdrawal restrictions.
Assets that cannot be realized into native ONE within that call MUST NOT contribute to immediate withdrawal capacity.
They MAY still contribute to `totalAssets()` under the published valuation policy.

### Accounting and Strategy Boundary

The issuer MUST publish the vault profile required by ORC-47, identifying this native deposit interface and the native settlement requirement.
The profile MUST explain the valuation of managed assets and external claims, reward recognition, fees, losses, transfer restrictions, and administrative authority.
It MUST also identify any minimum amounts and the treatment of unsolicited native transfers.

The strategy MAY hold native ONE or deploy it externally, provided its accounting and realized payments satisfy this profile.
External principal, rewards, and withdrawal liabilities MUST NOT be counted twice.
Fee settlement MUST be consistent with executable previews, including any share dilution that occurs before entry or exit.
The implementation MUST distinguish the value managed for holders from native balances excluded from that accounting; recovery of excluded balances MUST NOT remove holder backing.

Investment hooks and administrative methods are implementation choices.
This proposal specifies no external pool interface, position-transfer permission, or unstaking procedure.
A separate extension that changes the settlement asset MUST identify its different redemption semantics and MUST NOT claim this profile's native withdrawal behavior for that path.

## Rationale

A dedicated `depositNative` entry point makes the value-bearing call explicit and preserves the native deposit interface already used by the inspected vault source.
Its `minShares` overload provides a direct deposit slippage bound without requiring a separate router.
The standard deposit limits remain zero so applications do not mistake the disabled entry points for usable routes.

Native payment on withdrawal gives the common profile a clear settlement promise while leaving asset management to each implementation.
Keeping valuation separate from liquidity allows a strategy to hold illiquid assets without advertising them as immediately spendable ONE.

## Backwards Compatibility

This is a separate native profile; it does not change ORC-47's ERC-20 asset requirement.
Applications need an explicit integration for `depositNative` and the native asset marker.
The share token remains subject to ORC-20 independently of the vault entry points.

This profile is also distinct from [ERC-7535](https://eips.ethereum.org/EIPS/eip-7535), which requires payable `deposit` and `mint` methods.
Using the same native asset marker does not establish ERC-7535 compatibility.

## Test Cases

| Case | Expected result |
| --- | --- |
| Native deposit with a valid receiver | Credit exactly `msg.value`, mint shares, and emit `Deposit`. |
| Native balance already includes the incoming value | Quote shares from the pre-deposit state without counting the input twice. |
| One-argument and zero-floor deposits from identical states | Produce the same shares and accounting changes. |
| Minted shares fall below `minShares` | Revert the entire deposit. |
| Standard `deposit` or `mint` is called | Revert; their corresponding maximums remain zero. |
| Positive native capacity with a documented minimum | Reject a deposit below the minimum; do not interpret the maximum as a minimum-free acceptance guarantee. |
| Native withdrawal by an approved share spender | Consume the required authorization, burn shares, and pay the receiver in native ONE. |
| Receiver rejects payment or attempts reentrancy | Failed payment rolls back all effects; no callback can spend the same backing twice. |
| Managed value exceeds immediately realizable native assets | Withdrawal maximums do not exceed native settlement capacity. |
| Pending fees, losses, or differing share decimals | Preserve the declared valuation and preview behavior using each quantity's own units. |
| Unsolicited native transfer | Apply the published accounting policy without issuing deposit shares. |

These are required implementation scenarios, not claims that an implementation has passed them.
ORC-47's rounding fixture remains applicable, with assets denominated in wei and the mint result used only as a quote.

## Reference Implementation

[NativeVault at fce3934](https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol) supplies the inspected native deposit, share-accounting, and fee patterns.
It is a source for the reusable design, not a conforming reference implementation of the complete native settlement profile.
The correspondence and remaining implementation differences are recorded in the [verification record](../assets/orc-52/verification.md).

## Implementation and Activation

This proposal can serve as the design basis for a native vault, with investment-specific behavior documented alongside it.
Using it as a basis does not certify that an existing strategy implements every interface and settlement requirement.
Before Review, select a conforming native settlement implementation, publish its vault profile, pin the adopted ERC revisions, and test the scenarios above.
No conforming deployment or activation is established by this Draft.

## Security Considerations

Incoming native value can distort a deposit price if counted before its shares are priced.
Native payment introduces receiver callbacks; failed transfers and reentrant calls must not leave burned shares without payment or permit repeated withdrawal.
Donations, low share supply, valuation errors, fee dilution, loss allocation, and privileged upgrades require implementation-specific review.
Neither native denomination nor a positive managed balance proves that a strategy has immediate exit liquidity.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
