# ORC-43 Implementation Verification

This record describes source inspection performed for [ORC-43](../../ORCs/orc-43.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

References to `to-nexus/one-account-sdk` and `to-nexus/one-paymaster-contracts` are [internal verification sources](../../README.md#verification-sources) and require access to the cited repositories.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [one-paymaster-contracts `src/TokenPaymaster.sol` at 18b7fbd][paymaster-src-tokenpaymaster-sol] | Payment data layout, payment modes, quote limits, charging, refund credits, and owner withdrawal limits. |
| [one-paymaster-contracts `src/TokenPaymasterV08.sol` at 18b7fbd][paymaster-src-tokenpaymasterv08-sol] | The EntryPoint v0.8 variant. |
| [one-paymaster-contracts `src/SignedPaymaster.sol` at 18b7fbd][paymaster-src-signedpaymaster-sol] | Backend signature digest and recovery. |
| [one-paymaster-contracts `test/TokenPaymasterIntegration.t.sol` at 18b7fbd][paymaster-test-tokenpaymasterintegration-t-sol] | Existing EntryPoint integration test scope. |
| [one-account-sdk `src/client/tokenPaymaster.ts` at 21b0565][sdk-src-client-tokenpaymaster-ts] | Permit and approval integration. |

## Calculation Checks

The minimum payload lengths (224 and 214 bytes), the price example, and the charge, cap, and credit example (2,200,000, 1,320,000, and 880,000 token units) were checked by hand.
These are arithmetic checks, not output from running an implementation.

## Verification Limits

The repository's existing EntryPoint integration tests were not run for this record.
ERC-7597 was Draft when consulted.
The backend signs the fixed payment prefix; optional permit bytes are bound by the account operation signature, and markup is read during validation.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[paymaster-src-tokenpaymaster-sol]: https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/TokenPaymaster.sol
[paymaster-src-tokenpaymasterv08-sol]: https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/TokenPaymasterV08.sol
[paymaster-src-signedpaymaster-sol]: https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/src/SignedPaymaster.sol
[paymaster-test-tokenpaymasterintegration-t-sol]: https://github.com/to-nexus/one-paymaster-contracts/blob/18b7fbd60f4dfd7202ed7d5459fb2b20469a3676/test/TokenPaymasterIntegration.t.sol
[sdk-src-client-tokenpaymaster-ts]: https://github.com/to-nexus/one-account-sdk/blob/21b0565b21eb7d7ee2496049b981c4bbfbdb29c0/src/client/tokenPaymaster.ts
