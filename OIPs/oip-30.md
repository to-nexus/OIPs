---
oip: 30
title: Calldata Gas Floor
description: Prague calldata token accounting, minimum charged gas, and fee-delegation settlement.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 2, 9
---

# OIP-30: Calldata Gas Floor

## Abstract

This proposal records the EIP-7623 calldata gas floor and its interaction with ONEchain fee delegation and execution fee accounting.

## Motivation

The ordinary intrinsic gas calculation alone does not determine the minimum gas limit or final charge for data-heavy transactions.
Clients and sponsors must apply the floor consistently during admission, execution, estimation, and refunds.

## Specification

### Floor Calculation

Adopt [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623) by reference under the Prague execution rules.
For calldata with `z` zero bytes and `nz` nonzero bytes, the reference calculation is:

```text
tokens = z + 4 * nz
floorGas = 21000 + 10 * tokens
```

Reject arithmetic overflow.
The declared gas limit MUST cover both the normal intrinsic requirement and this floor.
The floor does not replace access-list, authorization, contract-creation, or initcode metering in the normal intrinsic calculation.

After execution and the ordinary capped refund calculation, charged gas is at least `floorGas`.
The refund cannot reduce the charge below that value.
The receipt gas used, cumulative block gas, sender/payer refund, and execution fee credit MUST use the resulting charge.

### Fee Delegation and Other Paths

For a fee-delegated transaction, apply the same calldata floor to its execution data.
[OIP-2](oip-2.md) determines who purchases gas and receives the remaining-gas refund; the floor does not transfer value-payment responsibility from sender to payer.
[OIP-9](oip-9.md) still determines base fee and block gas limits.

The public pool checks the floor under Prague at the pool's current head.
Historical block execution uses the executing block's rules, not the latest head.
Dedicated consensus system calls bypass ordinary transaction intrinsic/floor accounting as described by [OIP-19](oip-19.md).
A gas estimate or sponsorship quote MUST NOT assume that unused execution gas always reduces payment below the data floor.

## Rationale

Keeping the floor separate from intrinsic gas explains why an otherwise inexpensive execution can have a larger final charge.
The same accounting rule must apply regardless of which account pays.

## Backwards Compatibility

Before Prague, the existing intrinsic and refund rules apply without this additional floor.
Previously sufficient gas limits or fee quotes can be insufficient after the boundary.

## Test Cases

| Case | Expected result |
| --- | --- |
| Empty calldata | floorGas = 21000. |
| 100 nonzero bytes | floorGas = 25000. |
| 100 zero bytes | floorGas = 22000. |
| Declared gas below the floor | Reject even if ordinary intrinsic gas would fit. |
| Execution and refunds would charge less than the floor | Charge the floor. |
| Separate fee payer | Charge and refund the payer according to OIP-2, preserving sender value liability. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Floor calculation, execution, and refunds](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go).
- [Pool floor check](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go).
- [Gas constants](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go).
- [Upstream specification](https://eips.ethereum.org/EIPS/eip-7623).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-30/verification.md).

## Implementation and Activation

The source uses the Prague predicate for floor enforcement.
Its adoption must be evaluated together with the rest of the execution configuration, including fee delegation.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Verify ordinary and fee-delegated receipt, balance, refund, and fee-credit results with floor-dominated transactions.
- Run activation-boundary, overflow, creation, authorization-list, and estimation cases.

## Security Considerations

Applying the floor only in the pool leaves block execution inconsistent.
Refunding the sender when a separate payer purchased gas misdirects funds; estimators and services must also distinguish charged gas from peak execution needs.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
