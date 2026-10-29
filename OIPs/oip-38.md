---
oip: 38
title: Transaction Gas Limit Cap
description: The Osaka gas-limit ceiling for ordinary transactions and its system-call and simulation boundaries.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 19
---

# OIP-38: Transaction Gas Limit Cap

## Abstract

This proposal records the EIP-7825 ordinary transaction gas limit cap and identifies paths that use separate execution semantics.

## Motivation

A block gas limit does not by itself bound the work declared by one transaction.
ONEchain also has privileged system transactions whose deliberately large call allowance must not be confused with ordinary transaction admission.

## Specification

### Ordinary Transaction Rule

Adopt [EIP-7825](https://eips.ethereum.org/EIPS/eip-7825) under Osaka.
The maximum declared gas limit of an ordinary transaction is `2^24 = 16777216`.
Reject a greater limit even when the block gas limit is larger or actual execution would use less gas.
The cap supplements, rather than replaces, intrinsic gas, calldata-floor, available block-gas, and balance checks.

The reference pool checks the cap using its active rules.
Under Osaka the reference also removes over-cap transactions from the pool, applies the cap during block assembly, and limits gas estimation to the cap.
The ordinary state-transition precheck enforces it when `SkipTransactionChecks` is false.
Block processing MUST therefore apply the rule independently of public pool admission.
A fee-delegated wrapper remains an ordinary transaction for this cap; sponsorship does not increase the limit.

### Separate Execution Paths

[OIP-19](oip-19.md) system transactions use a dedicated EVM call path with gas allowance `2^63 - 1`; they do not pass through the ordinary transaction precheck.
Their actual gas consumption still contributes to block gas, and their identity and expected contents MUST pass consensus validation.
This exception does not apply to arbitrary zero-price user transactions.

Simulation paths such as `eth_call` set `SkipTransactionChecks` and MUST NOT be treated as evidence that a transaction with the same declared gas is admissible.
Unsigned EVM system calls, including history storage, are also separate from ordinary transaction admission.

## Rationale

Keeping the ordinary transaction cap and privileged execution paths explicit prevents a blanket rule from invalidating the existing system suffix or accidentally exempting user transactions.

## Backwards Compatibility

Pre-Osaka historical transactions retain their prior rules.
After activation, callers declaring more than the cap must reduce the declared limit or split execution where possible.

## Test Cases

| Case | Expected result |
| --- | --- |
| Ordinary declared gas 16777216 | Pass the cap check, subject to all other rules. |
| Ordinary declared gas 16777217 | Reject from pool and ordinary block execution. |
| High declared gas but low actual consumption | Reject based on declared gas after Osaka. |
| Fee-delegated transaction above the cap | Reject as an ordinary transaction. |
| Authenticated expected system transaction | Use OIP-19 execution and actual block gas accounting. |
| Simulation with transaction checks skipped | Do not infer submission validity from simulation success. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Gas cap constant](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go).
- [Ordinary precheck](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go).
- [Pool check](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go).
- [Pool removal](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/legacypool/legacypool.go).
- [Block assembly cap](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go).
- [Gas estimation limit](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/gasestimator/gasestimator.go).
- [System execution](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Upstream specification](https://eips.ethereum.org/EIPS/eip-7825).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-38/verification.md).

## Implementation and Activation

Osaka selects the cap in the ordinary pool and execution paths.
The mainnet and ZoneZero presets leave Osaka unset; this Draft proposes no network activation and does not describe other source presets.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Verify block import and assembly at cap-1, cap, and cap+1 for every supported ordinary transaction type.
- Test system classification and simulation separately so neither provides an unintended admission bypass.

## Security Considerations

Applying the cap only at the public pool leaves an import gap.
Broadening the system exception beyond verified consensus calls can bypass the intended resource bound.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
