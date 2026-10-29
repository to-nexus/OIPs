---
oip: 29
title: EOA Code Delegation Transactions
description: EIP-7702 transaction authorization, delegated execution, and ONEchain sponsorship boundaries.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
---

# OIP-29: EOA Code Delegation Transactions

## Abstract

This proposal records the EIP-7702 transaction and EOA code-delegation behavior in ONEchain's Prague-derived execution profile.
It does not extend the fee-delegated transaction format.

## Motivation

Wallets and clients must distinguish a delegation authorization from the transaction that carries it and pays for execution.
Protocol code delegation also needs to remain separate from application account standards.

## Specification

### Adopted Transaction and Authorization Rules

Adopt [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) by reference for transaction type `0x04`, authorization signing, delegation indicators, execution, and gas accounting.
The pool rejects this type before Prague and rejects an empty authorization list.
A set-code transaction has a destination; it is not a contract-creation transaction.

Each authorization contains chain ID, target address, authority nonce, and signature fields.
The reference state transition checks, in order, the chain ID (zero or the current chain), authority nonce overflow, signature recovery, existing authority code (empty or already a delegation indicator), and nonce equality.
It adds the authority to the access list before the code and nonce checks, and refunds 12500 gas for an accepted tuple whose authority account already exists.
Process the tuples in order; an invalid tuple is skipped under the adopted rules rather than treated as a successful authorization.
An accepted tuple increments the authority nonce and installs `0xef0100 || target`; a zero target clears the delegation.
Authorization processing occurs before the destination call, so an execution revert does not imply that accepted authorizations were rolled back.

### ONEchain Boundaries

[OIP-2](oip-2.md) wraps a type `0x02` dynamic-fee transaction as type `0x07`.
It does not wrap a type `0x04` set-code transaction or add an authorization list to that wrapper.
Do not advertise protocol fee-payer authorization for set-code transactions based solely on OIP-2 or [OIP-16](oip-16.md) GasAbs support.

A delegated authority and the outer transaction sender can differ according to EIP-7702.
That arrangement is distinct from ONEchain's payer signature and from ERC-4337 UserOperations.
The pool's limits for delegated senders and pending authorities apply to the transaction sender, not to an OIP-2 fee payer.
Contract-level account modules, validation policies, and wallet negotiation belong in ORCs.

The EVM resolves delegated code for execution when the Prague rules are active; the Prague-derived instruction table changes only the gas of the CALL-family instructions, and EXTCODE* instructions observe the delegation indicator itself.
A configuration MUST activate Prague no later than Breakpoint: the Breakpoint transaction signer accepts type `0x04` without checking Prague, while pool admission and delegated-code resolution require Prague.

## Rationale

Reusing the upstream transaction format preserves interoperability while documenting the limits of the separate ONEchain sponsorship mechanism.

## Backwards Compatibility

Existing transaction types retain their encodings.
Delegated EOAs require wallets, gas estimators, and code-inspection tools to distinguish an indicator from the code it points to.

## Test Cases

| Case | Expected result |
| --- | --- |
| Set-code transaction before Prague | Reject from the public pool. |
| Empty authorization list or contract-creation destination | Reject the transaction structure. |
| Wrong authorization chain ID or nonce | Do not apply that tuple. |
| Accepted authorization targeting zero | Clear delegation and increment authority nonce. |
| Accepted authorization followed by reverting execution | Preserve authorization effects under the adopted semantics. |
| Attempt to wrap type 0x04 using OIP-2 | Do not treat it as the defined fee-delegated transaction type. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Transaction and authorization encoding](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/tx_setcode.go).
- [Authorization validation and application](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go).
- [Pool admission](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go).
- [Instruction integration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/eips.go).
- [Delegated code resolution](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/evm.go).
- [Transaction signer selection](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction_signing.go).
- [Upstream specification](https://eips.ethereum.org/EIPS/eip-7702).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-29/verification.md).

## Implementation and Activation

Prague gates pool admission and delegated-code resolution, while the Breakpoint signer accepts type `0x04` independently of Prague, as constrained above.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Run authorization, rollback, delegation-resolution, refund, and pool replacement fixtures against the pinned client.
- Verify RPC construction and estimation for supported wallets without assuming OIP-2 sponsorship.

## Security Considerations

Delegation can give target code broad authority over an account.
Chain ID zero, replayable signing contexts, nonce changes, initialization races, and execution reverts must be visible to signers and relayers.
A valid authorization does not establish the safety of the delegated contract.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
