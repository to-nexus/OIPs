# OIP-14 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-14](../../OIPs/oip-14.md), not a definition of interface requirements or proof of provider deployment.
Source inspection was performed on 2026-10-28, and the tests below were run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [eth/api_backend.go][eth-backend], [core/blockchain.go][blockchain] | Standard tag resolution, missing-marker errors, pruning cutoff, and safe/finalized updates after canonical Istanbul import. |
| [eth/gasprice/feehistory.go][fee-history] | Next base fee, eligible receipt-gas weighting, fee-cap filtering, empty rows, percentile validation, and the pending fallback. |
| [backend/api.go][istanbul-api], [backend/snapshot.go][snapshot] | Method arguments, unsupported Istanbul aliases, snapshot timing, response casing, configuration units, suppressed membership lookup errors, and author activity intervals. |
| [backend/engine.go][backend-engine], [istanbul/config.go][runtime-config] | Namespace version and runtime timeout units. |

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [eth/gasprice][gasprice-tests] | `TestFeeHistory`, `TestSuggestTipCap` | Fee-history ranges, percentile rows, and pending handling with upstream test chains. |
| [consensus/istanbul/backend][backend-tests] | `TestAPI_Status`, `TestBackend_IsValidatorAt` | `istanbul_status` author counts over a half-open block interval and its maximum range; engine-level validator membership lookups. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./eth/gasprice ./consensus/istanbul/backend -run '^(TestFeeHistory|TestSuggestTipCap|TestAPI_Status|TestBackend_IsValidatorAt)$' -count=1
```

## Verification Limits

The fee-history tests use upstream test chains rather than Istanbul base fee parameters, and the proposal's percentile example was checked by arithmetic.
No node was started and no RPC method, including the mutating voting methods, was called over a transport.
No provider exposure, history retention, or production endpoint behavior was audited.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[eth-backend]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/api_backend.go
[blockchain]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/blockchain.go
[fee-history]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/gasprice/feehistory.go
[istanbul-api]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/api.go
[snapshot]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/snapshot.go
[backend-engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go
[runtime-config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/config.go
[gasprice-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/gasprice
[backend-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend
