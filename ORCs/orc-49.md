---
orc: 49
title: Multi-Token Game Asset Interoperability
description: An ERC-1155 application profile for asset identity, metadata, and inventory integration.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
---

# ORC-49: Multi-Token Game Asset Interoperability

## Abstract

This proposal defines a ONEchain application profile for [ERC-1155](https://eips.ethereum.org/EIPS/eip-1155) assets.
It adds shared inventory, metadata, and authority-disclosure requirements without standardizing individual game rules.

## Motivation

A game inventory may contain many token types with different issuance and transfer rules.
Wallets and inventory services need stable identity and metadata conventions while keeping product-specific mechanics separate.

## Specification

### Asset and Transfer Model

Adopt the upstream balance, operator approval, transfer, batch, receiver, event, and discovery behavior by reference.
Conforming contracts MUST implement the metadata URI extension and report its ERC-165 interface ID `0x0e89341c`.
Applications MUST identify each asset by `(chainId, contractAddress, tokenId)` and keep raw integer quantities distinct from display units.
Token ID zero is not reserved by this Draft.
No default 18-decimal interpretation or universal fungibility classification is assigned.
If display decimals are supplied, consumers apply that explicit value without changing transfer quantities; otherwise consumers MUST display raw integer quantities.

### Metadata and Inventory

Metadata MUST be a UTF-8 JSON object available through the published URI resolution scheme.
Use upstream field meanings and `{id}` substitution: lowercase hexadecimal, padded to 64 characters, without a `0x` prefix.
For example, token ID 42 substitutes 62 zeroes followed by `2a`.
Issuers MUST publish the mutability policy, update authority, and supported resolution behavior in the collection metadata returned by [ERC-7572](https://eips.ethereum.org/EIPS/eip-7572) `contractURI()`; ERC-7572 was Draft when consulted.
Follow the upstream `URI` event requirements; [ERC-4906](https://eips.ethereum.org/EIPS/eip-4906) applies only to ERC-721.
Off-chain content changes without a URI change MUST be described by a refresh policy in the same collection metadata.

Game-specific attributes, collection groupings, and cross-game item identifiers MAY be extensions, but MUST NOT replace the on-chain asset identity.
Clients MAY ignore unknown attributes for display and MUST NOT interpret them as transfer authority or executable instructions.
Metadata availability does not prove that a game currently accepts or gives utility to an item.

### Supply and Authority Disclosure

Issuers MUST publish the minting, burning, transfer-restriction, pause, and upgrade authorities applicable to each token class in the same collection metadata.
The base standard does not provide a universal `totalSupply(id)` getter; a supply extension MUST be identified separately.
Keep current supply, issuance cap, historical minted amount, and inventory balance distinct.
An item described as unique MUST have an explicit issuance policy; a balance of one by itself does not establish permanent uniqueness.

Crafting, consumption, rentals, bridging, and soulbound behavior require separate declared interfaces and rules.
This Draft imposes no product-specific token ID ranges, maximum batch length, or mandatory crafting schema.
Products with batch limits MUST disclose them without claiming a limit prescribed by ERC-1155.

## Rationale

Shared asset identity and metadata rules enable cross-application inventories without embedding one game's model in the base interface.
Separating supply concepts avoids treating an optional getter or display label as a consensus-backed issuance guarantee.

## Backwards Compatibility

Existing transfer interfaces remain unchanged.
Contracts without the metadata extension or required disclosures are not automatically conforming, even if basic transfers work.
No existing item is reissued, renumbered, or given new utility by publication.

## Test Cases

| Case | Expected result |
| --- | --- |
| Resolve metadata for ID 42 | Substitute a 64-character lowercase ID ending in `2a`. |
| Same token ID exists in two contracts | Track two separate assets. |
| No metadata display-decimal value | Show raw integer quantities rather than assuming an 18-decimal scale. |
| Supply getter is absent | Do not invent a current or maximum supply value. |
| Item is labelled unique while mint authority remains | Display the declared issuance policy rather than guaranteeing scarcity. |

Upstream transfer/receiver fixtures and product inventory tests must be added before conformance review.

## Reference Implementation

No ONEchain game-token contract or inventory consumer was selected for this Draft.
The upstream interface is adopted as a design basis, not a local implementation claim.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-49/verification.md).

## Implementation and Activation

Before Review, choose a concrete token implementation and consuming inventory tools, then agree on URI handling, update policy, supply extensions, and any product-specific limits.
Demonstrate single and batch transfer interoperability with receiver contracts and metadata consumers.
This design Draft activates no asset or game feature.

## Security Considerations

Operator approval grants broad authority across an ERC-1155 contract and must not be displayed as approval for only one item.
Receiver callbacks, mutable metadata, compromised minters, and arbitrary item attributes require explicit integration controls.
Display data must not be used as authorization to execute game actions or transfer assets.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
