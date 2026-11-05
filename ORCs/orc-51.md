---
orc: 51
title: AI Character Registry
description: An ERC-721 registry that gives each AI character one permanent identity card, with fixed character and creator records and details served by the issuing platform.
author: Issac (@issacley-nexus)
discussions-to: "https://github.com/to-nexus/OIPs/issues/8"
status: Draft
type: Standards Track
created: 2026-11-03
requires: 48
---

# ORC-51: AI Character Registry

## Abstract

This proposal specifies a registry that issues one permanent ERC-721 identity card for each AI character registered on an issuing platform. The card fixes the character's ID, its creator, its registration time and an initial fingerprint of its text, and the card's holder is the character's owner of record. Names, images, text and the services where the character is available stay with the issuing platform, which serves them through the card's metadata URL.

## Motivation

An AI character is often offered on several services at once. Each service keeps its own copy and assigns its own identifier, so nothing ties the copies to one character, and nothing records who created the character or who owns it after it changes hands.

This registry gives each character one card. The card number and the issuer's character ID identify the character on every service, the creator record survives transfers, and the holder is the owner of record. What changes over time stays with the issuing platform, so cards never need rewriting when a character is renamed or moves between services. The first expected issuer is ONE Stage.

## Specification

The uppercase keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY follow [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174).

### Definitions

- **Registry:** a dedicated ERC-721 contract deployed separately by each platform.
- **Issuer:** the registering platform, represented by exactly one registry-wide address at a time.
- **Card number:** the registry-assigned `tokenId` of a character's identity card.
- **Character ID:** the issuer's permanent character identifier, unique within that registry.
- **Creator:** the signing wallet to which the card is minted.
- **Holder:** `ownerOf(tokenId)`, the character's owner of record.
- **Registration time:** the issuance block's `block.timestamp` in seconds.
- **Fingerprint document:** the issuer's JSON object containing the character's published text fields, excluding timestamps, image URLs, and internal IDs.
- **Initial fingerprint:** `keccak256` of the UTF-8 bytes of that document's [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) canonical form.
- **Base URL:** the registry-wide prefix used to resolve character metadata.
- **Admin:** the address authorized to set the base URL and issuer address.

### Interface

Registries MUST satisfy [ORC-48](orc-48.md), adopting ERC-721 transfers, approvals, safe receivers, metadata, and events unchanged. They MUST advertise ERC-165 `0x01ffc9a7`, ERC-721 `0x80ac58cd`, metadata `0x5b5e139f`, ERC-4906 `0x49064906`, and `IAICharacterRegistry` `0x7f6f796a`; `0xffffffff` MUST return false. The extension identifier includes only the following functions, excluding events and errors.

```solidity
interface IAICharacterRegistry {
    struct Character {
        string characterId;
        address creator;
        uint256 registeredAt;
        bytes32 initialFingerprint;
    }
    error Unauthorized();
    error InvalidCharacterId();
    error CharacterAlreadyIssued();
    error InvalidCreator();
    error SignatureExpired();
    error InvalidSignature();
    error UnknownToken();
    error InvalidIssuer();
    error InvalidBaseURI();
    error InvalidRange();
    event CharacterIssued(uint256 indexed tokenId, string characterId,
        address indexed creator, bytes32 initialFingerprint, uint256 registeredAt);
    event IssuerChanged(address indexed previousIssuer, address indexed newIssuer);
    event BaseURIChanged(string previousBaseURI, string newBaseURI);
    event MetadataUpdate(uint256 _tokenId);
    event BatchMetadataUpdate(uint256 _fromTokenId, uint256 _toTokenId);
    function admin() external view returns (address);
    function issuer() external view returns (address);
    function baseURI() external view returns (string memory);
    function character(uint256 tokenId) external view returns (Character memory);
    function tokenIdOf(string calldata characterId) external view returns (uint256);
    function issue(string calldata characterId, address creator,
        bytes32 initialFingerprint, uint256 deadline, bytes calldata signature)
        external returns (uint256 tokenId);
    function setIssuer(address newIssuer) external;
    function setBaseURI(string calldata newBaseURI) external;
    function notifyMetadataUpdate(uint256 fromTokenId, uint256 toTokenId) external;
    function contractURI() external view returns (string memory);
}
```

### Records and issuance

Character IDs MUST contain 1–64 ASCII bytes matching `[A-Za-z0-9_-]+`, compared case-sensitively without normalization. The first expected issuer uses 26-character ULIDs within this alphabet. `tokenIdOf` MUST return zero for an unissued ID.

Only the issuer MUST be permitted to call `issue`; it submits and pays for issuance. Successful cards MUST receive consecutive numbers starting at 1. Repeated IDs MUST revert permanently. Issuance MUST store the supplied fields with `registeredAt = block.timestamp` and reserve the ID before safe-minting to the nonzero creator, emitting `Transfer` and `CharacterIssued`. Failed issuance MUST roll back all state and logs, including number allocation. `character` and `tokenURI` MUST revert for unissued numbers.

The card number and all `Character` fields MUST remain fixed. Registries MUST NOT expose burning, reassignment outside ERC-721 transfers, pausing, or upgrades. Transfers change only the holder among these identity fields; normal ERC-721 approval clearing still applies.

### Creator authorization

The creator MUST sign [EIP-712](https://eips.ethereum.org/EIPS/eip-712) typed data using domain `EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)`, with name `AI Character Registry`, version `1`, current chain ID, and registry address. The primary type MUST be:

```text
IssueCharacter(string characterId,address creator,bytes32 initialFingerprint,uint256 deadline)
```

The struct hash MUST be `keccak256(abi.encode(TYPEHASH, keccak256(bytes(characterId)), creator, initialFingerprint, deadline))`; the digest MUST be `keccak256(0x1901 || domainSeparator || structHash)`, without a personal-message prefix. `TYPEHASH` MUST match the Test Cases vector.

For creators without code, verification MUST recover the creator using 65-byte `r || s || v` ECDSA signatures, `v` 27 or 28, and nonzero `r` and `s` with low `s`. For creators with code, verification MUST call [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) `isValidSignature(bytes32,bytes)` by static call and require ABI-decoded `0x1626ba7e`; reverts, malformed returns, or other values MUST fail. Contract signature length MUST NOT be restricted. Counterfactual verification is outside scope. Issuance MUST reject `block.timestamp > deadline`; equality is valid. Permanent character-ID uniqueness prevents successful replay within the registry, without a nonce.

### Details and administration

Issuers MUST publish the fingerprint document's field selection and preserve its original values for recomputation; Unicode MUST NOT be normalized before JCS. The contract stores the supplied fingerprint, without verifying the offchain text.

`tokenURI(tokenId)` MUST concatenate `baseURI()` and the stored character ID, without further encoding or separators. The base URL MUST be a valid absolute HTTPS URL ending in `/`, without query or fragment. The issuer MUST serve ERC-721 JSON metadata containing `name`, `description`, and `image`, and character details containing current text and conversation services. Cards MUST NOT store per-token URLs. The services-list format and platform lookup API remain unfinished issuer work in this Draft. Holder rights over character data remain issuer-defined, outside this standard.

Deployment MUST set a nonzero admin, a nonzero initial issuer, the initial base URL, and the collection name and symbol. Only admin MUST be permitted to call `setIssuer` and `setBaseURI`, emitting their corresponding events. Admin MUST have no other powers over cards or registry settings. Whether the admin role can be handed to another address, for example through a two-step handover, is unresolved in this Draft; adding such a function would change the `IAICharacterRegistry` interface identifier. Neither operation changes fixed records. `contractURI()` MUST return `baseURI()` followed by `collection.json`, a path no character ID can produce. The issuer serves the collection metadata there, and it MUST satisfy ORC-48's collection disclosures, including the admin's and issuer's authorities and the mutable offchain content.

Each successful `setBaseURI` MUST emit `BatchMetadataUpdate(1, lastIssuedTokenId)` when cards exist. Only the issuer MUST be permitted to call `notifyMetadataUpdate`: a single-token range MUST emit `MetadataUpdate`, otherwise `BatchMetadataUpdate`, with inclusive endpoints. Issuers MUST notify every offchain JSON metadata change as ORC-48 requires.

Calls MUST revert with the declared errors as follows:

- `Unauthorized`: a caller other than the issuer calls `issue` or `notifyMetadataUpdate`, or a caller other than the admin calls `setIssuer` or `setBaseURI`.
- `InvalidCharacterId`: the character ID breaks the format rule above.
- `CharacterAlreadyIssued`: the character ID already has a card.
- `InvalidCreator`: the creator is the zero address.
- `SignatureExpired`: `block.timestamp > deadline`.
- `InvalidSignature`: the creator's signature fails verification.
- `UnknownToken`: `character` or `tokenURI` is called for a card number that was never issued.
- `InvalidIssuer`: `setIssuer` is given the zero address.
- `InvalidBaseURI`: `setBaseURI` is given a URL that breaks the base URL rule.
- `InvalidRange`: a notification range does not satisfy `1 <= fromTokenId <= toTokenId <= lastIssuedTokenId`.

Error precedence is unspecified when several conditions fail. ERC-721 errors and receiver failures keep their upstream behavior.

## Rationale

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) permits open registration and holder-controlled agent URI changes. A dedicated registry instead preserves the issuing platform's character association across transfers. [ENS](https://docs.ens.domains/registry/ens/) separates stable records from replaceable resolvers; one mutable base URL uses that separation without adopting ENS interfaces. [Olas registries](https://github.com/valory-xyz/autonolas-registries) retain hashes of agent components; this registry retains only an initial text commitment. Creator signatures prevent a leaked issuer key from attributing issuance to a real creator without that wallet's authorization.

## Backwards Compatibility

This adds a new collection without changing existing contracts. Characters created before a registry exists MAY receive cards under the same authorization rules; their registration time MUST be the issuance time, not the time the character was made.

## Test Cases

Each canonical form below is hashed as UTF-8 without a trailing newline. Inputs, byte encodings, selector arithmetic, and verification limits are in the [verification record](../assets/orc-51/verification.md).

`keccak256("IssueCharacter(string characterId,address creator,bytes32 initialFingerprint,uint256 deadline)")` MUST equal `0x3caa5fd2d7e3eff424e2c682c9590e6dfd02d2b6940bf5565609d9bb4928927a`.

| Vector | Canonical form | keccak256 |
| --- | --- | --- |
| ASCII | `{"description":"A guide.","name":"Ada"}` | `0xde15b1a45d9e298de5c7dac36fb3fff5698258f1cb7a3ee90b4164aaa4f24701` |
| Korean | `{"description":"함께 이야기해요.","name":"하늘"}` | `0xe41d7242a60e99f0efe9b2bdb75eb9c6885ffd0c56eb5e33fbbe0c5e07bab1a0` |
| Escapes and ordering | `{"aliases":["Guide",{"label":"Companion"}],"text":"Quote: \" Backslash: \\ Newline:\n"}` | `0x0ea0cae29925960577d1c23c614d5f523d6525e14c10e53d6fbfc12c0dd8d0d1` |

| Case | Expected result |
| --- | --- |
| Non-issuer calls `issue` | `Unauthorized`; no state change. |
| Issue valid authorization, then repeat its ID | First mints to creator; second reverts with `CharacterAlreadyIssued`, even after transfer or issuer rotation. |
| Wrong creator, altered signed field/domain, invalid ERC-1271 result, or expired signature | Reject; no state change. Deadline equality succeeds with valid authorization. |
| Authorized ERC-721 transfer | Change holder and clear approvals; preserve number and `Character` fields. |
| Admin changes base URL with two cards | Both URIs change; fixed records stay identical; emit batch range `[1,2]`. |
| Any caller attempts fixed-field mutation or burning | No permitted entry point; records remain fixed. |
| Issuer notifies `[1,1]`, `[1,2]`, or `[0,2]` | Single event, batch event, or `InvalidRange`, respectively. |

These are conformance cases, not passing contract tests.

## Implementation and Activation

Planned components are a ONEchain registry and an issuer's signing, fingerprint, and metadata services. Network selection, implementation revision, deployment address, and activation condition are undecided. No implementation, runtime test, or deployment was verified. Before Review, resolve the unfinished issuer formats and pin upstream revisions; before Final, supply implementation and interoperability evidence under [OIP-1](../OIPs/oip-1.md). Deployment requires issuer coordination, not a protocol fork; publication does not authorize deployment.

## Security Considerations

Production admin SHOULD require multiple signers. Admin compromise can redirect every card or replace issuance authority. Issuer rotation does not invalidate unused creator authorizations. Signatures prove wallet authorization, not authorship or legal rights; fingerprints prove a byte commitment, not text quality or originality. A fingerprint can only be checked against the originals the issuer keeps. Unavailable or malicious metadata does not change ownership; consumers MUST apply ORC-48's retrieval and rendering safeguards. Implementers MUST prevent callbacks from bypassing uniqueness or fixed records.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
