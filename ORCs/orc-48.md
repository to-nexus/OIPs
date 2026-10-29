---
orc: 48
title: NFT Metadata and Marketplace Interoperability
description: An ERC-721 application profile for metadata availability, updates, and marketplace integration.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
---

# ORC-48: NFT Metadata and Marketplace Interoperability

## Abstract

This proposal defines a ONEchain NFT integration profile based on [ERC-721](https://eips.ethereum.org/EIPS/eip-721).
It proposes additional metadata and disclosure requirements for collections, wallets, indexers, and marketplaces.
No specific ONEchain collection implementation is claimed to conform.

## Motivation

Ownership compatibility alone does not give applications predictable display metadata or a way to recognize changes.
Collections need common integration requirements without imposing one marketplace, storage vendor, royalty policy, or game model.

## Specification

### Required Profile

Adopt ERC-721 ownership, approvals, transfers, safe-receiver behavior, events, and interface discovery by reference.
This profile requires the metadata extension, which ERC-721 leaves optional: `name`, `symbol`, and `tokenURI`.
Enumeration is optional.
Identify an NFT by `(chainId, contractAddress, tokenId)`; names, images, and external marketplace IDs are not substitutes.
Any transfer restriction, burn authority, pause control, or upgrade authority MUST be disclosed in the collection metadata returned by [ERC-7572](https://eips.ethereum.org/EIPS/eip-7572) `contractURI()`; ERC-7572 was Draft when consulted.

### Metadata Availability

For an existing token, `tokenURI` MUST resolve under the collection's published URI scheme to a UTF-8 JSON object, directly or through a documented resolver.
The collection metadata MUST state supported URI schemes, availability expectations, mutability, and the authority that can change content or resolution.
Use upstream metadata field meanings; extensions MUST be documented, and consumers MAY ignore unknown fields for display but MUST NOT treat them as authority.
Display name and representative media SHOULD be available, with placeholders explicitly identified for unrevealed tokens.
This Draft does not mandate a ONEchain-specific attribute schema or storage gateway.

Consumers MUST keep token identity when metadata is missing or invalid and MUST NOT interpret a retrieval failure as loss of ownership.
They MUST distinguish a mutable URL from immutable content and MUST NOT infer permanence from an unchanged URL alone.
Cached metadata SHOULD be associated with its source and fetch time so updates can be reconciled.

### Updates and Optional Royalties

Collections supporting metadata changes MUST implement [ERC-4906](https://eips.ethereum.org/EIPS/eip-4906) notifications and discovery.
Whenever a token's JSON metadata changes, including through off-chain content, the collection MUST emit the corresponding ERC-4906 event.
Indexers use these notifications to refresh metadata; they are not ownership-transfer events.

[ERC-2981](https://eips.ethereum.org/EIPS/eip-2981) royalty information is optional and MUST be advertised only when implemented.
Its quote uses the same monetary units as the supplied sale price; returning royalty information does not itself enforce marketplace payment.
Royalty policy, recipients, and change authority MUST be disclosed in the collection metadata if this extension is used.

## Rationale

Requiring metadata and change notifications addresses shared consumer needs while leaving collection economics and content formats extensible.
Explicit asset identity prevents display similarities from implying the same collection or ownership.

## Backwards Compatibility

An ERC-721 collection lacking the required metadata or mutable-metadata notification behavior remains usable as an ERC-721 asset but does not automatically meet this profile.
Publication does not modify existing collections or enforce royalties.

## Test Cases

| Case | Expected result |
| --- | --- |
| Query declared interfaces and metadata | Match the implemented extensions and return types. |
| Update mutable JSON metadata | Notify and refresh through the declared ERC-4906 path. |
| Metadata retrieval fails | Preserve asset identity and show unavailable content without changing ownership. |
| Different collections use identical names and images | Keep separate contract-based identities. |
| Optional royalty quote requested | Use the sale-price units without claiming payment occurred. |

These are proposed conformance cases, not results from an existing collection.

## Reference Implementation

No ONEchain NFT implementation or marketplace integration was selected or validated for this Draft.
The upstream standards are interface references, not evidence of a local deployment.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-48/verification.md).

## Implementation and Activation

Before Review, select at least one collection and consuming wallet or marketplace, agree on URI resolution and metadata-update behavior, and implement interoperability fixtures.
Additional attributes, reveal rules, and royalty policies remain product decisions outside the required baseline.
This design Draft makes no adoption claim.

## Security Considerations

Metadata and media may contain malicious content or impersonate another asset; consumers must sanitize rendering and constrain retrieval.
Mutable metadata, upgrade authority, and transfer restrictions can change the user's effective rights.
An interface response or royalty declaration does not prove provenance or economic value.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
