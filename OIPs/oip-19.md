---
oip: 19
title: Deterministic Istanbul System Transactions
description: Identification, ordering, execution, receipts, and omission rules for signed consensus system transactions.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-19: Deterministic Istanbul System Transactions

## Abstract

This proposal specifies the signed transactions used by Istanbul consensus to initialize contracts, distribute rewards, update councils, and apply penalties.
These transactions form a deterministic suffix of a block and use a dedicated execution path.

## Motivation

A zero gas price is insufficient to identify a consensus operation.
Clients must reconstruct the expected calls and distinguish mandatory operations from calls whose failure can be tolerated.

## Specification

### Classification

A system transaction is a legacy transaction with a non-null destination in `0x1001` through `0x1004`, zero gas price, and a recovered sender equal to the block coinbase.
The reference engine uses its local signer as a fallback while constructing a block whose coinbase is not yet set.
Published-block checks MUST use the authenticated block author, not an unrelated local node identity.
All ordinary transactions MUST precede the system transaction suffix.
Classification does not authorize an arbitrary call: finalization also reconstructs each expected transaction.

### Expected Calls

The conditional order is:

1. Fork initialization calls, in registry order.
2. Offline-proposer penalty call, when targets exist and PoSA is active.
3. Reward distribution, on every PoSA block.
4. Penalty mitigation on a council-period transition, when both parent and child are PoSA blocks and the parent state lists penalized validators.
5. Council update on that transition, when both parent and child are PoSA blocks.

An expected transaction uses the sender's current state nonce, the expected destination, value and calldata, gas price `0`, and gas limit `2^63 - 1`.
Import compares its chain-aware signing hash with the next classified transaction.
Unconsumed transactions at the end of finalization invalidate the block.
Changing a destination, nonce, value, gas limit, calldata, or call order MUST NOT silently substitute another operation.

### Execution and Receipts

Execute the expected call directly through the EVM, without intrinsic gas, the [OIP-30](oip-30.md) calldata floor, or gas purchase.
Value transfer still requires the sender's balance.
From Cancun, prepare the transaction access state using the active rules and precompiles.
On success, increment the sender nonce, add the call's consumed gas (the declared limit minus the remaining gas, with no refund or calldata floor) to cumulative block gas, and append a success receipt containing the call's logs and bloom.
The declared system gas limit is not the actual block gas consumed.
Historical reconstruction and tracing use the same system execution semantics.

### Failure and Omission

Initialization, reward distribution, and council update failures abort block processing or assembly.
Errors from the optional slash and mitigation calls do not abort block processing.
A block can omit an expected optional slash or mitigation call; from BreakpointBravo, [OIP-36](oip-36.md) limits omission to calls that would fail.
Only omission is permitted: a present transaction that differs from the expected optional call is not consumed, so the next expected call or the leftover check rejects the block.

These rules do not apply to unsigned EVM system calls such as the history-storage update.

## Rationale

Reconstructing the expected call prevents a block author from using the privileged classification for arbitrary protocol state changes.
Separating mandatory from optional calls lets penalty bookkeeping fail without stopping block production.

## Backwards Compatibility

These rules retain the existing legacy transaction encoding.
Ordinary zero-price transactions do not gain privileged execution merely by targeting a system address.
The ordinary transaction gas cap in [OIP-38](oip-38.md) does not govern this dedicated execution path.

## Test Cases

| Case | Expected result |
| --- | --- |
| Ordinary transaction after a classified system transaction | Reject. |
| Expected call with changed nonce, value, or calldata | Reject the block, for mandatory and optional calls alike. |
| Successful system call | Increment nonce once and include actual call gas and logs in the receipt. |
| Reverting mandatory call | Fail the block rather than accept a failed mandatory-operation receipt. |
| Missing optional call before BreakpointBravo | Continue with the next expected call. |
| Unknown or duplicated suffix transaction | Reject leftover system transactions. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Classification, finalization, and execution](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Expected slash, reward, mitigation, and council calls](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus.go).
- [Suffix separation during import](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_processor.go).
- [System addresses](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/const.go).
- [Existing system execution tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine_test.go).
- [Existing finalization tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-19/verification.md).

## Implementation and Activation

Fork initializers run at their configured boundaries; ongoing PoSA calls use `IsIstanbulPoSA`.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Run import, assembly, historical tracing, and replay tests against identical blocks.
- Cover optional-call omission, mismatches, reverts, and total block gas.

## Security Considerations

Incorrect classification can bypass fees and normal transaction checks.
Inconsistent nonce handling, gas accounting, or replay semantics can change the state root.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
