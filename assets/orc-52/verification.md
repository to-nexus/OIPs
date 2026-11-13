# ORC-52 Implementation Verification

This record supports [ORC-52: Native Asset Vaults](../../ORCs/orc-52.md).
It records source inspection on 2026-11-04, not test execution or deployment verification.

## Sources

The inspected checkout was `stake-one-contracts` at `fce3934dc8d980aac5eb1ecca094cfd3985f0f69`.
The normative starting point was [ORC-47](../../ORCs/orc-47.md), with the [ORC-20](../../ORCs/orc-20.md) share interface.
[ERC-4626](https://eips.ethereum.org/EIPS/eip-4626), [ERC-7528](https://eips.ethereum.org/EIPS/eip-7528), and [ERC-7535](https://eips.ethereum.org/EIPS/eip-7535) were consulted on 2026-11-04.

## Correspondence to NativeVault

| Source | Relationship to the draft |
| --- | --- |
| [Native marker and share offset][identity] | Uses the native marker and an offset of 6; the source describes shares with 24 decimals. The draft permits this scale without mandating it. |
| [Initialization][initialize] | Initializes ERC-20 share metadata and the ERC-4626 asset field with the native marker. |
| [Valuation and fee accounting][accounting] | Reads managed principal plus rewards and mints performance-fee shares. The draft requires a disclosed policy without standardizing this strategy or fee formula. |
| [Conversions and limits][limits] | Includes pending fee dilution in quotes; standard deposit and mint capacity are zero. Withdrawal capacity currently concerns transferable stake, which is not native liquidity. |
| [Native deposit overloads][deposit] | Uses `msg.value`, checks capacity and minimum amount, quotes before crediting assets, and enforces `minShares`. These signatures are retained. |
| [Disabled standard deposit and mint][disabled] | Both revert with `NativeAssetOnly`, matching the dedicated deposit interface. |
| [Asset movement hooks][hooks] | Entry invests native ONE; exit transfers a staking position. The exit does not provide the draft's native payment. |

## Basis Versus Conformance

The draft extracts a reusable native asset interface and accounting contract from the source.
It leaves `depositStake`, `DelegationPool`, and `transferStake` outside its normative interface.
These are strategy-specific paths in the inspected implementation, including its current withdrawal path.

The current source cannot become a conforming native settlement implementation merely by ignoring those paths in documentation.
It would need a native payment path and withdrawal limits based on the native funds it can actually deliver.
Its valuation and capacity reads also depend on external contracts; their availability and compliance with the adopted view requirements have not been established here.
Alternatively, the existing strategy can use the common design as background while separately specifying its position settlement behavior, without claiming full conformance.

## Verification Limits

No contract source was changed.
No Solidity test, build, fork execution, live-chain query, or deployment audit was run.
The inspected checkout has no dedicated NativeVault test file, and its configured OpenZeppelin dependencies were not present locally.
The draft's test table describes work required for a conforming implementation; it is not evidence of passing tests.
No full ORC-20, ERC-4626, or fee-accounting conformance audit was performed.
The adopted external specification revisions remain to be pinned before Review.

[identity]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L63-L97
[initialize]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L144-L161
[accounting]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L284-L373
[limits]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L375-L451
[deposit]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L588-L636
[disabled]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L712-L722
[hooks]: https://github.com/to-nexus/stake-one-contracts/blob/fce3934dc8d980aac5eb1ecca094cfd3985f0f69/src/NativeVault.sol#L724-L773
