# ORC-20 Implementation Verification

This record describes checks performed on 2026-11-02 against [cross-token revision f4d1a0c](https://github.com/to-nexus/cross-token/tree/f4d1a0c9578838f5ccbdad20294c2e44ddd59cbe), [bridge-contracts revision b6be327](https://github.com/to-nexus/bridge-contracts/tree/b6be3278ae793ce448a29bec1a9bff005438792b), and their deployments.
It is supporting evidence for [ORC-20](../../ORCs/orc-20.md), not a definition of requirements.

## Deployed Contracts

| Item | CrossToken | USDTx | GHUBx |
| --- | --- | --- | --- |
| Network | BNB Smart Chain mainnet (`56`) | ONEchain mainnet (`612055`) | ONEchain mainnet (`612055`) |
| Address | `0x6bf62ca91e397B5A7d1D6bCe97D9092065d7A510` | `0x1c37d4F44ed3eC86d96868001CfA89e97112a85C` | `0xB506d82CA638548a597Ac8143217534C524b81dA` |
| `name()` / `symbol()` | `Cross` / `CROSS` | `Cross Bridge USDT` / `USDTx` | `Cross Bridge GHUB` / `GHUBx` |
| `decimals()` | `18` | `18` | `18` |
| `totalSupply()` | `1,000,000,000 * 10^18` | `81,399,439,874,507,055,556,357` | `10,000,000 * 10^18` |
| `eip712Domain()` | Name `Cross`, version `1`, chain ID `56`, token address | Name `Cross Bridge USDT`, version `1`, chain ID `612055`, token address | Name `Cross Bridge GHUB`, version `1`, chain ID `612055`, token address |
| Source | CrossToken, OpenZeppelin Contracts 5.1.0 | CrossMintableERC20V2, OpenZeppelin Contracts 5.2.0 | CrossMintableERC20V2, OpenZeppelin Contracts 5.2.0 |

`eth_chainId` returned the listed chain IDs, and the values were read on 2026-11-02; ONEchain values are at block 48,121,257.
USDTx and GHUBx are registered in the ONEchain bridge as representations of BSC USDT and Kaia GHUB, and the bridge holds their minter role.

### Runtime Code Comparison

CrossToken was built with Hardhat 2.22.17 and Solidity `0.8.22+commit.4fc1097e`, with the optimizer at 200 runs and the `paris` EVM target, as selected by the revision's configuration.
After the seven immutable-value ranges reported by the compiler were masked, its deployed code (4,338 bytes, Keccak-256 `0x94153b8b4d47e9794e833801f13d52ad780ed0d18ae41a7f741b5149fa671825`) matched the build byte for byte, including the metadata hash.

The bridge tokens were compared with Foundry builds of CrossMintableERC20V2 using Solidity `0.8.28` and a range of pipeline, optimizer, and EVM settings.
After immutable values were masked, USDTx (7,081 bytes) matched the legacy pipeline with 162 optimizer runs, and GHUBx (6,464 bytes) matched the IR pipeline with 162 runs.
Both matched for the `cancun` and `prague` targets, which produce identical code, and differed only in the trailing metadata hash.
The revision's own configuration uses 1 run; 162 runs appears in the repository's `251127/deploy-bridge-v2` branch.
The CrossMintableERC20V2 source is unchanged from its addition in revision 935628b through the reference revision, so the deployed tokens use the same contract source.
Revision 3401906 and later, checked through 9a2434f, replace it with a beacon-upgradeable implementation that keeps decimals in proxy storage; neither deployed token uses that design.

## Existing Tests

The following existing tests passed in isolated snapshots of the reference revisions:

| Test | Checked behavior |
| --- | --- |
| cross-token [`test/test.ts`](https://github.com/to-nexus/cross-token/blob/f4d1a0c9578838f5ccbdad20294c2e44ddd59cbe/test/test.ts) `deploy non-upgradable contract` | Owner, name `Cross`, symbol `CROSS`, 18 decimals, and the initial supply. |
| cross-token `test/test.ts` `burn test` | Owner burning, a transfer, rejection of a non-owner `burn`, and the reduced supply. |
| bridge-contracts [`test/CrossMintableERC20V2.t.sol`](https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/test/CrossMintableERC20V2.t.sol) `test_mint_burn` | Factory creation and minter-role minting and burning. |

To repeat them, run `npx hardhat test` in cross-token and `forge test --match-contract '^CrossMintableERC20V2Test$'` in bridge-contracts, each from a checkout of the reference revision with its pinned dependencies.

## Conformance Tests

[`ORC20Conformance.t.sol`](ORC20Conformance.t.sol) implements the token-side cases of the ORC-20 test table.
[`ORC20CrossToken.t.sol`](ORC20CrossToken.t.sol) and [`ORC20CrossMintableERC20V2.t.sol`](ORC20CrossMintableERC20V2.t.sol) apply them to each implementation and its deployments.
They ran with Foundry 1.7.1 and forge-std 1.9.6:

| Suite | Target | Result |
| --- | --- | --- |
| `ORC20CrossTokenTest` | CrossToken built from its reference revision. | 7 passed. |
| `ORC20CrossTokenBscForkTest` | The deployed CrossToken on a BSC mainnet fork at block 131,182,588 (2026-11-02T05:10:31Z). | 7 passed. |
| `ORC20CrossMintableERC20V2Test` | CrossMintableERC20V2 built from its reference revision, including 6- and 0-decimal instances. | 9 passed. |
| `ORC20USDTxForkTest` | The deployed USDTx on a ONEchain mainnet fork at block 48,121,257 (2026-11-02T05:10:28Z). | 7 passed. |
| `ORC20GHUBxForkTest` | The deployed GHUBx on the same ONEchain fork. | 7 passed. |

To repeat them, place `ORC20Conformance.t.sol` and the implementation's file in `test/` of a Foundry project containing that implementation's source at its repository path and its reference dependencies.
For CrossToken, the source is `src/CrossToken.sol`, compiled as described above; for the bridge token, a bridge-contracts checkout of the reference revision and its configuration can be used directly.
Later bridge-contracts revisions replace the token's constructor with an initializer, so the bridge token test does not compile against them.
Set `ORC20_BSC_URL` or `ORC20_ONECHAIN_URL`, with the optional `ORC20_BSC_BLOCK` or `ORC20_ONECHAIN_BLOCK`, to include the fork suites.

| ORC-20 case | Coverage |
| --- | --- |
| Read metadata without privileged credentials | Executed; return data decodes as `string`, `string`, and `uint8`. |
| Decimals `6` and decimals `0` | Executed for CrossMintableERC20V2; raw balances are unchanged. CrossToken has fixed 18 decimals. |
| Decimals changed by an upgrade | Not applicable; neither implementation is upgradeable, and decimals are constant or immutable. |
| Transfer, zero-value transfer, approval replacement, and finite-allowance `transferFrom` | Executed; each checks the 32-byte `true` result, balances or allowance, and the expected events. |
| Insufficient balance or authorization | Executed; the call reverts and balances, supply, and allowance are unchanged. |
| A token call returns no boolean | Covered by the return-data length check in the executed cases. |
| Missing or `bytes32` metadata, shared symbols, and mixed native and token logs | Consumer classification rules; not executed. |

Temporary variants that returned `false` from `transfer` or `approve`, returned an empty name, or omitted the zero-value `Transfer` event failed the corresponding cases.
These variants confirm that the cases can detect such defects; they are not part of the test files.

## Verification Limits

The fork suites set balances by writing storage with forge-std `deal`, so they exercise the deployed code on synthetic balances rather than existing holder state.
The public RPC endpoints used for the forks keep only recent state; repeating a run at the recorded blocks requires archive endpoints.
The bridge token builds reproduced the executable code but not the metadata hash, so the exact build environment of those deployments is unconfirmed.
Owner-only `burn` and minter-role `mint` and `burn` were checked only by the existing tests, and CrossToken's `burnFrom` was inspected in source but not exercised.
The dependencies were matched by version and by the code comparison, not authenticated against release hashes.
Other ONEchain token contracts and wallet, exchange, and indexer behavior were not checked.
