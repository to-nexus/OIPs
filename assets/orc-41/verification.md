# ORC-41 Implementation Verification

This record describes source inspection performed for [ORC-41](../../ORCs/orc-41.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [cross-account-contracts `src/modules/SessionKeyValidator.sol` at 1da203b][account-src-modules-sessionkeyvalidator-sol] | Session installation forms, policy checks, and removal on uninstall. |
| [cross-account-contracts `src/modules/SessionKeyStorage.sol` at 1da203b][account-src-modules-sessionkeystorage-sol] | Storage bounds and target and selector matching. |
| [cross-account-contracts `src/modules/SpendingLimitHook.sol` at 1da203b][account-src-modules-spendinglimithook-sol] | Execution-time accounting and covered transfer forms. |
| [cross-account-contracts `src/modules/SpendingLimitStorage.sol` at 1da203b][account-src-modules-spendinglimitstorage-sol] | Period reset and limit updates. |
| [cross-account-contracts `src/modules/SessionKeyModule.sol` at 1da203b][account-src-modules-sessionkeymodule-sol] | Combined validator and hook roles, per-session spending limits, and the EntryPoint v0.9 requirement. |

## Calculation Checks

The budget boundary examples (limit 100, spent 70, next amount 31) were checked by hand.
These are arithmetic checks, not output from running an implementation.

## Verification Limits

Module combinations other than those listed were not reviewed.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[account-src-modules-sessionkeyvalidator-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SessionKeyValidator.sol
[account-src-modules-sessionkeystorage-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SessionKeyStorage.sol
[account-src-modules-spendinglimithook-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SpendingLimitHook.sol
[account-src-modules-spendinglimitstorage-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SpendingLimitStorage.sol
[account-src-modules-sessionkeymodule-sol]: https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SessionKeyModule.sol
