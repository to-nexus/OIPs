---
oip: 9
title: Base Fee and Block Gas Limit Rules
description: Istanbul base fee calculation, configurable bounds, and block gas limit transitions.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-9: Base Fee and Block Gas Limit Rules

## Abstract

This proposal specifies the base fee and block gas limit rules used by ONEchain Istanbul chains.
It adopts the dynamic-fee pricing model of [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) and the `BASEFEE` instruction of [EIP-3198](https://eips.ethereum.org/EIPS/eip-3198), with configurable elasticity, adjustment denominator, fee bounds, and deterministic gas limit transitions.
It defines calculation rules; fee crediting is specified by [OIP-11](oip-11.md).

## Motivation

Clients must compute identical base fees and block gas limits to agree on block validity.
Ethereum's default parameters and producer-adjustable gas limit do not describe ONEchain's Istanbul configuration.
The height used to select each parameter and the exact branches applying fee bounds are consensus-relevant.

## Specification

### Scope and Parameters

The rules apply to Istanbul chains with London execution enabled.
They do not introduce an activation schedule or define validator economics.
Let `H` be a child header at height `n`, and `P` its parent at height `n - 1`.
All arithmetic below uses nonnegative integers and floor division.

| Symbol | Meaning |
| --- | --- |
| `B` | Parent base fee, in wei per gas. |
| `G` | Parent block gas limit. |
| `U` | Parent gas used. |
| `E` | Elasticity multiplier selected at the parent height. |
| `D` | Base fee change denominator selected at the parent height. |
| `L`, `M` | Optional minimum and maximum base fees selected at the parent height. |
| `Q` | Parent gas target, `floor(G / E)`. |

Configuration begins with the `istanbul` values, then applies transitions in order through the queried block height, inclusive.
For each parameter, the last configured override wins; an omitted override preserves the preceding value.
Transitions must be ordered by block number.
If the resolved elasticity or denominator is zero or absent, the reference defaults are `E = 2` and `D = 8`.
An absent bound means that bound is not applied; a configured zero is a value, not an instruction to remove the bound.
Network configurations must keep `Q > 0`, use nonnegative bounds, and avoid contradictory minimum and maximum values.

### Base Fee Calculation

If London is not active at the parent height, the first London block uses `1,000,000,000` wei per gas.
This initialization branch does not apply the configured bounds.
Otherwise the parent must supply a base fee, and the child base fee is computed as follows:

```text
if U == Q:
    next = B
elif U > Q:
    delta = max(1, floor(floor(B * (U - Q) / Q) / D))
    next = B + delta
    if M is configured:
        next = min(next, M)
else:
    delta = floor(floor(B * (Q - U) / Q) / D)
    next = max(0, B - delta)
    if L is configured:
        next = max(next, L)
```

The maximum is applied only in the above-target branch, and the minimum only in the below-target branch.
The at-target branch preserves `B` without clamping it.
Consequently, changing a bound does not immediately clamp every subsequent block to the new interval.
An independently implemented client must preserve these branch-specific rules.

`H.baseFeePerGas` must be present and equal to the computed result.
The `BASEFEE` instruction returns the executing block's base fee using EIP-3198 semantics.
Estimation and fee history must use the same calculation rather than Ethereum's hard-coded elasticity assumptions.

### Block Gas Limit

The expected gas limit is the configured `gaslimit` resolved at the **child** height `n`.
If no value is configured, the expected limit is `P.gasLimit`.
The child must use that value exactly; the Ethereum rule permitting a producer to adjust the parent limit within a small range is not used on Istanbul chains.
There is no automatic elasticity multiplication of the block limit at the London boundary in this Istanbul path.

The header must also satisfy `gasLimit <= 2^63 - 1` and `gasUsed <= gasLimit`.
The base fee calculation for `H` still uses the parent's limit and parent-height fee parameters.
For a transition at height `n`, a new gas limit therefore takes effect in `H`, while a fee-parameter override first affects the calculation for height `n + 1`.

### Transaction and Accounting Boundaries

The effective execution gas price of a dynamic-fee transaction remains `min(maxFeePerGas, baseFeePerGas + maxPriorityFeePerGas)`.
[OIP-2](oip-2.md) changes the paying account for its transaction type without changing that price or the block's fee calculation.
Refunds and fee recipients are separate accounting rules.
The presence of `BASEFEE` or a dynamic-fee transaction must not be interpreted as evidence that ONEchain burns the base fee.

## Rationale

Configured limits give operators an agreed capacity schedule rather than a producer-selected limit.
Configurable fee parameters allow ONEchain to retain the existing transaction pricing interface with network-specific behavior.
Explicit parent-versus-child height selection and branch-specific bounds are necessary to reproduce the reference implementation.

## Backwards Compatibility

The proposal documents existing behavior and schedules no parameter change.
Using Ethereum's default elasticity, clamping both bounds in every branch, or applying a child-height fee parameter early can produce a different header and fork the chain.
Existing deployed configurations must be recovered and replayed before their historical parameters are changed.

## Test Cases

For the following calculation vectors, let `B = 1,000`, `G = 120`, `E = 3`, and `D = 8`, so `Q = 40`.
Bounds are absent unless specified.

| Parent gas used | Bounds or condition | Expected child base fee |
| --- | --- | --- |
| `0` | None | `875` |
| `40` | None | `1,000` |
| `80` | None | `1,125` |
| `120` | None | `1,250` |
| `80` | Maximum `1,100` | `1,100` |
| `0` | Minimum `900` | `900` |
| `40` | Maximum `900` | `1,000`; no clamping at target. |
| `41` | Replace `B` with `1` | `2`; upward movement is at least one. |
| Any | Parent is before London | `1,000,000,000`, independently of bounds. |

Additional cases must cover absent/zero elasticity and denominator, non-divisible gas targets, parameter transitions, missing base fees, and invalid child gas limits.
For a gas-limit transition from `120` to `240` at height `n`, block `n` must use `240`, while its base fee still uses parent limit `120`.
These vectors and requirements are not a claim that a full runtime conformance suite was executed.

## Reference Implementation

Reference implementation: [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Header verification and fee calculation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip1559/eip1559.go).
- [Parameter lookup and transitions](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config_istanbul.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-9/verification.md).

## Implementation and Activation

The reference mainnet and ZoneZero presets use elasticity `3`, denominator `8`, minimum base fee `10^9`, and maximum base fee `10^18`.
These are source defaults, not an audit of deployed historical configuration.
[OIP-17](oip-17.md) references these rules as an inherited execution baseline.
Any new parameter schedule requires coordinated chain configuration and boundary replay; this proposal activates none.

## Security Considerations

Invalid parameters can make fee calculation undefined or make blocks impossible to execute.
Operators must check parameter validity and transition ordering before deployment.
Integer rounding, parameter height, and bound application must agree across clients.
Fee prediction is not a guarantee of transaction inclusion or a definition of fee ownership.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
