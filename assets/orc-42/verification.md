# ORC-42 Implementation Verification

This record describes source inspection performed for [ORC-42](../../ORCs/orc-42.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [bridge-contracts `src/token/ICrossMintableERC20.sol` at b6be327][bridge-src-token-icrossmintableerc20-sol] | Token interface. |
| [bridge-contracts `src/token/CrossMintableERC20V2.sol` at b6be327][bridge-src-token-crossmintableerc20v2-sol] | ERC-2612 permit inheritance. |
| [one-paymaster-contracts `src/TokenPaymaster.sol` at 18b7fbd][paymaster-src-tokenpaymaster-sol] | Use of the byte-signature ERC-7597 permit. |
| [one-account-sdk `src/client/tokenPaymaster.ts` at 21b0565][sdk-src-client-tokenpaymaster-ts] | Permit request checks, approval headroom, and validator prefix. |

## Verification Limits

ERC-7597 was Draft when consulted.
The bridge token's ERC-2612 permit and the paymaster's ERC-7597 permit are different interfaces; connecting them needs an adapter or an approval fallback.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[bridge-src-token-icrossmintableerc20-sol]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/ICrossMintableERC20.sol
[bridge-src-token-crossmintableerc20v2-sol]: https://github.com/to-nexus/bridge-contracts/blob/b6be3278ae793ce448a29bec1a9bff005438792b/src/token/CrossMintableERC20V2.sol
[paymaster-src-tokenpaymaster-sol]: https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/TokenPaymaster.sol
[sdk-src-client-tokenpaymaster-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts
