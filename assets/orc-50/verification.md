# ORC-50 Specification Verification

This record supports [ORC-50](../../ORCs/orc-50.md).
It records specification inspection on 2026-10-29 and does not establish implementation or deployment conformance.

## Upstream Specification Inspection

The following files were retrieved from `ethereum/ERCs` at revision `4878022015ce5cbaed9ad6c4c8afe4cca95b1983`.

| Source | Status at the inspected revision | Use |
| --- | --- | --- |
| [ERC-5192][erc5192] | Final | Required locking query, events, discovery, and transfer restrictions. |
| [ERC-5484][erc5484] | Final | Optional signed issuance, fixed metadata, burn authorization, and issuance event. |
| [ERC-4973][erc4973] | Review | Alternative considered; its exclusion of the ERC-721 interface prevents treating it as the same profile. |

The Draft adds permanent locking, mandatory mint-time `Locked` emission, non-reuse of burned IDs, and consumer rules to the ERC-5192 baseline.
Its optional consent binding and fixed issuer identity requirements are proposed ONEchain additions, not claims about an existing contract.
ORC-48 supplies metadata conventions; the optional ERC-5484 profile further prohibits metadata changes.

## Interface Identifier Checks

The following commands were run locally:

```text
cast sig 'locked(uint256)'    -> 0xb45a3c0e
cast sig 'burnAuth(uint256)'  -> 0x0489b56f
```

Each extension declares one function, so its selector matches its ERC-165 interface identifier.
Events do not contribute to interface identifiers.
These checks establish selector arithmetic only.

## Verification Limits

No ONEchain SBT implementation, consent encoding, burn entry point, credential status service, or deployment was selected or tested.
No Solidity runtime test, wallet interoperability test, or deployment audit was run.
The proposal's test table remains required work before conformance can be claimed.

[erc5192]: https://github.com/ethereum/ERCs/blob/4878022015ce5cbaed9ad6c4c8afe4cca95b1983/ERCS/erc-5192.md
[erc5484]: https://github.com/ethereum/ERCs/blob/4878022015ce5cbaed9ad6c4c8afe4cca95b1983/ERCS/erc-5484.md
[erc4973]: https://github.com/ethereum/ERCs/blob/4878022015ce5cbaed9ad6c4c8afe4cca95b1983/ERCS/erc-4973.md
