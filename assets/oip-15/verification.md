# OIP-15 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-15](../../OIPs/oip-15.md), not a definition of interface requirements or proof of provider deployment.
The proof vectors were computed on 2026-10-28, and the test below was run on 2026-10-29.

## Existing Regression Test

The following test passed in an isolated source snapshot of the reference revision:

| Package | Test | Checked behavior |
| --- | --- | --- |
| [internal/ethapi][crossapi-tests] | `TestCrossAPI_GetCheckpointProof` | Expected proofs for valid ranges, and the `invalid block number`, `invalid range`, `range too large`, and missing-header errors, including a range ending at the largest signed 64-bit value. |

To repeat this test from a checkout of the reference revision:

```sh
go test ./internal/ethapi -run '^TestCrossAPI_GetCheckpointProof$' -count=1
```

## Vectors

The proof vectors in the proposal were computed with the reference client's tree and proof functions in a temporary test.
That test also checked the proposal's verification algorithm against every leaf index for ranges of 2 to 70 blocks.
The roots for `c = 2` and `c = 3` were recomputed independently with `cast keccak` and matched the proposal.

## Verification Limits

The method was not called over a JSON-RPC transport, and JSON-RPC error codes were not checked.
Downstream checkpoint producers and verifiers were not tested against the proposal.
No provider exposure or production endpoint behavior was audited.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[crossapi-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/crossapi_test.go
