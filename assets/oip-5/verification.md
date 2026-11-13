# OIP-5 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-5](../../OIPs/oip-5.md), not a definition of protocol requirements or proof of network activation.
The encoding vectors were computed on 2026-10-28, and the tests below were run on 2026-10-29.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [core/types][types-tests] | `TestHeaderHash`, `TestIstanbulFilteredHeaderWithRound` | A fixed Istanbul header hash, and block and commit seal hashes that exclude committed seals and set the round. |
| [core/types][types-tests] | `TestIstanbulExtraDecodeRLP`, `TestExtractToIstanbulExtra`, `TestIsIstanbulDigest`, `TestMakeIstanbulDigest` | Extra-data decoding and extraction, and digest prefix recognition and construction. |
| [consensus/istanbul/backend][backend-tests] | `TestVerifyHeader`, `TestVerifyHeaders` | Rejection of malformed extra-data, a wrong digest prefix, uncles, a difficulty other than `1`, and an early timestamp; batch verification. |
| [consensus/istanbul/engine][engine-tests] | `TestWriteCommittedSeals`, `TestWriteRoundNumber`, `TestWriteValidatorVote`, `TestPrepareExtra` | Writing committed seals, the round, and a vote into extra-data. |

Some of these tests also cover header variants outside this proposal's scope; only their cases for the format specified here are relied on.

To repeat these tests from a checkout of the reference revision:

```sh
go test ./core/types ./consensus/istanbul/backend ./consensus/istanbul/engine -run '^(TestHeaderHash|TestIstanbulFilteredHeaderWithRound|TestIstanbulExtraDecodeRLP|TestExtractToIstanbulExtra|TestIsIstanbulDigest|TestMakeIstanbulDigest|TestVerifyHeader|TestVerifyHeaders|TestWriteCommittedSeals|TestWriteRoundNumber|TestWriteValidatorVote|TestPrepareExtra)$' -count=1
```

## Encoding Vectors

The header vector in the proposal was computed with the reference client's extra-data encoder and header hash functions in a temporary program.
The program produced the unsealed and sealed extra-data, `blockHash`, `sealHash(H, 2)`, and the plain `keccak256(RLP(H))` shown in the proposal.
Because the vector comes from the reference code, it is not an independent implementation check.

## Extra-Data Extension Compatibility

Source inspection on 2026-11-13 rechecked the decoder, encoder, and hash filtering at the same reference revision.
The six base fields are followed by optional `signersBitset` and `signers` fields, so the decoder accepts typed six-, seven-, and eight-element lists.
The encoder emits six elements when both optional fields are absent and eight when either is present, including a present but empty list.
Before PoSA activation, the trailing fields do not participate in consensus validation and are excluded from the original-prefix filtered hashes.
From PoSA activation, [OIP-23](../../OIPs/oip-23.md) defines the BLS validation rules; [OIP-35](../../OIPs/oip-35.md) defines digest version 2, which retains signer keys in the filtered hashes.
This is a source-inspection clarification of fork-specific behavior, not a new test run or a change to historical acceptance rules.

## Verification Limits

Committed seal recovery and quorum counting were inspected in source; the tests above do not isolate each seal validity case.
The proposal's validity table is not a claim that every listed case has an executed regression test.
No multi-node run, historical replay, or independent-client comparison was performed.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[types-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul_test.go
[backend-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine_test.go
[engine-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine_test.go
