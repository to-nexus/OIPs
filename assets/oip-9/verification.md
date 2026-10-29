# OIP-9 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-9](../../OIPs/oip-9.md), not a definition of protocol requirements or proof of network activation.
Source inspection was performed on 2026-10-28, and the tests below were run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [eip1559.go][execution-fees] | Parent-height fee parameters, first-London initialization, asymmetric branch-specific bounds, and exact configured child gas limit. |
| [config_istanbul.go][istanbul-config] | Initial values, ordered transition overrides, fallback elasticity/denominator, and optional fee bounds. |
| [config.go][config] | Reference network presets and London activation. |
| [state_transition.go][state-transition] | Execution fee accounting boundary; presence of a base fee does not imply burning. |
| [vm/eips.go][evm-eips] | `BASEFEE` implementation inherited from EIP-3198. |

## Runtime Checks

A temporary test was added to an isolated source snapshot of the reference revision and passed.
It called `CalcBaseFee` and `VerifyEIP1559Header` with an Istanbul configuration using elasticity `3` and denominator `8`, and parent headers carrying the Istanbul digest prefix.

| Check | Result |
| --- | --- |
| All nine calculation vectors in the proposal's Test Cases | The reference function returned each expected child base fee, including the branch-specific bounds, the unclamped at-target case, the minimum upward step, and the pre-London initial base fee. |
| Gas limit transition to `240` at the child height, with parent limit `120` | A child header with gas limit `240` and base fee `875` was accepted; the same header with gas limit `120` was rejected. |

The temporary test is not a permanent regression test in the reference repository.
The existing `TestCalcBaseFee` and `TestBlockGasLimits` tests also passed, but they use upstream configuration without Istanbul parameters or bounds.

## Verification Limits

Historical configurations and deployed parameter transitions were not queried.
Transitions of fee parameters, absent or zero elasticity and denominator, and missing parent base fees were inspected in source but not exercised.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[execution-fees]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip1559/eip1559.go
[istanbul-config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config_istanbul.go
[config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[state-transition]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[evm-eips]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/eips.go
