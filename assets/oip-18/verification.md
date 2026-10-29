# OIP-18 Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-18](../../OIPs/oip-18.md), not proof of how or when a network was deployed.
The genesis values were computed on 2026-10-28, and the tests below were run on 2026-10-29.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Package | Tests | Checked behavior |
| --- | --- | --- |
| [core][genesis-tests] | `TestGenesisHashes` | The default ONEchain mainnet and ZoneZero genesis blocks hash to the preset genesis hash constants. |
| [core][genesis-tests] | `TestSetupGenesis` | Genesis initialization and stored-genesis compatibility handling. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./core -run '^(TestGenesisHashes|TestSetupGenesis)$' -count=1
```

## Genesis Values

A temporary program rebuilt the mainnet and ZoneZero genesis blocks with the reference genesis construction.
The header fields, state roots, allocation totals, and genesis hashes in the proposal come from those rebuilt blocks.
Each runtime code hash is `keccak256` of the code bytes in the corresponding preset allocation.

## Verification Limits

No running node or deployed network was queried.
The ZoneZero initial validator list, launch dates, and the purpose of individual funded accounts were not verified.
Source presets can change between releases and do not prove which genesis a running network uses.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[genesis-tests]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/genesis_test.go
