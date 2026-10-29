# ORC-47 Implementation Verification

This record describes source inspection performed for [ORC-47](../../ORCs/orc-47.md).
It is supporting evidence, not a definition of requirements or proof of deployment.
The sources were inspected on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [cross-contracts `src/DelegationPool.sol` at 3905c3a][cross-src-delegationpool-sol] | Native deposit, router authority, and withdrawal and unbonding, as background for a nonconforming pool. |

## Calculation Checks

The rounding fixture was checked against the ERC-4626 rounding rules by hand.
These are arithmetic checks, not output from running an implementation.

## Verification Limits

No wrapped asset, share contract, or ERC-4626 or ERC-7540 adapter was selected.
ERC-4626 and ERC-7540 were Final when consulted.
Adopted ERC text was consulted on 2026-10-29; the adopted revisions still need to be pinned before Review.
No Solidity or TypeScript test, EntryPoint `handleOps` run, bundler validation trace, or deployment audit was run for this record.

[cross-src-delegationpool-sol]: https://github.com/to-nexus/cross-contracts/blob/3905c3a02fd4825739f2cc61dc8c9a11a3670fc2/src/DelegationPool.sol
