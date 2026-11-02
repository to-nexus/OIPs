---
orc: 50
title: Soulbound Token Standard
description: An ERC-5192 profile for permanently account-bound tokens with optional ERC-5484 consent and burn authorization.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 48
---

# ORC-50: Soulbound Token Standard

## Abstract

This proposal defines a ONEchain soulbound token (SBT) profile based on [ERC-5192][erc5192] and the NFT metadata requirements in [ORC-48](orc-48.md).
It requires permanent account binding and defines wallet, issuance, and lifecycle disclosures.
[ERC-5484][erc5484] is an optional extension for signed recipient consent, immutable metadata, and predetermined burn authority.
These are proposed application requirements; no ONEchain implementation or deployment is asserted to conform.

## Motivation

Credentials, memberships, and achievement badges need a discoverable transfer restriction that wallets can distinguish from temporary pauses or failed transactions.
Applications also need to distinguish possession from recipient consent, issuer trust, and the continued validity of a credential.
A common profile can provide those boundaries without prescribing a credential issuer or identity system.

## Specification

### Required Interfaces

Conforming collections MUST satisfy ORC-48 and implement ERC-5192, adopting unchanged selectors, return types, events, and event indexing by reference.
The following interface declarations apply alongside ORC-48's metadata and conditional extension requirements:

| Interface | Identifier | Requirement |
| --- | --- | --- |
| ERC-165 | `0x01ffc9a7` | Required. |
| ERC-721 | `0x80ac58cd` | Required, with transfers restricted below. |
| ERC-721 metadata | `0x5b5e139f` | Required through ORC-48. |
| ERC-5192 | `0xb45a3c0e` | Required. |
| ERC-5484 | `0x0489b56f` | Advertise only when the optional extension is fully implemented. |

No additional ORC-specific interface identifier is assigned.
Implementations MUST retain the upstream ERC-721 ownership and approval interfaces; an approval MUST NOT bypass the transfer restriction or implicitly grant burn authority.

### Permanent Account Binding

For every existing token, `locked(uint256 tokenId)` MUST return `true` from issuance until destruction.
Queries for an unissued or burned token MUST revert.
Issuance MUST emit the ERC-721 mint `Transfer` event and ERC-5192 `Locked` event.
This profile strengthens ERC-5192's mint-event recommendation into a requirement.

All `transferFrom` and both `safeTransferFrom` overloads MUST revert for existing tokens, including self-transfers and calls from owners, approved operators, or administrators.
Custom methods MUST NOT move an existing token to another nonzero owner.
The collection MUST NOT unlock tokens or emit `Unlocked`; authorized destruction is not an unlock.
Upgrades MUST preserve these restrictions to retain conformance.

Minting and authorized burning remain distinct lifecycle operations and retain their ERC-721 events.
A burned token ID MUST NOT be issued again, including to the original address.
Permanent locking and non-reuse of burned IDs are ONEchain profile requirements beyond the minimal ERC-5192 interface.
Collections with temporarily locked or freely transferable tokens do not meet this collection-wide profile.

### Issuance, Metadata, and Credential State

The deployment MUST publish its issuer identities, mint authority, recipient acceptance mechanism or absence of one, burn authority, and upgrade permissions in the collection metadata required by ORC-48.
The base profile does not itself require a recipient signature or a burn function; applications MUST NOT infer either from `locked()`.
An ERC-721 receiver callback alone does not establish informed recipient consent to the credential's contents.

Use `(chainId, contractAddress, tokenId)` as the asset identity and apply ORC-48's metadata availability and update rules.
Metadata mutability remains possible in the base profile and MUST be disclosed; the optional ERC-5484 extension below prohibits it.
An unchanged URI does not prove that its resolved content is unchanged.

Issuers MUST separately describe any expiry, suspension, revocation, or replacement mechanism and how consumers can check its current state.
Those application states MUST NOT be encoded by returning `false` from `locked()`.
Token ownership alone MUST NOT be treated as proof of an unexpired credential, a trusted issuer, or a unique human.
This Draft defines no common credential schema, revocation registry, or status getter.

### Optional Consensual Issuance and Burn Authorization

A collection advertising ERC-5484 MUST implement its complete interface and requirements, including `burnAuth(uint256)`, the `Issued` event, recipient signature before issuance, and immutable metadata and burn authorization.
`Issued` supplements the mint `Transfer` and `Locked` events; it does not replace them.
Queries for unissued or burned IDs MUST revert.

| `BurnAuth` value | Party authorized to burn |
| --- | --- |
| `0` — `IssuerOnly` | Issuer only. |
| `1` — `OwnerOnly` | Token owner only. |
| `2` — `Both` | Either issuer or owner; joint approval is not required. |
| `3` — `Neither` | Neither party. |

The deployment MUST expose the authorized burn operation and issuer identity to consumers; ERC-5484 does not standardize a burn entry point.
A token operator or collection administrator receives no independent burn right outside the declared authorization.
The issuer identity used for a token's burn authorization MUST be fixed at issuance and match the issuer recorded by `Issued`.

Before signing, the recipient MUST be shown the issuer, destination account, metadata, and burn policy.
As an additional ONEchain requirement, consent verification MUST bind the chain, collection, issuer, recipient, token ID, metadata commitment, burn authorization, expiry, and a replay identifier consumed on successful issuance.
Expired or invalid consent MUST be rejected before minting; failed issuance MUST leave the replay state unchanged.
The exact signing schema and issuance ABI MUST be published and tested before Review; this Draft does not allocate a new signature format.
If contract recipients are supported, their consent MUST be verified through ERC-1271 at issuance; OneAccount signatures follow [ORC-40](orc-40.md).

ERC-5484 metadata immutability applies to the represented content, not only the URI string.
Issuers MUST NOT use ORC-48's metadata-update option to modify a token advertised under this extension.
Changes to credential validity must use the separately disclosed status mechanism without rewriting the issued metadata.

### Recovery and Consumer Behavior

Replacing a lost account MUST NOT transfer or silently reassign its existing SBT.
If supported, replacement requires a new token ID, the applicable issuance consent, and a disclosed relationship to the earlier credential.
The old token can be burned only under its burn policy; consumers must resolve any remaining old credential through the issuer's declared status rules.
An ERC-5484 `Neither` token has no burn-based recovery path.

Wallets MUST discover the locking interface and query token state before offering transfer or marketplace actions.
A failed query MUST NOT be interpreted as an unlocked token.
Wallets SHOULD allow locally hiding unsolicited credentials; hiding or burning does not erase public transaction history.
Changing a smart account's signer while keeping its address leaves token ownership unchanged.
Account binding therefore does not prevent account control from being sold, delegated, or compromised.

## Rationale

ERC-5192 supplies a small discovery surface compatible with the existing ORC-48 NFT profile.
Permanent locking and distinct replacement IDs keep token identity stable across credential lifecycles.
ERC-5484 remains optional because signed issuance, fixed metadata, and immutable burn rights are additional commitments that the minimal locking interface cannot establish.

[ERC-4973][erc4973] was considered as an alternative account-bound token model.
It excludes the ERC-721 interface identifier and defines its own issuance and unequip lifecycle, so its requirements are not combined with this ERC-721-based profile.

## Backwards Compatibility

An ERC-721 token that merely reverts on transfers does not automatically implement ERC-5192 discovery or this permanent-locking profile.
An ERC-5192 implementation that can unlock tokens does not satisfy the added permanent-binding requirement.
ERC-5484 support is not implied by ERC-5192 support, and an ERC-5484-only token still needs the required ERC-5192 and ORC-48 behavior.
Existing accounts and collections are not migrated by publication.

## Test Cases

| Case | Expected result |
| --- | --- |
| Query required interfaces | Return the declared ERC-165 support values. |
| Mint a token | Emit `Transfer` and `Locked`; `ownerOf` identifies the recipient and `locked` is true. |
| Owner, operator, or administrator invokes any transfer overload | Revert without changing ownership, balances, or successful-transfer logs. |
| Invoke self-transfer, custom reassignment, or unlock | Reject; the existing token stays bound. |
| Query `locked` for an unissued or burned ID | Revert. |
| Burn using declared authority | Remove the token and emit the burn `Transfer`; do not emit `Unlocked`. |
| Reissue a burned ID | Reject. |
| Exercise every ERC-5484 burn mode | Enforce all four authorization modes, including rejection for `Neither`. |
| Modify, replay, or submit expired signed issuance data | Reject without minting or consuming a new authorization. |
| ERC-5484 recipient is a smart account | Check its current ERC-1271 signature result using the declared signature profile. |
| Change metadata or burn authority after ERC-5484 issuance | Reject, including through an implementation upgrade. |
| Credential expires or is revoked without burning | Keep `locked` true and report validity through the declared application mechanism. |
| Token query fails or account signer changes | Do not infer transferability or a new token owner. |

Burn and consent cases apply to the features a collection advertises.
All applicable cases are required conformance checks, not passing runtime results.

## Reference Implementation

No ONEchain SBT contract, issuance service, or wallet consumer was selected or validated for this Draft.
The pinned upstream specifications define the interface basis.
Source scope and interface identifier checks are recorded in the [verification record](../assets/orc-50/verification.md).

## Implementation and Activation

Before Review, select an issuer and consumer, publish the collection and signature profiles, and implement the required conformance cases.
Verify every ownership-changing path, burn authorization, upgrade behavior, and any consent replay protection with the actual contract and wallet.
Resolve credential status and account replacement rules for the selected product.
This Draft requires no protocol activation and performs no deployment or migration.

## Security Considerations

Public credentials can expose or falsely imply personal attributes; issuers should avoid sensitive plaintext metadata and consumers must distinguish issuer claims from verified facts.
Unsolicited issuance, permanent records, and metadata retention require explicit product policies.
Neither hiding a token nor destroying it removes historical metadata or logs.

Compromised issuers, account keys, and upgrade authorities can undermine the credential's meaning even when ordinary transfers are disabled.
Mutable content behind a fixed URI breaks an ERC-5484 immutability claim.
Consent signatures need replay and domain protection; unsafe mint callbacks and custom recovery paths must not bypass authorization or permanent account binding.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).

[erc5192]: https://github.com/ethereum/ERCs/blob/4878022015ce5cbaed9ad6c4c8afe4cca95b1983/ERCS/erc-5192.md
[erc5484]: https://github.com/ethereum/ERCs/blob/4878022015ce5cbaed9ad6c4c8afe4cca95b1983/ERCS/erc-5484.md
[erc4973]: https://github.com/ethereum/ERCs/blob/4878022015ce5cbaed9ad6c4c8afe4cca95b1983/ERCS/erc-4973.md
