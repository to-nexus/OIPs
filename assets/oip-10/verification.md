# OIP-10 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-10](../../OIPs/oip-10.md), not a definition of protocol requirements or proof of network activation.
Source inspection was performed on 2026-10-28, and the tests below were run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [eip4844.go][blob-fees], [config.go][config], [protocol_params.go][parameters] | Initial schedule selection, header fields, excess formula, default limits, and the local availability window. |
| [core/data_availability.go][availability], [types/blob_sidecar.go][sidecar] | Recent versus historical checks, metadata, transaction ordering, versioned hashes, KZG proofs, and sidecar cleanup. |
| [engine/engine.go][engine], [core/blockchain.go][blockchain] | Availability verification before proposal voting and during import. |
| [protocols/preprepare.go][wire-preprepare], [protocols/roundchange.go][wire-roundchange] | Optional sidecar elements outside signed message payloads. |
| [core/block_validator.go][body-validator], [state_transition.go][state-transition] | Blob counts, exclusion of sidecars from body transactions, execution fee liability, and beneficiary crediting. |
| [core/txpool/validation.go][pool] | Unconditional Istanbul pool rejection of blob transactions, independent of active blob execution. |
| [internal/ethapi/api.go][eth-api] | Canonical sidecar lookups, missing/error results, response fields, and first-32-byte truncation when `fullBlob` is false. |
| [vm/jump_table.go][jump-table], [vm/contracts.go][precompiles] | Blob opcodes and point-evaluation precompile in the initial execution schedule. |

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [core][core-tests] | `TestIsDataAvailable`, `TestIsDataAvailableSkipsOldBlocks`, `TestCheckDataAvailableInBatch` | Sidecar validation for recent blocks, the historical-window exception, and batch checks. |
| [consensus/istanbul/core][istanbul-core-tests] | `TestRoundChange_ReproposesPreparedBlockWithSidecars` | Re-proposal of a prepared block together with its sidecars after a round change. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./core ./consensus/istanbul/core -run '^(TestIsDataAvailable|TestIsDataAvailableSkipsOldBlocks|TestCheckDataAvailableInBatch|TestRoundChange_ReproposesPreparedBlockWithSidecars)$' -count=1
```

## Verification Limits

Successful end-to-end blob production, voting, import, or retrieval was not demonstrated.
The excess-gas example and RPC truncation behavior were checked by inspection and arithmetic, not by a runtime test.
The proposal does not remove pool rejection or establish deployed support.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[state-transition]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[blockchain]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/blockchain.go
[jump-table]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go
[blob-fees]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go
[parameters]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go
[availability]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/data_availability.go
[sidecar]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/blob_sidecar.go
[wire-preprepare]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/protocols/preprepare.go
[wire-roundchange]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/protocols/roundchange.go
[body-validator]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/block_validator.go
[pool]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go
[eth-api]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go
[precompiles]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go
[core-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/data_availability_test.go
[istanbul-core-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core
