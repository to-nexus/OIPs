# ORC-40 Implementation Verification

This record describes source inspection performed for [ORC-40](../../ORCs/orc-40.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [cross-account-contracts `src/OneAccountBase.sol` at 1da203b][account-src-oneaccountbase-sol] | EntryPoint binding, validator routing, last-validator protection, executor authorization, and ERC-1271 dispatch. |
| [cross-account-contracts `src/OneAccount.sol` at 1da203b][account-src-oneaccount-sol] | UUPS upgrade authorization. |
| [cross-account-contracts `src/OneAccountFactory.sol` at 1da203b][account-src-oneaccountfactory-sol] | Proxy address derivation and initialization. |
| [cross-account-contracts `src/OneAccount7702.sol` at 1da203b][account-src-oneaccount7702-sol] | EntryPoint v0.9 binding and delegatecall rejection. |
| [cross-account-contracts `src/modules/ECDSAValidator.sol` at 1da203b][account-src-modules-ecdsavalidator-sol] | Direct digest verification. |
| [one-account-sdk `src/account/accountMethods.ts` at 21b0565][sdk-src-account-accountmethods-ts] | `signHash` and `signMessage`. |
| [one-account-sdk `src/utils/userOp.ts` at 21b0565][sdk-src-utils-userop-ts] | Nonce encoding. |
| [one-account-sdk `src/client/tokenPaymaster.ts` at 21b0565][sdk-src-client-tokenpaymaster-ts] | Permit signature routing. |

## Calculation Checks

The 85-byte envelope size and the nonce packing in the proposal were checked by hand.
These are arithmetic checks, not output from running an implementation.

## Verification Limits

The account's OpenZeppelin 5.6.0 and EntryPoint 0.9.0 dependencies, selected by its remappings, were inspected but not rebuilt or authenticated against release hashes.
The single-hook rule, the `supportsExecutionMode` checks, and the `uninstallModule` behavior were read from that OpenZeppelin dependency.
ERC-7579 and ERC-7739 were Draft when consulted.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[account-src-oneaccountbase-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccountBase.sol
[account-src-oneaccount-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccount.sol
[account-src-oneaccountfactory-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccountFactory.sol
[account-src-oneaccount7702-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccount7702.sol
[account-src-modules-ecdsavalidator-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/ECDSAValidator.sol
[sdk-src-account-accountmethods-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/account/accountMethods.ts
[sdk-src-utils-userop-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/utils/userOp.ts
[sdk-src-client-tokenpaymaster-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts
