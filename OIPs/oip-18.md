---
oip: 18
title: ONEchain Network Parameters and Genesis
description: Chain identifiers, genesis blocks, genesis allocations, and initial chain configuration of the public ONEchain networks.
author: ONEchain Contributors
status: Final
type: Informational
created: 2026-10-28
---

# OIP-18: ONEchain Network Parameters and Genesis

## Abstract

This document records the identifiers, genesis blocks, genesis allocations, and genesis-era chain configuration of the public ONEchain networks, ONEchain mainnet and the ZoneZero testnet.
It lets node operators, wallets, and independent clients confirm that they join the intended network and reproduce its genesis state.
It records configuration values rather than new rules and links the proposals that define how those values are used.

## Motivation

A node can join a network only when its chain ID, network ID, genesis block, and fork configuration match those of its peers.
Wallets need the chain ID to sign transactions, and independent clients need the exact genesis allocation to reproduce the genesis state root and block hash.
These values are otherwise available only in the reference client's source code.
A versioned document gives them a reviewable record and a single place to check them.

## Specification

### Scope

This document describes the reference client presets at revision 4c0838f.
Values are source settings; they do not by themselves establish when or how a network was deployed.
Fork schedules after the genesis rule set are recorded by the documents for those forks.

Balances are given in ONE, where 1 ONE equals `10^18` wei.

### Networks

| Network | Chain ID | Network ID | Client flag | Genesis hash |
| --- | --- | --- | --- | --- |
| ONEchain mainnet | `612055` | `612055` | `--one`, alias `--cross` | `0x675a5d7c97cc1be3bf061635d31206966ef7ae0205a45890a4bab931456a8348` |
| ZoneZero testnet | `612044` | `612044` | `--zonezero` | `0xcd8ce15999597691045f5f9675debfe4e0a7e5dca94b866e01df6b5b9d4263aa` |

Each network flag selects the genesis block and sets the network ID equal to the chain ID.
A reference node started without a network flag or a custom genesis initializes the mainnet genesis.
For a custom genesis without an explicit `--networkid`, the reference client uses the chain ID as the network ID.

The network and its native coin were previously named CROSS chain and CROSS.
The reference client's documentation records the rename to ONE effective 2026-07-23.
Some identifiers keep the earlier name, including the `--cross` flag alias, the `cross_*` RPC namespace, the CrossEx contract, and the `Cross Istanbul. ` header prefix.

### Genesis Block

Both public genesis blocks have number `0`, a zero parent hash, the empty uncle hash, empty transaction and receipt roots, and a zero bloom.
Their other header fields are:

| Field | ONEchain mainnet | ZoneZero |
| --- | --- | --- |
| `timestamp` | `1739496247` (`0x67ae9b37`, 2025-02-14 01:24:07 UTC) | `1739496247` |
| `gasLimit` | `105,000,000` | `105,000,000` |
| `difficulty` | `1` | `1` |
| `nonce` | `0x000000000000aaaa` | `0x000000000000eeff` |
| `mixDigest` | `0x43726f737320497374616e62756c2e2000000000000000000000000000000000` | Same as mainnet. |
| `coinbase` | `0xb9E345bA27826D71eb89a015852c752e341010EC` | `0x06Dc63E28d18172A689213071884c66c5281b493` |
| `extraData` | `0xc680c0c080c080` | `0xc680c0c080c080` |
| `baseFeePerGas` | `1,000,000,000` wei | `1,000,000,000` wei |
| `withdrawalsHash` | `0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421` | Same as mainnet. |
| `stateRoot` | `0xf1d5c5a9e75052f87ceec26d1c71428956026ef68fc1866f7f697d760cbd39b7` | `0x180b05c4c7b2faad175f0fa8e912c50ece411fdabc0dede07739caf6a5ee525a` |

The `mixDigest` is the Istanbul prefix followed by 16 zero bytes.
The `extraData` is the six-element Istanbul extra-data of [OIP-5](oip-5.md) with every element empty: no vanity, no validators, no vote, round `0`, no committed seals, and no random reveal.
The initial validator set therefore comes from the chain configuration's `istanbul.validators` list.
The `withdrawalsHash` is the root of an empty list, because Shanghai is active at genesis.
The base fee is the initial London base fee.

### Genesis Rule Set

Both public networks use the following chain configuration at genesis:

- Homestead, Tangerine Whistle (EIP-150), Spurious Dragon (EIP-155 and EIP-158), Byzantium, Constantinople, Petersburg, Istanbul, Muir Glacier, Berlin, London, Arrow Glacier, and Gray Glacier at block `0`.
- The DAO fork block at `0` with `daoForkSupport` set to `false`, so no DAO state change applies.
- Shanghai and Adventure at timestamp `0`; Adventure is described by [OIP-17](oip-17.md).
- `terminalTotalDifficulty` of `2^63 - 1`, which the chain does not reach, as described by [OIP-4](oip-4.md).

The Istanbul upgrade in this list is the Ethereum execution upgrade and is unrelated to the name of Istanbul consensus.

The `istanbul` section has these values on both networks:

| Parameter | Value | Where it is used |
| --- | --- | --- |
| `epochlength` | `86400` blocks | Periodic reset of pending validator votes, in [OIP-6](oip-6.md). |
| `blockperiodseconds` | `1` | Minimum timestamp interval, in [OIP-5](oip-5.md). |
| `emptyblockperiodseconds` | `0` | Additional producer interval for empty blocks; `0` adds none. |
| `requesttimeoutseconds` | `5` | Base round timeout, in [OIP-7](oip-7.md). |
| `maxRequestTimeoutSeconds` | `60` | Round timeout cap, in [OIP-7](oip-7.md). |
| `policy` | `0`, round robin | Proposer selection, in [OIP-7](oip-7.md). |
| `beneficiary` | Mainnet `0xEB569FfDa1a757938187320866959438Aa61f4c6`; ZoneZero `0x579c60A3176C5B588aeAD61a1F878a6A19CCc84E` | Fee recipient, in [OIP-11](oip-11.md). |
| `gaslimit` | Not set | Each block keeps its parent's limit, `105,000,000` from genesis, under [OIP-9](oip-9.md). |
| `elasticitymultiplier` | `3` | [OIP-9](oip-9.md). |
| `basefeechangedenominator` | `8` | [OIP-9](oip-9.md). |
| `minbasefee` | `1,000,000,000` wei | [OIP-9](oip-9.md). |
| `maxbasefee` | `10^18` wei | [OIP-9](oip-9.md). |

Neither network defines block-numbered Istanbul `transitions` in the reference presets.

### Initial Validators

The ONEchain mainnet preset lists these 20 initial validators, in ascending byte order:

```text
0x02f5F938B40A60B2345Ac0C9Fd9D909bD1F012eE
0x091E0be1D78511dE3b6D7022C99539671d235D73
0x0A62e6a8553A10B2031fD956df6bc28852F4d91d
0x49bcC861395C42cA60d773FB053F25DDaACbeA50
0x60Eef089B72da83eC98330296b1E1Ff37C118588
0x6C79321D421E9a37041e1477929d478492a04608
0x7De4fa95e742D34f0979875c060f7e1886948f03
0x87EB0d108594FFC6DeB4dcBdB43E3B0899B7a863
0x884DCf7bE65a5287cFb9648283B90C70D0D59c8A
0x88B9B24C441f8775c01443F6Ce244cEF5dA0364A
0x90e456Fe1f07A56e891BA11C8dE045091363527D
0x95fa026C756874f12a499ef0f95531f0b93629F5
0xAB128537bBC770C8f9E9225c854a2170B708E88A
0xBb2182CE952F3501325cd77A7327f8De091b394c
0xbCb02c35e753b25c450727C3cb61F6Aa4D2D545F
0xc193C8F676aF724B1d2cCF1236200044E8c6C4a6
0xD6EE737Ff9EABda5f9E9365AfE7D032e2aEb208C
0xE6927A1181bf5760fC7e25ABC96f7C025fF73802
0xF405a387AA84e58c1A5D2150305AD1b1788646Cf
0xfa884b0C778Fa24D015481a262F3efe924dc0D61
```

The ZoneZero preset lists these 7 initial validators, in ascending byte order:

```text
0x28a0Ef4a0cb8204a810615C9b01475006dA35ECD
0x2bCFC7F77555B585941Ddb04d9B7977f1Ae612CB
0x3AeE6025948c380cD0E4e71cBB041337cc0E2C4E
0x53bDC4196454c15af773BF00D3b4bC1BC913B751
0x88501713D1Bb34d81c4857C8F32905574D67Cd57
0xd3f69551F006075aA71351a387eE23DdeaA5DbF1
0xfb2Ce154CF90F35851D3D3c2C378D9820dEd4eb5
```

These lists record the configured initial sets at revision 4c0838f, not verified launch membership or current on-chain membership.
Neither list is committed by the genesis hash, because the genesis extra-data carries no validators.

### Genesis Allocations

| Address | Account | Mainnet balance | ZoneZero balance | Runtime code hash |
| --- | --- | --- | --- | --- |
| `0xfeed00000000000000000000000000000000C0DE` | CrossEx | `0` | `0` | `0xa39c1e1fd7f8692e6850497a888bcded2229e957dad6c3a112fb77d9f89ccffc` |
| `0xb81d6e000000000000000000000000000000C0de` | Bridge proxy | `980,000,000` ONE | `980,000,000` ONE | `0x0dac1e1deb9381d1139c43a9d49d022a4786242e90744abd0f77bf85375b548b` |
| `0xB81D6e000000000000000000000000000000AAaA` | Bridge implementation | `0` | `0` | `0xc1ff81042b4e5a16a79527e6388fc7b3b99b7f9707036127feb48624c9d46488` |
| `0xcA11bde05977b3631167028862bE2a173976CA11` | Multicall3 | `0` | `0` | `0x2739586f0710b7af4c04843ecf23e4aa32145c0a05e1b0844e560ec56fe5a293` |
| `0xb9E345bA27826D71eb89a015852c752e341010EC` | Mainnet foundation account | `10,000,000` ONE | Not allocated. | None. |
| `0x0575a1B8e9E8950356b0c682bB270e16905eb108` | Mainnet account named `EcoCross` in the reference source | `10,000,000` ONE | Not allocated. | None. |
| `0x06Dc63E28d18172A689213071884c66c5281b493` | ZoneZero foundation account | Not allocated. | `1,000,000,000,000` ONE | None. |

Every allocated account has nonce `0`.
The bridge proxy has one storage entry: the [ERC-1967](https://eips.ethereum.org/EIPS/eip-1967) implementation slot `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc` holds the bridge implementation address, left-padded to 32 bytes.
No other allocated account has storage.

The genesis allocations total `1,000,000,000` ONE on mainnet and `1,000,980,000,000` ONE on ZoneZero.
These totals describe genesis state only, not current supply.

[OIP-3](oip-3.md) uses the CrossEx address for native transfer logs without requiring its code.
The application interfaces of CrossEx, the bridge, and Multicall3 are outside this document.

The reference client's `make-genesis` tooling builds custom networks and can optionally add the bridge, Multicall3, and two deterministic deployment proxies at `0x4e59b44847b379578588920cA78FbF26c0B4956C` and `0x914d7Fec6aaC8cd542e72Bca78B30650d45643d7`.
The deterministic deployment proxies are not part of either public genesis.
A generated genesis is a different chain and does not reproduce the public genesis hashes.

### Source History

In the reference client's history, the public genesis definitions took their current values in revision [10dea30](https://github.com/to-nexus/go-cross/commit/10dea307f9ae559c7e0316bc5e6f05ae9136e08b) on 2025-04-23.
Earlier revisions defined other genesis hashes for these networks.
This source history does not establish deployment dates or prove which genesis a running network uses; operators should confirm the genesis hash reported by their nodes.

## Rationale

Recording each value with its source and a reproducible check lets readers confirm the record without trusting a single implementation.
The document links the proposals that define how parameters are applied, so a rule has one authoritative description.

Pinning both validator lists to the same reference revision keeps the source presets reproducible without equating them with historical or current network membership.

## Backwards Compatibility

This document changes no client behavior or network configuration.
Changing any genesis header field or allocation produces a different genesis hash and therefore a different chain.
The renamed client flags keep their earlier names as aliases.

## Test Cases

Each public genesis block was rebuilt with the reference genesis construction at revision 4c0838f, using `ToBlock()` on `DefaultCrossGenesisBlock` and `DefaultZoneZeroGenesisBlock`.
The resulting block hashes were compared with the genesis hash constants in the reference source:

| Preset | Recomputed genesis hash | Matches the constant |
| --- | --- | --- |
| ONEchain mainnet | `0x675a5d7c97cc1be3bf061635d31206966ef7ae0205a45890a4bab931456a8348` | Yes. |
| ZoneZero | `0xcd8ce15999597691045f5f9675debfe4e0a7e5dca94b866e01df6b5b9d4263aa` | Yes. |

The state roots and header fields in [Genesis Block](#genesis-block) come from the same rebuilt blocks.
Each runtime code hash is `keccak256` of the code bytes in the corresponding preset allocation.
The validator lists in [Initial Validators](#initial-validators) were compared with the configured validator addresses at revision 4c0838f: 20 unique mainnet addresses and 7 unique ZoneZero addresses, each listed in ascending byte order.
No running node or deployed network was queried.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Chain configurations](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Genesis hashes, accounts, and initial validators](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/cross_params.go).
- [Default genesis blocks](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/genesis.go).
- [Genesis allocations](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/predeploy/predeploy.go).
- [Predeployed contract addresses](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/const.go).
- [Network flags and network IDs](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/cmd/utils/flags.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-18/verification.md).

## Implementation and Activation

This document records source defaults and schedules no change.
It does not establish the deployed configuration, launch date, or running client version of any network.

## Security Considerations

Transaction signatures bind to the chain ID, so wallets should use `612055` for mainnet and `612044` for ZoneZero to keep transactions from being valid on the other network.
Operators should pin and check the expected genesis hash, because a node started with a different genesis joins a different chain.

The funded accounts and the bridge balance are controlled by their keys and contract code, which this document does not describe.
Administration and upgrade authority of the predeployed contracts are defined by their code and are outside this document.

Source presets can change between client releases.
Operators should confirm a release's chain configuration and genesis hash before upgrading an existing node.

## References

- [EIP-155: Simple replay attack protection](https://eips.ethereum.org/EIPS/eip-155).
- [ERC-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967).
- [OIP-5](oip-5.md).
- [OIP-4](oip-4.md).
- [OIP-17](oip-17.md).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
