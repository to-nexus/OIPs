# OIP-12 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-12](../../OIPs/oip-12.md), not a definition of protocol requirements or proof of network activation.
The fork identifier and encoding vectors were computed on 2026-10-28, and the tests below were run on 2026-10-29.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [eth/protocols/eth][eth-tests] | `TestHandshake68` | Status exchange carrying the local total difficulty, and rejection of a mismatched protocol version, network ID, genesis, or fork identifier. |
| [eth/protocols/eth][eth-tests] | `TestGetBlockBodies68`, `TestHandleNewBlock` | Block body serving and handling of a propagated `NewBlock` message. |
| [core/forkid][forkid-tests] | `TestCreation`, `TestValidation`, `TestEncoding`, `TestTimeBasedForkInGenesis` | EIP-2124 identifier construction, filtering, and encoding with upstream network configurations, including forks at or before the genesis time. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./eth/protocols/eth ./core/forkid -run '^(TestHandshake68|TestGetBlockBodies68|TestHandleNewBlock|TestCreation|TestValidation|TestEncoding|TestTimeBasedForkInGenesis)$' -count=1
```

## Vectors

The fork identifiers for the mainnet and ZoneZero presets, the filter results, and the body encodings in the proposal were computed with the reference client's fork identifier and RLP code in a temporary program.
The program also confirmed that a decoder with only the three upstream body fields rejects a body carrying the sidecar element.
Because the vectors come from the reference code, they are not an independent implementation check.

The statement that upstream go-ethereum v1.16.9 sends a zero total difficulty was checked against the upstream `StatusPacket68` construction, which leaves the field unset.

## Verification Limits

No connection to a live peer, multi-node propagation run, or synchronization across forks was performed.
The informative reference values for peer counts, timers, and discovery were inspected in source but not exercised.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[eth-tests]: https://github.com/to-nexus/go-cross/tree/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/protocols/eth
[forkid-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/forkid/forkid_test.go
