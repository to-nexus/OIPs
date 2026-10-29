# ORC-46 Implementation Verification

This record describes source inspection performed for [ORC-46](../../ORCs/orc-46.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [bridge-contracts `src/token/CrossMintableERC20V2.sol` at b6be327][bridge-src-token-crossmintableerc20v2-sol] | Metadata, minter authority, legacy mint and burn methods, and absence of upgradeability. |
| [bridge-contracts `src/BaseBridge.sol` at b6be327][bridge-src-basebridge-sol] | How the bridge mints to and burns from its own address. |

## Calculation Checks

The 18-to-6 decimal conversion example was checked by hand.
These are arithmetic checks, not output from running an implementation.

## Verification Limits

No ERC-7802 adapter or end-to-end bridge route was established.
ERC-7802 was Draft when consulted.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[bridge-src-token-crossmintableerc20v2-sol]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/CrossMintableERC20V2.sol
[bridge-src-basebridge-sol]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/BaseBridge.sol
