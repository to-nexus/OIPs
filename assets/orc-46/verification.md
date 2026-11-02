# ORC-46 Implementation Verification

This record describes source inspection performed for [ORC-46](../../ORCs/orc-46.md).
It is supporting evidence, not a definition of requirements.
The sources were inspected on 2026-10-29; later source revisions and the ONEchain mainnet were checked on 2026-11-02.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [bridge-contracts `src/token/CrossMintableERC20V2.sol` at b6be327][bridge-src-token-crossmintableerc20v2-sol] | Metadata, minter authority, legacy mint and burn methods, and absence of upgradeability. |
| [bridge-contracts `src/BaseBridge.sol` at b6be327][bridge-src-basebridge-sol] | How the bridge mints to and burns from its own address. |
| [bridge-contracts `src/token/CrossMintableERC20V2Code.sol` at 9a2434f][bridge-src-token-crossmintableerc20v2code-sol-9a2434f] | Later token creation as `BeaconProxy` instances sharing one beacon that the factory's administrator can upgrade. |

Revision 3401906 introduced the beacon-upgradeable token and factory, and revision 9a2434f keeps that design.
In 9a2434f, the bridge still mints to and burns from its own address.

## ONEchain Mainnet Observations

The bridge proxy `0xb81d6e000000000000000000000000000000C0de` registers two token representations whose origin is on another chain.
The following values were read from ONEchain mainnet (`612055`) at block 48,121,257 and from the origin chains.

| Item | USDTx | GHUBx |
| --- | --- | --- |
| Local token | `0x1c37d4F44ed3eC86d96868001CfA89e97112a85C` | `0xB506d82CA638548a597Ac8143217534C524b81dA` |
| Origin token | BSC (`56`) USDT, `0x55d398326f99059fF775485246999027B3197955` | Kaia (`8217`) GHUB, `0x4836cC1f355bB2A61c210EAA0CD3f729160CD95E` |
| Origin and local decimals | `18` and `18` | `18` and `18` |
| Route paused in the bridge registry | No | Yes |
| Registry `minted` and local `totalSupply()` | Both `81,399,439,874,507,055,556,357` | Both `10,000,000 * 10^18` |
| Bridge holds `MINTER_ROLE` | Yes | Yes |
| Default admin and its transfer delay | `0x535c7b8C25eADACCAf857652cA34cF4c010957E2`, `0` | `0x22C1522276855B028c31a731BA10D125811Af37c`, `0` |
| Legacy `mint` and `burn` selectors | Present | Present |
| ERC-7802 `crosschainMint` and `crosschainBurn` selectors | Absent | Absent |
| `supportsInterface(0x33331994)` | `false` | `false` |

Their runtime code matches CrossMintableERC20V2 from the inspected revision, apart from immutable values and the metadata hash.
The [ORC-20 verification record](../orc-20/verification.md) describes that comparison and the token's ERC-20 conformance runs.
Both routes use equal decimals, so the existing deployments perform no decimal conversion.
Both default administrators are externally owned accounts.

The bridge's configured token factory, `0x474d2Fdc2dA12f29925C9eA71dea1CfACBF2fA0D`, returns the bridge proxy from `bridge()` and reverts on `defaultAdmin()` and `beacon()`.
It therefore exposes the interface of the inspected V1 factory, `CrossMintableERC20Code`, rather than either V2 factory, and the registry's `createToken` path uses it.

## Calculation Checks

The 18-to-6 decimal conversion example was checked by hand.
These are arithmetic checks, not output from running an implementation.

## Verification Limits

No ERC-7802 adapter or end-to-end bridge route was established.
ERC-7802 was Draft when consulted.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
The mainnet observations are read-only calls; no bridge message, mint, burn, or release was executed, and no deployment audit was run.
Other `MINTER_ROLE` holders were not enumerated, because the token does not expose role membership lists.

[bridge-src-token-crossmintableerc20v2-sol]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/CrossMintableERC20V2.sol
[bridge-src-basebridge-sol]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/BaseBridge.sol
[bridge-src-token-crossmintableerc20v2code-sol-9a2434f]: https://github.com/to-nexus/bridge-contracts/blob/9a2434f4301ee8e2d9e82364907a4f2938bea063/src/token/CrossMintableERC20V2Code.sol
