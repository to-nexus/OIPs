# OIP-11 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-11](../../OIPs/oip-11.md), not a definition of protocol requirements or proof of network activation.
Source inspection was performed on 2026-10-28, and the test below was run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [core/state_transition.go][state-transition] | Crediting the full effective gas price on Istanbul chains, the configured recipient with `coinbase` fallback, the blob fee credit, and the simulation exception. |
| [params/config_istanbul.go][istanbul-config] | Beneficiary lookup from the base configuration and block-keyed transitions. |
| [consensus/istanbul/engine/engine.go][engine] | Block author and finalization without a block reward. |
| [internal/ethapi/api.go][eth-api] | The `eth_beneficiary` query. |

## Existing Regression Test

The following test passed in an isolated source snapshot of the reference revision:

| Package | Test | Checked behavior |
| --- | --- | --- |
| [core][core-tests] | `TestFeeDelegationMinedChargesPayer` | On an Istanbul configuration with a beneficiary, mined fee-delegated transactions reduce the fee payer's balance by exactly the beneficiary's gain, so no base fee is burned, and the sender pays no gas. |

To repeat this test from a checkout of the reference revision:

```sh
go test ./core -run '^TestFeeDelegationMinedChargesPayer$' -count=1
```

## Calculation Checks

The amounts in the proposal's test table were recomputed by hand, including the effective gas price `3,000,000,000`, the refunded gas `50,000`, the fee payer's debit and refund, and the blob credit of `131,072` wei.
These are arithmetic checks, not output from running the reference client for each case.

## Verification Limits

Beneficiary transitions, the `coinbase` fallback, blob fee crediting, the absence of block rewards, and the `COINBASE` instruction were inspected in source but not exercised by a test.
No historical replay, deployed beneficiary history, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[state-transition]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[istanbul-config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config_istanbul.go
[engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[eth-api]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go
[core-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/feedelegation_test.go
