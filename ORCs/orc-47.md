---
orc: 47
title: Tokenized Staking and Yield Vault Adapters
description: An ERC-4626 application profile for tokenized assets and optional asynchronous redemption.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 20
---

# ORC-47: Tokenized Staking and Yield Vault Adapters

## Abstract

This proposal defines a target adapter profile based on [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626), with optional [ERC-7540](https://eips.ethereum.org/EIPS/eip-7540) asynchronous flows.
It specifies ONEchain asset identification and accounting disclosures without treating the existing native staking pool as a conforming tokenized vault.

## Motivation

Wallets and yield applications need a clear distinction between deposited assets, transferable shares, accrued rewards, and pending withdrawals.
A native staking balance with custom router calls does not supply those standard interfaces by itself.

## Specification

### Asset and Share Interface

Conforming vaults MUST implement ERC-4626's asset/share interface, conversions, previews, limits, events, and rounding requirements by reference.
The underlying asset MUST be an ERC-20 token, and the share token MUST satisfy [ORC-20](orc-20.md), including explicit and stable display decimals.
The underlying asset MUST be a token contract; native ONE requires a separately specified wrapped-asset or adapter path.
The vault issuer MUST publish a vault profile that identifies the vault, asset, chain, implementation, and administrative authority and contains the disclosures below; its location and format remain a Review decision.
Share decimals and asset decimals may differ and MUST NOT be assumed equal; vaults SHOULD use share decimals equal to asset decimals, as ERC-4626 recommends.

### Accounting and Consumer Disclosures

The adapter MUST publish how it values held assets, protocol claims, accrued rewards, pending withdrawals, fees, and losses.
It MUST prevent double counting assets already committed to a withdrawal liability or reward distribution.
No fixed exchange rate, guaranteed yield, or monotonic share price is implied.
The relationship between external staking claims and `totalAssets()` MUST be reproducible from the selected adapter's state and valuation rules.

Applications MUST distinguish conversion estimates from executable previews and current deposit/withdrawal limits.
The adapter MUST declare who bears slashing, delayed reward realization, rounding dust, and any shortfall during withdrawal.
As ERC-4626 requires for `maxWithdraw` and `maxRedeem`, advertised instantaneous redemption MUST be limited to actually available liquidity.
Slippage bounds require an explicit consumer/router mechanism; the base ERC-4626 methods do not automatically add a user-selected minimum output.

### Synchronous and Asynchronous Profiles

A synchronous profile follows the ERC-4626 interaction model.
A deployment using ERC-7540 MUST identify which flows are asynchronous and implement its request/controller/operator model and interface discovery, including the `share()` method of [ERC-7575](https://eips.ethereum.org/EIPS/eip-7575) that ERC-7540 requires.
For an asynchronous redemption flow, the corresponding redeem/withdraw preview methods revert and requests progress through pending, claimable, and claimed states.
Asynchronous deposit has its own corresponding preview overrides.
Consumers MUST NOT treat a pending request as immediately redeemable or invent a guaranteed completion time.
Cancellation or claim-transfer features require separately declared behavior; they are not assumed from having a request ID, and [ERC-7887](https://eips.ethereum.org/EIPS/eip-7887) defines one cancellation extension.

### Illustrative Accounting Fixture

For a fee-free synchronous fixture with assets `A = 1000`, shares `S = 333`, and no virtual offsets, converting 10 assets gives 3 shares rounded down, and converting 3 shares gives 9 assets rounded down.
Minting 3 shares requires 10 assets rounded up; withdrawing 10 assets requires 4 shares rounded up.
This fixture tests rounding only and does not prescribe an initial exchange rate, donation defense, or deployed adapter formula.

## Rationale

An adapter boundary allows application interoperability without redefining consensus staking or reward rules.
Separating asynchronous requests from immediate redemption makes liquidity and ownership obligations visible.

## Backwards Compatibility

The inspected DelegationPool accepts native value through privileged router paths and exposes custom deposit, withdrawal, and unbonding behavior.
Its `balanceOf` and `totalSupply` names do not make it an ERC-20 share token or ERC-4626 vault.
A new wrapper or adapter changes custody, authority, and addresses and requires a separate deployment decision.

## Test Cases

| Case | Expected result |
| --- | --- |
| Fee-free rounding fixture above | Conversions 3 shares/9 assets; exact-output requirements 10 assets/4 shares. |
| Asset and share decimals differ | Preserve raw units and display each with its own scale. |
| Loss or slash reduces recoverable assets | Reflect the declared loss allocation; do not promise unchanged redemption value. |
| Withdrawal is pending | Do not allow it to be claimed twice or show it as liquid. |
| Async redemption preview is called | Follow the required ERC-7540 revert behavior. |
| Donation or first-deposit edge case | Verify the chosen adapter's rounding and inflation defenses before acceptance. |

Only the arithmetic fixture was checked; no vault implementation or staking integration was exercised.

## Reference Implementation

[DelegationPool](https://github.com/to-nexus/cross-contracts/blob/3905c3a02fd4825739f2cc61dc8c9a11a3670fc2/src/DelegationPool.sol) is inspected background for native staking and unbonding, not a conforming implementation of this Draft.
No wrapped asset, share contract, or ERC-4626/7540 adapter was selected.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-47/verification.md).

## Implementation and Activation

Before Review, choose the product's asset, share rights, wrapping/custody model, accounting formula, loss allocation, and synchronous or asynchronous withdrawal profile.
Implement the adapter and test its interfaces against real staking and consumer contracts, including liquidity and loss scenarios.
This design Draft makes no deployment, backing, or yield claim.

## Security Considerations

Donation attacks, low initial share supply, valuation manipulation, fee rounding, privileged upgrades, and delayed exits can harm depositors.
An adapter must not claim liquidity or assets it cannot realize, and claims must remain accounted for across losses and pending exits.
Interface conformance is separate from the security and economics of the underlying staking system.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
