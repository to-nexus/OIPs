---
orc: 46
title: Bridged Fungible Tokens
description: An ERC-7802 bridge interface with ONEchain asset identity and supply-accounting rules.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 20
---

# ORC-46: Bridged Fungible Tokens

## Abstract

This proposal combines [ORC-20](orc-20.md) with [ERC-7802](https://eips.ethereum.org/EIPS/eip-7802) bridge minting and burning.
It proposes common asset identity, authorization, unit conversion, and migration requirements for ONEchain bridge integrations.

## Motivation

Matching token names do not establish that assets share backing, and existing mint/burn interfaces differ between bridge implementations.
An explicit profile lets wallets, bridges, and indexers distinguish local token accounting from cross-chain issuance.

## Specification

### Token and Bridge Interface

Conforming tokens MUST satisfy ORC-20 and implement ERC-7802's `crosschainMint` and `crosschainBurn` methods and events, and ERC-165 support for interface ID `0x33331994`, on the token contract itself.
ERC-7802 was Draft when consulted and requires ERC-165 and ERC-5679; the adopted revision MUST be pinned.
Both operations MUST also emit ERC-20 `Transfer` events from or to the zero address, which strengthens ERC-7802's recommendation.
The proposed interface is a target for new deployments; it is not asserted to exist in the inspected token.
Both operations MUST enforce an explicitly configured bridge authority.
Revocation or replacement of that authority MUST follow the token's documented administration model.
Bridge mint/burn authority is separate from user allowance and can affect user balances; issuers MUST disclose that power, and wallets SHOULD display it.

### Asset Identity and Units

The issuer MUST publish a route record for each supported route as a JSON object with `originChainId`, `originToken`, `destinationChainId`, `destinationToken`, `bridge`, `originDecimals`, `destinationDecimals`, `remainderPolicy`, `custody`, `upgradeAuthority`, and `pauseAuthority`.
Applications MUST key the destination asset by chain ID and token address, not symbol.
The record MUST also state whether another bridge's representation of the same origin asset is interchangeable.
No on-chain getter or registry is mandated; where route records are published remains a Review decision.

`totalSupply()` MUST remain the supply of the local representation under ORC-20.
Backing, locked amounts, pending messages, and circulation on other chains are separate accounting quantities.
The bridge MUST convert amounts from `originDecimals` to `destinationDecimals` by exact powers of ten with checked arithmetic.
If downscaling leaves a remainder, the bridge MUST either reject the amount or retain and account for the remainder, as declared in `remainderPolicy`; silently discarding it is prohibited.
For example, converting `1,000,000,000,000,000,000` raw units from 18 to 6 decimals produces `1,000,000` destination units.

### Message Processing

The bridge layer MUST authenticate the source message, bind the destination route and recipient, enforce its finality policy, and prevent duplicate execution.
The token interface alone does not provide these properties.
Message outcomes MUST be observable as pending, completed, or failed through bridge events or a status interface named in the route record; retries MUST NOT mint or release twice.
The bridge MUST define whether a failed destination operation can be retried, refunded, or cancelled, without assuming rollback across chains.

### Existing Token Migration

The inspected token exposes `mint(address,uint256) returns (bool)` and `burn(address,uint256) returns (bool)` guarded by a minter role.
The inspected bridge mints to its own address and burns its own balance before moving tokens, so wrapping those calls as ERC-7802 would report the bridge, not the user, as `_to` or `_from`.
Those methods are not ERC-7802 selectors and do not emit its additional bridge events.
An adapter that calls the legacy methods is a bridge component, not a conforming token: it MUST be explicitly authorized and enforce the same route and message checks, consumers MUST index the token address rather than adapter events, and a deployment MUST NOT claim the original token implements an interface exposed only by an adapter.
The inspected token is not upgradeable, so conformance requires a redeployed token or a lockbox-style wrapper; each changes trust and address properties and requires a route-specific migration decision.

## Rationale

The upstream interface supplies a small interoperable surface, while route identity and accounting address ONEchain integration needs.
Keeping bridge verification outside the token interface avoids implying that a successful mint proves backing or finality.

## Backwards Compatibility

Existing ERC-20 calls remain unchanged.
Legacy bridge selectors may coexist as separately authorized interfaces, but their existence does not establish conformance.
No existing representation is renamed, migrated, or granted a new minter by this document.

## Test Cases

| Case | Expected result |
| --- | --- |
| Authorized bridge mint/burn | Correct local balance/supply changes, ERC-7802 events, and `Transfer` events from or to the zero address on the token contract. |
| Unauthorized or revoked bridge | Reject without changing balances or supply. |
| Replay a completed message | Reject before a second issuance or release. |
| Same symbol on a different origin route | Treat as a distinct asset. |
| Exact 18-to-6 conversion of one token | Produce 1,000,000 raw destination units. |
| Downscale an amount with a nonzero remainder | Follow the declared reject or accounted-remainder policy. |
| Call ERC-7802 on an unmodified legacy deployment | Do not report supported-interface conformance. |

These cases require token, adapter, bridge, and indexer testing; none was executed for this Draft.

## Reference Implementation

[CrossMintableERC20V2](https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/CrossMintableERC20V2.sol) provides the inspected legacy metadata, minter-role, and mint/burn behavior, and [BaseBridge](https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/BaseBridge.sol) shows how the bridge calls it.
No conforming ERC-7802 adapter or end-to-end route was established.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-46/verification.md).

## Implementation and Activation

Before Review, choose the bridge route, authorization model, canonical asset-discovery format, conversion policy, and migration mechanism.
Implement and verify the new selectors and bridge events with the actual bridge consumers.
This Draft makes no deployment or backing claim and grants no bridge authority.

## Security Considerations

A compromised minter can create unbacked balances or burn balances without allowance.
Route confusion, finality failures, message replay, decimal truncation, and independent upgrades can break backing or release the wrong asset.
Interface conformance must be assessed separately from bridge custody and verification security.
ERC-7802 advises against using its interface for wrapped native tokens; a wrapped ONE representation needs its own custody review.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
