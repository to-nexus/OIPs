---
oip: 36
title: Optional System Call Omission Check
description: Rejection of blocks that omit a slash or mitigation system call that would succeed, from BreakpointBravo.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 19, 26
---

# OIP-36: Optional System Call Omission Check

## Abstract

From BreakpointBravo, a block can omit an expected optional slash or mitigation system transaction only if that call would fail.
Clients decide this by executing the expected call on trial state that is then reverted.

## Motivation

[OIP-19](oip-19.md) lets the slash and mitigation calls fail without aborting block processing and lets a block omit them.
Limiting omission to calls that would actually fail keeps that tolerance while making a successful call part of the expected block contents.

## Specification

### Activation

This rule applies to a block when London is active, `breakpointBravoTime` is configured, and the block timestamp is at least that value.
It does not apply to earlier blocks.

### Omission Rule

The rule covers the optional calls of OIP-19: the offline-proposer penalty call and the penalty mitigation call specified in [OIP-26](oip-26.md).
When the next system transaction in the block does not match an expected optional call, the client MUST execute the expected call against the current state as a trial and then revert every change made by the trial.
If the trial succeeds, the block is invalid.
If the trial fails, the call is treated as omitted, and processing continues with the next expected call.
The trial MUST NOT change accepted state, logs, receipts, nonces, cumulative gas, or transaction order.
A present transaction that differs from the expected call is never consumed as that call; the matching and leftover checks of OIP-19 still apply.
Mandatory system calls are unchanged.

## Rationale

A trial against the same state gives every client the same answer without adding data to the block.
Keeping failed calls omissible preserves the existing failure tolerance of the optional calls.

## Backwards Compatibility

Blocks before activation keep the omission rule of OIP-19.
From activation, a block that omits an optional call that would succeed becomes invalid.

## Test Cases

| Case | Expected result |
| --- | --- |
| Missing optional call that succeeds in the trial | Reject the block. |
| Missing optional call that reverts in the trial | Permit omission. |
| Trial changes storage, logs, or nonce before completing | Leave none of those changes in the accepted result. |
| Optional call with changed calldata, trial succeeds | Reject the block. |
| Same missing call one block before activation | Permit omission under OIP-19. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Optional system call and trial execution](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Existing omission cases](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/consensus_test.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-36/verification.md).

## Implementation and Activation

The check follows `IsBreakpointBravo`, independently of the ordinary transaction checks.
The mainnet and ZoneZero presets leave `breakpointBravoTime` unset, and this Draft proposes no activation time.
Activation is coordinated through the BreakpointBravo profile in [OIP-37](oip-37.md).

Before advancing beyond Draft:

- Run omission, mismatch, revert, and trial-rollback cases on both sides of the activation boundary.
- Verify that import, block assembly, and replay reach the same decision for identical blocks.

## Security Considerations

The trial must run against the same state as block execution; a client whose trial diverges splits from the network.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
