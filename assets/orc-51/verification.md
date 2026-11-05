# AI Character Registry Specification Verification

This record supports the [Draft proposal](../../ORCs/orc-51.md).
It records specification inspection and local arithmetic on 2026-11-03. It does not establish implementation or deployment conformance.

## Repository Sources

These files were read at repository revision `4f87e88499627e0705ddc698eaa79d62eac7f7ff`.

| Source | Use |
| --- | --- |
| [OIP-1](../../OIPs/oip-1.md) | Document format, ORC conventions, Draft-stage omissions, and Implementation and Activation records. |
| [ORC template](../../templates/orc-template.md) | Metadata fields and section order. |
| [ORC-48](../../ORCs/orc-48.md) | The ERC-721 profile adopted through `requires: 48`, including `contractURI()` disclosures and ERC-4906 notifications for offchain metadata changes. |
| [ORC-42](../../ORCs/orc-42.md) | Precedent for EIP-712 domains and for verifying signatures from EOAs and ERC-1271 contract wallets. |

## External References

These references were not retrieved for this Draft. Their revisions and status must be pinned and inspected before Review.

| Reference | Use in the proposal |
| --- | --- |
| [ERC-721](https://eips.ethereum.org/EIPS/eip-721), [ERC-165](https://eips.ethereum.org/EIPS/eip-165) | Ownership, transfers, approvals, metadata, and interface discovery. |
| [ERC-4906](https://eips.ethereum.org/EIPS/eip-4906), [ERC-7572](https://eips.ethereum.org/EIPS/eip-7572) | Metadata update events and collection metadata, as ORC-48 requires. |
| [EIP-712](https://eips.ethereum.org/EIPS/eip-712), [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) | Creator signatures from EOAs and contract wallets. |
| [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) | Canonical JSON for the fingerprint. |
| [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) | Open registration and holder-controlled agent URIs, contrasted in the Rationale. |
| [ENS registry documentation](https://docs.ens.domains/registry/ens/) | Stable records with replaceable resolvers, cited in the Rationale. |
| [Olas registries](https://github.com/valory-xyz/autonolas-registries) | Hashes of agent components, cited in the Rationale. |

## Arithmetic Checks

Keccak-256 was computed with pycryptodome's `Crypto.Hash.keccak` after two known-answer checks:

| Input | Keccak-256 |
| --- | --- |
| Empty string | `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470` |
| `Transfer(address,address,uint256)` | `ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` |

The fingerprint vectors in Test Cases come from a canonicalizer with these properties:
- it covers strings, objects, and arrays only;
- it sorts object keys by UTF-16 code units;
- it does not normalize Unicode.

Numbers, booleans, null, and the rest of RFC 8785 were not tested. [vectors.json](vectors.json) holds the original inputs, with their keys deliberately out of order, along with their canonical forms, UTF-8 bytes, and hashes.

The EIP-712 typehash and the selectors below were computed the same way. XOR of the ten selectors gives the `IAICharacterRegistry` interface identifier `0x7f6f796a`.

| Function | Selector |
| --- | --- |
| `admin()` | `0xf851a440` |
| `issuer()` | `0x1d143848` |
| `baseURI()` | `0x6c0360eb` |
| `character(uint256)` | `0x468f25b0` |
| `tokenIdOf(string)` | `0xa398d819` |
| `issue(string,address,bytes32,uint256,bytes)` | `0xaa82cdbe` |
| `setIssuer(address)` | `0x55cc4e57` |
| `setBaseURI(string)` | `0x55f804b3` |
| `notifyMetadataUpdate(uint256,uint256)` | `0x512b2bff` |
| `contractURI()` | `0xe8a3d485` |

A second, independently written script reproduced every fingerprint, the typehash, each selector, and the interface identifier.

## Verification Limits

The following were not tested:
- a Solidity implementation;
- a signing wallet or an ERC-1271 wallet;
- a metadata endpoint;
- a deployment.

No complete EIP-712 domain separator or signed-digest vector was computed. The behavior table in Test Cases lists required conformance work. It does not record passing tests.
