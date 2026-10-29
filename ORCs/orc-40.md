---
orc: 40
title: Modular Smart Account Interoperability
description: A OneAccount profile for account variants, module authorization, execution, nonce routing, and signature validation.
author: ONEchain Contributors
status: Draft
type: Standards Track
created: 2026-10-29
---

# ORC-40: Modular Smart Account Interoperability

## Abstract

This proposal defines the inspected OneAccount integration profile using [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) and [ERC-7579](https://eips.ethereum.org/EIPS/eip-7579).
It records account variants, EntryPoint binding, validator selection, and execution differences needed by modules, wallets, and bundlers.
It also defines the OneAccount [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) signature envelope and separates it from operation signatures.

## Motivation

Implementing common module methods does not make every account support the same execution modes or initialization path.
Wallets, token contracts, and applications also need the same interpretation of a signature's validator and signed message.
A shared profile must preserve those distinctions while giving consumers predictable account and validator identities.

## Specification

### Upstream Surface and Deployment Identity

Adopt the referenced account/module interfaces by reference, with the OneAccount selections below.
The upstream ERC-7579 proposal remains Draft at the time of preparation; a dependency version MUST be pinned before conformance review.
Consumers MUST identify chain, account address, implementation or delegate, factory where applicable, EntryPoint address/version, and installed validator.
The account's configured EntryPoint MUST match the wallet, bundler, and paymaster configuration.

| Variant | EntryPoint | Initialization and upgrades |
| --- | --- | --- |
| OneAccount proxy | Each implementation is bound at construction to one supported EntryPoint, v0.8 or v0.9; changing it requires a UUPS upgrade. | Factory derives an ERC-1967 proxy address from salt, implementation and initialization data; UUPS authorization is EntryPoint-or-self. |
| OneAccount7702 | Bound to v0.9. | Initialized through that EntryPoint's sender creator; delegation changes follow EIP-7702 authority. |

[OIP-29](../OIPs/oip-29.md) covers protocol code delegation.
The delegation authorization reaches the chain only inside a type `0x04` transaction, which a bundler submits with the operation's `eip7702Auth`; [OIP-2](../OIPs/oip-2.md) fee delegation cannot carry it.
An EIP-7702 authorization signer and the account's operation validator can be different principals and MUST NOT be conflated.
Factories MUST initialize the intended validator atomically with deployment.
Initialization of a delegated account MUST be authorized by the delegating account's own key, not only by the contract that delivers it.
Changing initialization data changes the derived address; clients MUST query or reproduce the matching factory derivation.

### Delegated Accounts

An account delegated under EIP-7702 keeps its EOA key as an independent authority:

- The EOA can send transactions to its own address, which the account accepts as self-calls, including module and trusted-executor changes.
- Verifiers that recover an ECDSA signer accept the EOA key for the account address, while the account's `isValidSignature` routes only through installed validators.
- Module storage is not cleared when the delegation changes; returning to the same delegate restores the earlier validators, executors, and sessions.

Wallets MUST present the EOA key as full account authority, MUST NOT treat removal of a validator as revocation of that key, and MUST inspect existing module state before delegating to an account implementation.

### Modules and Authority

Use ERC-7579 module types: validator, executor, fallback, and hook.
Installation and removal follow account-authorized lifecycle calls; module data is interpreted by that module's declared version.
The reference counts installed validators and rejects removal of the last one.
The inherited hooked account accepts at most one installed hook, so hook-based policies cannot be combined by installing several hooks.
Consumers MUST verify installation before selecting a validator and MUST NOT treat a module address supplied by an application as account authority.

`executeFromExecutor` accepts either an installed executor or the explicitly configured trusted DelegationManager.
The latter is an additional privileged path, not evidence that any delegation service is trusted.
Changes to trusted executors, validators, hooks, delegates, and implementation versions require the corresponding account authorization.

### Deviations from ERC-7579

The reference differs from ERC-7579 as follows, and consumers MUST NOT assume the upstream behavior:

- `uninstallModule` completes even when the module's `onUninstall` call fails, whereas ERC-7579 requires a revert.
- `executeFromExecutor` also accepts the trusted DelegationManager, which is not an installed executor; `isModuleInstalled` reports false for it, so clients MUST read `trustedDelegationManager()` to discover it.
- `supportsExecutionMode` checks only the call type and execution type and ignores the mode selector and payload; static calls are not supported.

### Execution Modes

The inspected proxy profile supports single, batch, and delegatecall call types with default and try execution modes through its inherited implementation.
OneAccount7702 rejects delegatecall in both capability discovery and execution.
Clients MUST check `supportsExecutionMode` for the intended variant; module installation does not override this rejection.
Default failure propagation and try-mode behavior MUST be disclosed to applications; a try-mode batch MUST NOT be presented as atomic execution.
Native value remains the account's obligation even when gas is sponsored.

### Nonce and Operation Signatures

A conforming OneAccount MUST interpret the 32-byte operation nonce as `validatorAddress[20] || key[4] || sequence[8]` in big-endian order and validate the operation with that installed validator.
Equivalently, the 192-bit EntryPoint nonce key is `(uint160(validator) << 32) | key`, with a 64-bit sequence supplied by EntryPoint.
This is a OneAccount implementation choice, not a universal ERC-7579 encoding.

The operation signature contains the validator's signature bytes; it does not use the 20-byte message-signature prefix below.
The selected installed validator receives the EntryPoint operation digest without an added personal-message prefix.
Reading a nonce does not reserve it against another submission.

### Message Signatures

Use `isValidSignature(bytes32,bytes)` and its success value by reference to ERC-1271.
Only `0x1626ba7e` is successful verification; another value, malformed return, or failed call MUST NOT be accepted.
Verification MUST use the account address and its current state, not merely recover a signer and compare it with an assumed owner.
Consumers MUST NOT assume that a signature valid at one block remains valid after a validator or account configuration change.

A conforming OneAccount MUST accept application signatures of the form `validatorAddress[20] || validatorSignature` and pass the remaining bytes to that installed validator.
The address is raw packed bytes without ABI padding.
The reference account returns failure for an envelope shorter than 20 bytes, an uninstalled validator, or a reverting validator call.
The validator defines its inner signature encoding; a 65-byte ECDSA signature is only one supported implementation choice, for which the complete envelope is 85 bytes.
Applications MUST NOT strip, add twice, or replace the routing prefix after approval.
The reference ECDSA validator verifies the supplied digest directly.
The SDK's `signHash` produces the inner signature; `signMessage` hashes a personal message and adds the routing prefix.
Token permit handling instead signs the token's typed-data digest and then adds the same prefix.

### Signed-Message Domains

The consuming application MUST define the message purpose, chain, verifying contract, intended account, nonce or replay identifier, and expiry where applicable.
[EIP-712](https://eips.ethereum.org/EIPS/eip-712) provides typed-data hashing and domain construction; replay state remains the application's responsibility.
For an existing ERC-defined message, preserve that ERC's exact digest and fields unless signer and verifier have negotiated an extension below.
A profile missing intended-account binding MUST NOT claim protection against replay across accounts sharing the same signer.
Personal-message signatures, typed approvals, session authorizations, and UserOperation signatures are separate domains.

[ERC-6492](https://eips.ethereum.org/EIPS/eip-6492) counterfactual verification and [ERC-7739](https://eips.ethereum.org/EIPS/eip-7739) defensive rehashing are optional profiles.
Neither is implied by the baseline account envelope or established as implemented here.
An extension MUST define how signers and verifiers negotiate it, how its encoding is distinguished, and how the underlying validator is selected.
An undeployed address MUST NOT be accepted merely because an off-chain signer claims it will use a compatible account.
Existing signatures MUST NOT be silently reinterpreted under a new extension.

### Validation and Session Extensions

Bundler acceptance requires the applicable [ERC-7562](https://eips.ethereum.org/EIPS/eip-7562) validation rules and supported EntryPoint behavior, in addition to contract-level validation.
Module support alone does not prove that a validator is admissible in a public mempool.
[ORC-41](orc-41.md) separately defines restricted session authority and its coverage limits.

## Rationale

A variant matrix keeps one shared interface while exposing the delegated account's different authority and storage model.
Explicit nonce routing avoids ambiguity between account operation signatures and application message signatures.
Explicit message routing allows different validators to coexist without imposing a universal signature length, while digest rules stay with the consuming application.

## Backwards Compatibility

Existing account addresses, validators, and delegated EOAs are not migrated by publication.
Consumers that assume a universal owner getter, identical delegatecall support, or a 65-byte account signature need explicit adaptation.
An implementation upgrade that changes EntryPoint or routing must be treated as an integration change.
Adding defensive rehashing or counterfactual support requires coordinated signer and verifier changes.

## Test Cases

| Case | Expected result |
| --- | --- |
| Factory and client use identical salt and initialization data | Predict the same account address. |
| Change validator initialization data | Derive the corresponding different deployment address. |
| Last installed validator is removed | Reject. |
| Uninstalled executor without trusted-manager status | Reject. |
| Delegatecall requested from OneAccount7702 | Report unsupported and reject execution. |
| Validator address, key, and sequence encoded into nonce | Recover exactly the original three fields. |
| Second hook installation | Reject. |
| Query `isModuleInstalled` for the trusted DelegationManager | Return false; discover it through `trustedDelegationManager()`. |
| Wallet and account EntryPoints differ | Reject preparation or submission. |
| Installed ECDSA validator with 65-byte inner signature | Verify the 85-byte envelope against the intended digest. |
| Envelope shorter than 20 bytes or uninstalled validator | Reject. |
| Validator reverts or returns the wrong magic value | Reject. |
| Validator is removed or its signer changes | Re-evaluate against current account state. |
| Token permit is signed as a personal message instead | Do not accept it as the original typed approval. |
| Application digest without account binding | Do not claim protection against replay across accounts. |
| Counterfactual wrapper without an advertised verifier profile | Report unsupported verification. |

These cases require factory, module, signature, and real EntryPoint tests; this Draft reports no new runtime run.

## Reference Implementation

- [OneAccountBase](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccountBase.sol), [proxy implementation](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccount.sol), [factory](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccountFactory.sol), and [7702 variant](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/OneAccount7702.sol).
- [ECDSA validator](https://github.com/to-nexus/cross-account-contracts/blob/1da203bda9dc3f6cd53b74ef0b7b330c80f8833a/src/modules/ECDSAValidator.sol).
- [SDK account methods](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/account/accountMethods.ts), [nonce encoding](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/utils/userOp.ts), and [permit routing](https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts).

Inherited behavior, including the account's ERC-1271 dispatch, was inspected in the repository's OpenZeppelin 5.6.0 dependency selected by its remappings.
Implementation checks and their scope are recorded in the separate [verification record](../assets/orc-40/verification.md).

## Implementation and Activation

Before Review, publish supported implementation/factory/delegate addresses and code revisions for each EntryPoint variant.
Validate module discovery, nonce routing, initialization, upgrade authorization, supported execution modes, and supported validator signature encodings with the intended bundler and at least one consuming application and permit token.
Choose any optional signature extension through a separate compatibility review.
The contracts are compiled for the Prague EVM target and use transient storage; on ONEchain they require the instructions enabled by [OIP-17](../OIPs/oip-17.md), and OneAccount7702 also requires OIP-29.
The Draft deploys no account and does not establish production compatibility.

## Security Considerations

Executors, hooks, validators, and trusted managers can exercise significant account authority.
Initialization races, mismatched EntryPoints, unsafe delegatecall, and upgrades can compromise that authority.
Operation validation and successful simulation do not replace explicit user authorization for module and delegation changes.
A validator prefix routes a request but does not prove its intended use.
Applications must verify the exact account and digest at the state relevant to execution.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
