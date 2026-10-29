# ORC-44 Implementation Verification

This record describes source inspection performed for [ORC-44](../../ORCs/orc-44.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [one-account-wallet-sample `packages/wallet/src/provider.ts` at 654de5e][wallet-packages-wallet-src-provider-ts] | Capability handling, batch identifiers, call submission, and status and receipt reporting. |
| [one-account-wallet-sample `packages/wallet/src/config.ts` at 654de5e][wallet-packages-wallet-src-config-ts] | Paymaster provider context fields. |
| [one-account-sdk `src/client/paymasterClient.ts` at 21b0565][sdk-src-client-paymasterclient-ts] | Paymaster RPC requests. |
| [one-account-sdk `src/client/bundlerClient.ts` at 21b0565][sdk-src-client-bundlerclient-ts] | Preparation and submission of prepared operations. |
| [one-account-sdk `src/client/tokenPaymaster.ts` at 21b0565][sdk-src-client-tokenpaymaster-ts] | Token authorization handling. |

## Verification Limits

ERC-7677 was in Review when consulted.
The sample wallet advertises atomic calls but does not implement an application-selected paymaster-service capability.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[wallet-packages-wallet-src-provider-ts]: https://github.com/to-nexus/one-account-wallet-sample/blob/654de5e2a4125218555bfb810dcd383a22dec27d/packages/wallet/src/provider.ts
[wallet-packages-wallet-src-config-ts]: https://github.com/to-nexus/one-account-wallet-sample/blob/654de5e2a4125218555bfb810dcd383a22dec27d/packages/wallet/src/config.ts
[sdk-src-client-paymasterclient-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/paymasterClient.ts
[sdk-src-client-bundlerclient-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/bundlerClient.ts
[sdk-src-client-tokenpaymaster-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts
