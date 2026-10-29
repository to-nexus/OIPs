# OIP-4 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-4](../../OIPs/oip-4.md), not a definition of protocol requirements or proof of network activation.
Source inspection was performed on 2026-10-28, and the tests below were run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [params/config.go][config] | `IsPostMerge` returning false while Adventure is active, upgrade rules conditioned on Istanbul consensus, and the preset `terminalTotalDifficulty` of `2^63 - 1`. |
| [consensus/beacon/consensus.go][beacon], [eth/ethconfig/config.go][ethconfig] | The merge-aware wrapper around the Istanbul engine, its post-merge preparation and difficulty selection, and the configuration check that requires a terminal total difficulty. |
| [consensus/istanbul/engine/engine.go][engine], [consensus/istanbul/constants.go][constants] | Istanbul header validation requiring difficulty `1`, including genesis. |
| [core/evm.go][evm-context], [core/vm/evm.go][evm] | Block-context random value and instruction selection for difficulty-`1` headers. |
| [miner/worker.go][worker], [eth/downloader/downloader.go][downloader] | Code paths that stop sealing or reject synchronized headers once the terminal total difficulty is reached. |

The decimal value `9223372036854775807` of `2^63 - 1` was checked with `cast to-dec 0x7fffffffffffffff`.

## Tests and Runtime Checks

The following existing test passed in an isolated source snapshot of the reference revision:

| Package | Test | Checked behavior |
| --- | --- | --- |
| [consensus/istanbul/backend][backend-tests] | `TestVerifyHeader` | Istanbul header validation rejects a header with difficulty `2`, together with other malformed header fields. |

A temporary test called `NewEVMBlockContext` for a difficulty-`1` header with the proposal's `mixDigest` vector.
The block context's random value was `0x8a0657ff121883007437d73266604532ec282b3434f6719c66eb914f8ed66fff`, matching the proposal.
The temporary test is not a permanent regression test in the reference repository.

## Verification Limits

Block production across a Shanghai activation, with and without Adventure, was inspected in source but not executed.
Rejection of zero-difficulty headers on every import path is not covered by the checks recorded here.
No multi-node run, historical replay, or independent-client comparison was performed.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[beacon]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/beacon/consensus.go
[ethconfig]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/ethconfig/config.go
[engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[constants]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/constants.go
[evm-context]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go
[evm]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/evm.go
[worker]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go
[downloader]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/downloader/downloader.go
[backend-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine_test.go
