# OIP-7 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-7](../../OIPs/oip-7.md), not a definition of protocol requirements or proof of network activation.
The message vectors were computed on 2026-10-28, and the tests below were run on 2026-10-29.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [consensus/istanbul/core][core-tests] | `TestJustifyTrue`, `TestJustifyFalse`, `TestJustifyTreatsBadPrepared`, `TestValidateMessageJustification`, `TestPreprepare_RejectsStaleRoundChangeJustification`, `TestRoundChange_RejectsDuplicatedPrepareJustification` | Round-change and prepare justification rules, distinct sources, target rounds, and bad prepared blocks. |
| [consensus/istanbul/core][core-tests] | `TestCore_CheckMessage`, `TestCore_AddToBacklog`, `TestCore_VerifySignatures`, `TestCore_HandleDecodedMessage`, `TestCore_HandleEncodedMsg` | View ordering, future-message buffering, signature checks, and message dispatch. |
| [consensus/istanbul/core][core-tests] | `TestCore_HandleRoundChange`, `TestRoundChangeSet_GetMinRoundChange`, `TestRoundChangeSetBadPrepared`, `TestPreprepareRejectsMismatchedProposalNumber`, `TestRoundChangeRejectsMismatchedPreparedBlockNumber`, `TestRoundChange_ReproposesPreparedBlockWithSidecars` | Round-change handling, selection of the smallest higher round, prepared certificates, block-number checks, and re-proposal. |
| [consensus/istanbul/protocols][protocols-tests] | `TestRoundChange_EncodeRLP` | ROUND-CHANGE encoding. |
| [consensus/istanbul/backend][backend-tests] | `TestSign`, `TestCheckSignature`, `TestCheckValidatorSignature`, `TestIstanbulMessage`, `TestBackend_HandleMsg` | Message signing and signer recovery, and subprotocol message handling. |
| [consensus/istanbul/validator][validator-tests] | `TestValidatorSet`, `TestProposerPolicy` | Quorum size and proposer selection. |
| [consensus/istanbul][istanbul-tests] | `TestViewCompare`, `TestGetConfig` | View ordering and configuration lookup including transitions. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./consensus/istanbul/... -count=1
```

## Message Vectors

The PREPARE and ROUND-CHANGE vectors in the proposal were computed with the reference client's message encoding and signing code in a temporary program.
Decoding each payload with the reference client and recovering the signer over the signing payload returned the test key's address.
Because the vectors come from the reference code, they are not an independent implementation check.

## Verification Limits

No multi-node consensus run, network partition, or timeout behavior was exercised.
The informative local limits were inspected in source and are not interoperability requirements.
No historical replay, independent-client comparison, network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[core-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/core
[protocols-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/protocols
[backend-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend
[validator-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/validator
[istanbul-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul
