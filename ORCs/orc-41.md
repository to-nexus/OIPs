---
orc: 41
title: Session Permissions and Spending Policies
description: Scoped account authority and explicit enforcement limits for ONEchain session modules.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
requires: 40
---

# ORC-41: Session Permissions and Spending Policies

## Abstract

This proposal describes the inspected OneAccount session-key and spending-hook profiles and proposes consumer requirements for restricted authority.
It is an integration and disclosure profile of the reference modules and allocates no shared policy ABI.
It builds on [ORC-40](orc-40.md) without claiming that every allowed call has a globally bounded asset effect.

## Motivation

A short-lived signing key is not necessarily a restricted key.
Wallets must expose the actual policy, including wildcard targets, bypass paths, and operations the spending implementation does not account for.

## Specification

### Authority and Lifecycle

Use [ERC-7579](https://eips.ethereum.org/EIPS/eip-7579) lifecycle interfaces and the deployed module's versioned policy encoding.
A session MUST identify the account, module, signing key, validity range, allowed calls, and any separately installed spending policy.
Policy creation, replacement, revocation, and module removal MUST use the account's authorized control path.
Consumers MUST recheck the active module and policy before treating a stored session as usable.
The inspected SessionKeyValidator removes every session on uninstall; it grants no automatic authority after reinstallation.

The reference installation accepts either `abi.encode(sessionKey, validUntil, validAfter)` or that tuple extended with `targets`, `selectors`, and `allowEthTransfers` arrays.
The arrays are positional: each target has a selector list and native-value permission.
The reference storage bounds are six sessions per account, six targets per session, and eight selectors per target.
These are this module profile's limits, not universal ERC-7579 limits.
Use the exact declared module ABI and validity semantics; another permission module is not interchangeable solely because both use a session key.

### Target and Selector Policy

The reference checks an account `execute(bytes32,bytes)` request.
With target policies present, it accepts single or batch call types and checks every call.
An exact target entry takes precedence over the `address(0)` wildcard entry.
Within an entry, `bytes4(0)` is the selector wildcard.
A value-bearing call with function data requires both selector permission and `allowEthTransfer`; a plain nonzero-value transfer uses the value permission.
A zero-value call without a function selector does not pass the scoped policy.

A session with no target policies is not restricted by this module.
Wallets MUST present such a session as full account authority and obtain explicit owner consent before installing it.
Validity is returned to EntryPoint for operations and checked by the validator for message signatures.
For this session-key profile, zero `validAfter` means immediate validity and zero `validUntil` means no expiry.
Message signatures accept both nonzero bounds inclusively, but EntryPoint v0.8 and v0.9 reject an operation at `block.timestamp == validAfter`, so an operation becomes valid one second after a message signature does.
Wallets MUST NOT use a session key to answer application signature requests unless the session's declared purpose includes them; message signatures follow ORC-40.

### Spending Hook Profile

The inspected SpendingLimitHook accounts during execution, rather than during operation validation.
Its limits are configured per account and apply to every hooked execution, whichever validator authorized it; they are not per-session limits.
It is installed with either `abi.encode(uint256 nativeLimit, uint32 duration)` for native ONE only or `abi.encode(address[] assets, uint256[] limits, uint32[] durations)`.
The pinned revision also contains SessionKeyModule, which acts as both a session validator and a hook, keeps spending limits per session key, and accepts only EntryPoint v0.9.
Because the account accepts one hook ([ORC-40](orc-40.md)), SpendingLimitHook and the hook role of SessionKeyModule cannot be installed together.
A wallet MUST identify which module enforces each displayed limit.
`address(0)` identifies native ONE in this hook's asset configuration.
An asset limit has a positive raw-unit amount and positive duration; assets without a configured limit are not capped by this hook.
The first period begins when the limit is configured.
On a later accounted spend at or after `periodStart + duration`, the reference resets spending and starts the next period at that call's timestamp.
Changing an existing limit preserves spending and requires the same duration; removing and recreating a limit resets its state.

Coverage is deliberately limited to:

- Native value in decoded single and batch executions.
- Direct token `transfer` amounts.
- Direct token `transferFrom` amounts when the source is the account itself.

Token movements in other forms are not counted by this hook.
Its pre-check counts attempted decoded amounts, so a failed call in try mode can still consume budget.
A revert that unwinds the whole hooked execution also unwinds its spending update.

### Proposed Restricted-Session Integration

A wallet advertising a bounded session MUST disclose the policy and all known uncovered paths.
It MUST reject or separately authorize account self-management, approvals, module changes, delegatecall, and nested-call targets that can bypass the advertised bounds unless a verified policy covers them.
Targets equal to the account itself, the session validator, or the spending hook MUST be treated as module changes, because those modules accept configuration calls from the account.
This is an additional integration requirement; the reference modules are not claimed to enforce it universally.
Rolling-period logic MUST remain outside [ERC-7562](https://eips.ethereum.org/EIPS/eip-7562)-restricted validation paths.
The reference PermissionsValidator uses a distinct lifetime allowance design; it is not specified as the same rolling-period module here.

## Rationale

Documenting exact coverage makes sessions usable without presenting a selector filter as an arbitrary-call asset firewall.
Keeping authorization and execution-time accounting distinct matches their different validation constraints.

## Backwards Compatibility

Existing unrestricted sessions retain their implementation behavior; this Draft does not silently narrow or revoke them.
New wallet restrictions may reject a previously available flow and require an explicit policy migration.
No universal module ABI or new module type is allocated.

## Test Cases

| Case | Expected result |
| --- | --- |
| Batch contains one disallowed target/selector | Scoped validator rejects the operation. |
| Exact target denies a selector but wildcard permits it | Exact target policy governs; reject. |
| Session has no target policies | Present full account authority and require explicit consent. |
| Module is removed | Previously stored sessions cease to authorize calls. |
| Message signed at either nonzero time boundary | Apply the inclusive session validity window. |
| Operation at exactly a nonzero `validAfter` | Reject at EntryPoint; accept from the next second. |
| Session policy targets the session validator or spending hook | Treat it as a module change requiring separate authorization. |
| Application requests a signature from a session key | Refuse unless the session's declared purpose includes it. |
| Limit 100, spent 70; next accounted amount 31 | Reject within the current period. |
| Same limit; first spend at the reset boundary | Reset before accounting the new spend. |
| Token movement outside the covered forms | Do not report it as capped spending. |
| Try-mode call fails after pre-check | Verify the disclosed attempted-spend accounting. |

These are required module and wallet tests, not new runtime results.

## Reference Implementation

References to `to-nexus/cross-account-contracts` are [internal verification sources](../README.md#verification-sources) and require access to the cited repositories.

- [SessionKeyValidator](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SessionKeyValidator.sol) and [SessionKeyStorage](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SessionKeyStorage.sol).
- [SessionKeyModule](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SessionKeyModule.sol).
- [SpendingLimitHook](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SpendingLimitHook.sol) and [SpendingLimitStorage](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/SpendingLimitStorage.sol).

Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-41/verification.md).

## Implementation and Activation

This proposal is intended for Final registration under [OIP-1's retrospective path](../OIPs/oip-1.md#documenting-existing-deployed-behavior); requirements that the referenced implementations do not meet must be implemented or moved to a separate proposal before then.
Before that registration, choose the supported module combination and validate restricted-session behavior through actual account, executor, hook, and EntryPoint paths.
Complete bypass and revocation tests before claiming a bounded spending product.
This Draft installs or revokes no module.

## Security Considerations

Wildcard targets, trusted executors, self-calls, mutable target contracts, approvals, and hook removal can expand effective authority.
A filter over direct calls cannot by itself guarantee a cap on all downstream token movements.
Session UI must reflect this limit and require deliberate consent for broad authority.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
