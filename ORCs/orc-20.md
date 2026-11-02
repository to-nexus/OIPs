---
orc: 20
title: Fungible Token Standard
description: An ERC-20 extension with required metadata and interoperability rules for ONEchain token contracts.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
---

# ORC-20: Fungible Token Standard

## Abstract

ORC-20 defines a fungible token contract standard for ONEchain by extending [ERC-20][erc20].
It preserves ERC-20's transfer, approval, allowance, and event interfaces, and requires the metadata methods `name()`, `symbol()`, and `decimals()`.
It also defines metadata stability, token identification, and call-result handling for applications integrating these contracts.

The proposal follows [BEP-20][bep20]'s approach of adding ecosystem requirements to ERC-20.
It is an application-level contract standard and requires no consensus change.

## Motivation

Wallets, exchanges, and indexers need a predictable interface for displaying and transferring fungible tokens.
ERC-20 leaves its metadata methods optional, so an ERC-20 implementation alone does not guarantee that applications can retrieve a token's display information.
ORC-20 makes these methods part of the required contract interface while retaining compatibility with existing ERC-20 integrations.

Tokens may have different issuance and administration models.
A shared base standard should support those models without prescribing a particular owner, minter, bridge, or supply schedule.

## Specification

### Relationship to ERC-20 and BEP-20

An ORC-20 contract MUST implement the Final ERC-20 specification, with the additional requirements in this proposal.
Unchanged ERC-20 behavior is adopted by reference rather than redefined here.
Existing function selectors, argument types, return types, event signatures, and indexed event parameters MUST remain compatible.

| Requirement | ERC-20 | BEP-20 | ORC-20 |
| --- | --- | --- | --- |
| Transfers, balances, allowances, and standard events | Required | Retained | Retained |
| `name()` | Optional | Optional | Required |
| `symbol()` | Optional | Required | Required |
| `decimals()` | Optional | Required | Required and stable for the contract address |

The BEP-20 comparison refers to its published proposal, not to additional interfaces in individual token templates or bridge tools.
Its historical cross-chain supply conventions are not adopted by ORC-20.
The requirements below define ONEchain's extension.

### Contract Interface

Every conforming token MUST expose the following ABI:

```solidity
/// @title IORC20
/// @notice Required interface for an ORC-20 fungible token.
interface IORC20 {
    /// @notice Emitted for a token transfer, including a zero-value transfer.
    event Transfer(address indexed from, address indexed to, uint256 value);

    /// @notice Emitted when an owner sets a spender's allowance.
    event Approval(address indexed owner, address indexed spender, uint256 value);

    /// @notice Returns the token's display name.
    function name() external view returns (string memory);

    /// @notice Returns the token's display symbol.
    function symbol() external view returns (string memory);

    /// @notice Returns the number of decimal places used for display.
    function decimals() external view returns (uint8);

    /// @notice Returns the outstanding supply accounted for by this contract.
    function totalSupply() external view returns (uint256);

    /// @notice Returns the token balance of an account.
    function balanceOf(address account) external view returns (uint256);

    /// @notice Transfers tokens from the caller to a recipient.
    function transfer(address to, uint256 value) external returns (bool);

    /// @notice Returns the remaining allowance granted to a spender.
    function allowance(address owner, address spender) external view returns (uint256);

    /// @notice Sets the caller's allowance for a spender.
    function approve(address spender, uint256 value) external returns (bool);

    /// @notice Transfers tokens from an account using the caller's spending authorization.
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}
```

This is an interface declaration, not a token implementation or a required Solidity inheritance hierarchy.
An existing implementation may conform without inheriting an interface named `IORC20`.
ORC-20 defines no additional interface-discovery method or ERC-165 identifier.

### Required Metadata

`name()` and `symbol()` MUST return ABI-encoded Solidity strings; a `bytes32` return value does not satisfy these methods.
`decimals()` MUST return an ABI-encoded `uint8`.
These methods MUST be callable without privileged authorization and MUST succeed for an initialized, conforming token.

The name and symbol SHOULD be nonempty and suitable for display.
This standard imposes no fixed symbol length, uppercase requirement, or uniqueness requirement.
Applications MUST treat both strings as untrusted display data.

`decimals()` defines the display scale: a raw amount `a` represents `a / 10^d` display units when `d = decimals()`.
It does not scale the arguments or results of balance, supply, transfer, or allowance methods.
Tokens are not required to use 18 decimals; zero and other `uint8` values are valid.
Consumers MUST preserve integer precision and MUST NOT assume that `10^d` fits in a 256-bit integer for every valid `d`.

The decimals value MUST remain unchanged for the lifetime of a token address, including through implementation upgrades.
Name or symbol changes MAY be supported, but the issuer MUST document that policy and the authority able to make those changes.
No metadata-change event is required by this base standard, so consumers must not assume that cached names and symbols remain current indefinitely.

### Calls, Events, and Failure Handling

`transfer`, `transferFrom`, and `approve` MUST return an ABI-encoded boolean on a successful EVM call.
Successful token operations return `true`.
A rejected operation MAY revert or return `false`; a `false` result MUST leave token balances, supply, and allowances unchanged and MUST NOT emit a success event for that operation.
This atomic-failure requirement is an explicit ORC-20 clarification for integrations.

Callers MUST handle both a revert and a decoded `false` as failure.
Empty return data, malformed return data, or an EVM call that succeeds without executing a token operation MUST NOT be interpreted as evidence of ORC-20 conformance.
Applications may separately support legacy token conventions, but those compatibility paths do not change this standard's required return types.

ERC-20's event requirements remain in force, including `Transfer` for successful zero-value transfers and `Approval` for successful `approve` calls.
Approving a new value replaces the previous allowance; consumers must account for the existing ERC-20 allowance-update race.
ORC-20 does not require an `Approval` event when an allowance is consumed by `transferFrom`, so event history alone is not an authoritative current allowance.

### Supply and Token Identity

`totalSupply()` MUST report the outstanding supply accounted for by this token contract, using the same raw units as `balanceOf()`.
It MUST NOT substitute an aggregate of independently accounted token supplies on other chains.
Bridge backing and cross-chain issuance accounting require their own specification.

Consumers MUST identify an asset by its chain ID and token contract address.
A name, symbol, decimals value, or matching metadata on another chain does not establish asset identity or backing.
For a proxy token, the token address is the proxy address used for token calls.

Native ONE is not an ORC-20 contract.
The native transfer logs defined by [OIP-3](../OIPs/oip-3.md) do not create ERC-20 balances, approvals, or allowance methods for native ONE.
An indexer MUST distinguish a token contract's `Transfer` events from the native transfer logs identified by that OIP.

### Optional Extensions

Minting, burning, ownership, roles, pausing, signed approvals, and bridge interfaces are optional extensions.
Neither `owner()` nor `getOwner()` is required, and the base standard grants no administrative authority.
Issuers MUST document any additional transfer restrictions, transfer charges, balance adjustments, or upgrade permissions that affect integrations.
Applications MUST assess those behaviors separately; ORC-20 conformance alone does not guarantee suitability for a particular exchange, bridge, or payment service.

Signed approvals, bridged tokens, and token-denominated gas payment require separate interface specifications.
[OIP-2](../OIPs/oip-2.md) changes transaction fee payment and does not add token permit methods or make an ORC-20 token acceptable for gas payment.

## Rationale

Requiring all three metadata methods gives applications one predictable interface without changing ERC-20 selectors.
Requiring `name()` as well as symbol and decimals avoids a separate metadata fallback for an otherwise conforming token.
Stable decimals prevent an upgrade from silently changing the displayed interpretation of existing balances and allowances.

A mandatory owner getter would impose a single-owner model on tokens using roles, multiple administrators, or no administrator.
Keeping administration optional allows those contracts to share the same token interface.
Local supply reporting and address-based identification avoid coupling every fungible token to a particular bridge design.

## Backwards Compatibility

An ERC-20 token that already provides the required metadata and satisfies the additional rules can conform without changing its ABI.
ERC-20 clients can continue to call ORC-20 tokens through their existing interfaces.
Tokens with missing metadata, `bytes32` metadata, empty operation return data, or mutable decimals do not automatically qualify.
They may remain supported as legacy assets by individual applications.

No existing token is renamed, migrated, or upgraded by publication of this proposal.
Changing a deployed token or wrapping it requires a separate deployment decision; a wrapper has its own address and asset identity.

## Test Cases

Use an ordinary token fixture without optional transfer charges or balance adjustments for the balance examples below.
Let accounts `A`, `B`, and spender `S` be distinct nonzero addresses.
Each case is independent, and `B` starts with a zero balance unless otherwise stated.

| Case | Expected result |
| --- | --- |
| Read metadata without privileged credentials | All three methods succeed with `string`, `string`, and `uint8` return types. |
| Missing `name()` or `bytes32` metadata | Does not satisfy ORC-20. |
| Decimals `6`, raw balance `1,234,567` | Display `1.234567`; contract balance remains `1,234,567`. |
| Decimals `0` | Valid; display units equal raw units. |
| Decimals changed by an upgrade | Violates ORC-20 even if transfer selectors remain unchanged. |
| `A` has `100`; `A.transfer(B, 25)` | Return `true`, balances become `75` and `25`, supply is unchanged, and emit `Transfer(A, B, 25)`. |
| Successful zero-value transfer between valid accounts | Return `true`, preserve balances, and emit `Transfer` with value zero. |
| `A` approves `S` for `40`, then approves `S` for `10` | Current allowance is `10`, with an `Approval` event for each successful call. |
| Finite allowance `40`; `S.transferFrom(A, B, 15)` with sufficient balance | Return `true`, transfer `15`, and leave allowance `25`. |
| Insufficient balance or authorization | Reject; a `false` result must preserve token accounting and emit no success event. |
| A token call returns no boolean | Does not satisfy the required operation ABI. |
| Two contracts share a symbol | Treat them as distinct assets by chain ID and address. |
| Native and token transfer logs appear in one receipt | Classify them using their emitting addresses and the applicable specification. |

These are conformance requirements, not a report that existing deployments have passed them.
Optional extensions need additional tests for their own behavior and integration assumptions.

## Reference Implementation

OpenZeppelin's [ERC20 implementation][oz-erc20] and [IERC20Metadata interface][oz-metadata] provide the existing ERC-20 and metadata interfaces used by the inspected token contracts.
They are implementation building blocks; conforming behavior still depends on the derived token and its extensions.

Two inspected implementation examples are:

- [CrossToken at revision f4d1a0c][cross-token], which inherits ERC-20 metadata and adds an owner-only `burn` method and signed approvals.
- [CrossMintableERC20V2 at revision b6be327][bridge-token], which supplies constructor-selected immutable decimals and role-controlled minting and burning.

These source references illustrate different administration and supply models sharing the proposed base interface.
Their legacy names are retained only to identify the source; no deployment or complete ORC-20 conformance is asserted here.

## Implementation and Activation

ORC-20 documents the token interface of the existing contracts cited in [Reference Implementation](#reference-implementation).
It is intended for Final registration under [OIP-1's retrospective path](../OIPs/oip-1.md#documenting-existing-deployed-behavior).
It requires no hardfork or protocol activation timestamp.
Token issuers can assess existing contracts against the specification or implement it in newly deployed contracts.
Wallets, indexers, and services must verify metadata, call results, and any optional extensions for each supported token address.

The interface declaration was compiled with Solidity `0.8.35`; all nine function selectors, return types, mutability declarations, and both event encodings matched `IERC20Metadata`.
Token runtime conformance, deployed contract behavior, and consumer interoperability remain unverified for this proposal.
Final registration requires identifying the deployed token contracts and networks it documents, and recording existing tests or runtime checks for the required metadata, return values, and events.
No token deployment or upgrade is performed by registering ORC-20.

## Security Considerations

Metadata can imitate another asset or contain unsafe display content; applications must sanitize it and display the contract identity when needed.
Incorrect decimal assumptions or floating-point conversions can cause users to approve or transfer the wrong amount.
Metadata caches and proxy upgrades must not hide changes to an asset's behavior or authority.

Approval changes can race with a spender using the previous allowance.
Applications should follow ERC-20's allowance-update guidance and avoid granting unnecessary spending authority.
A successful EVM call is insufficient without checking the required boolean result.

Administrative minting, pausing, restrictions, and upgrades can affect token holders even when the base ABI is compatible.
The standard does not establish economic backing, bridge safety, issuer trustworthiness, or permission to spend a holder's tokens.
Any extension that calls external contracts needs its own reentrancy and authorization review.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).

[erc20]: https://eips.ethereum.org/EIPS/eip-20
[bep20]: https://github.com/bnb-chain/BEPs/blob/master/BEPs/BEP20.md
[oz-erc20]: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.1.0/contracts/token/ERC20/ERC20.sol
[oz-metadata]: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.1.0/contracts/token/ERC20/extensions/IERC20Metadata.sol
[cross-token]: https://github.com/to-nexus/cross-token/blob/f4d1a0c9578838f5ccbdad20294c2e44ddd59cbe/contracts/CrossToken.sol
[bridge-token]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/CrossMintableERC20V2.sol
