# OIP-6 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-6](../../OIPs/oip-6.md), not a definition of protocol requirements or proof of network activation.
Source inspection was performed on 2026-10-28, and the listed tests were run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [engine/engine.go][engine] | Header author, timestamp and digest checks, proposal versus final-header verification, direct-digest ECDSA committed seals, duplicate/member checks, and random reveal integration. |
| [backend/engine.go][backend-engine], [backend/snapshot.go][snapshot] | Genesis validator precedence, parent snapshot use, vote replacement, strict majority, removal cleanup, and vote reset at configured epochs. |
| [validator/default.go][validators] | Byte-ordered selection integration, round-robin/sticky selection, `ceil(2N/3)` quorum, and `ceil(N/3)-1` fault bound. |
| [core/preprepare.go][preprepare], [core/roundchange.go][roundchange] | Current-view proposal acceptance, distinct-source justification validation, matching target rounds, preservation of older prepared certificates, and invalid prepared-value handling. |
| [core/prepare.go][prepare], [core/commit.go][commit] | Prepared and committed transitions; the message signature and final committed-seal verification are distinct checks. |
| [types/istanbul.go][istanbul-types], [types/block.go][block-types] | Six-element extra-data, filtered header hash, and round-bound committed-seal hash. |

The proposal relies on [OIP-5](../../OIPs/oip-5.md) for the header format and [OIP-7](../../OIPs/oip-7.md) for the message exchange.
The reference COMMIT-message path does not independently validate the embedded committed seal at the same point as message authorization; final header verification checks the certificate.
The proposal therefore does not claim that message acceptance alone proves a valid final certificate.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [consensus/istanbul/backend][backend-tests] | `TestVoting`, `TestSnapshot`, `TestSaveAndLoad`, `TestSnapshotLoadValidatorsByteSorted` | Vote tallies and membership changes across blocks, epoch resets, snapshot persistence, and byte-ordered validator sets. |
| [consensus/istanbul/backend][backend-tests] | `TestVerifyHeader`, `TestVerifyHeaders`, `TestGetProposer` | Header rejection for invalid extra-data, digest, uncles, difficulty, and timestamp; batch verification; proposer lookup. |
| [consensus/istanbul/validator][validator-tests] | `TestValidatorSet`, `TestProposerPolicy`, `TestProposerPolicyRegistration` | Validator set operations, quorum size, and round-robin and sticky proposer selection. |
| [consensus/istanbul/core][core-tests] | `TestJustifyTrue`, `TestJustifyFalse`, `TestPreprepare_RejectsStaleRoundChangeJustification` | Round-change justification acceptance and target-round matching. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./consensus/istanbul/backend ./consensus/istanbul/validator ./consensus/istanbul/core -run '^(TestVoting|TestSnapshot|TestSaveAndLoad|TestSnapshotLoadValidatorsByteSorted|TestVerifyHeader|TestVerifyHeaders|TestGetProposer|TestValidatorSet|TestProposerPolicy|TestProposerPolicyRegistration|TestJustifyTrue|TestJustifyFalse|TestPreprepare_RejectsStaleRoundChangeJustification)$' -count=1
```

## Verification Limits

The tests exercise single-process engine and snapshot logic; no multi-node consensus run, historical replay, or independent-client comparison was performed.
The proposal's test table describes expected behavior; it is not a claim that every listed case has an executed regression test.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[backend-engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go
[snapshot]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/snapshot.go
[validators]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/validator/default.go
[preprepare]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/preprepare.go
[roundchange]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/roundchange.go
[prepare]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/prepare.go
[commit]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core/commit.go
[istanbul-types]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[block-types]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/block.go
[backend-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend
[validator-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/validator
[core-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core
