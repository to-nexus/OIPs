---
oip: 34
title: Breakpoint Hardfork
description: The Breakpoint profile of Cancun and Prague execution, PoSA consensus, and protocol contract installation.
author: ONEchain Contributors
status: Draft
type: Meta
created: 2026-10-29
requires: 4, 10, 17, 19, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 33
---

# OIP-34: Breakpoint Hardfork

## Abstract

This Meta proposal lists the specifications included in the Breakpoint hardfork at the reference revision.
Breakpoint combines the Cancun and Prague execution upgrades with Istanbul PoSA consensus, protocol contract installation, and fee settlement.

## Motivation

A single upgrade name spans EVM features, contract state, validator authority, and fee settlement.
A profile must link those rules without treating every source feature or service as a consensus requirement.

## Specification

### Included Specifications

The earlier Adventure profile is specified in [OIP-17](oip-17.md), and [OIP-4](oip-4.md) defines Istanbul chains without the Merge transition.
Upstream EIPs listed without a separate ONEchain proposal are adopted by reference, subject to the activation conditions below.

Consensus, contracts, and fee settlement:

| Specification | Scope |
| --- | --- |
| [OIP-19](oip-19.md), [OIP-21](oip-21.md) | System transactions, contract installation, and ordered initialization. |
| [OIP-22](oip-22.md), [OIP-23](oip-23.md), [OIP-24](oip-24.md) | PoSA council, BLS commit seals, and BLS random reveal. |
| [OIP-25](oip-25.md), [OIP-26](oip-26.md) | Reward settlement, offline penalties, and mitigation. |
| [OIP-27](oip-27.md) | ONEchain BLS signature verification precompile at `0xc0`. |

Cancun and Prague execution:

| Specification | Scope |
| --- | --- |
| [OIP-10](oip-10.md) | Blob transactions, blob gas, and the `BLOBHASH` and `BLOBBASEFEE` instructions. |
| [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780) | SELFDESTRUCT deletes an account only when it was created in the same transaction. |
| [OIP-29](oip-29.md) | EOA code delegation transactions. |
| [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537) | BLS12-381 operation precompiles at `0x0b` through `0x11`. |
| [OIP-30](oip-30.md) | Calldata gas floor. |
| [OIP-31](oip-31.md) | Historical block hash storage. |
| [OIP-32](oip-32.md) | Prague blob schedule on Istanbul chains. |
| [OIP-33](oip-33.md) | Withdrawals, parent beacon roots, and execution requests without an Ethereum consensus layer. |

EIP-6780 applies to the Cancun-derived instruction tables, including Prague and Breakpoint; the Adventure-only table keeps the earlier SELFDESTRUCT behavior.
A balance moved by SELFDESTRUCT does not emit the transfer log of [OIP-3](oip-3.md).
The EIP-2537 operations use uncompressed field and point encodings and are separate from the compressed `0xc0` interface of OIP-27.
Adventure already adopts the Shanghai execution changes and EIP-1153 and EIP-5656, so naming Cancun does not enable them again.
These tables cover the specified adoption units, not an exhaustive inventory of every inherited EIP in the client.

[OIP-28](oip-28.md) is companion peer policy, not a new block-validity requirement.
Application-level account and token standards remain ORCs.

### Activation Conditions

Let `T` be `breakpointTime`.
Breakpoint is active when London is active, T is configured, and the block timestamp is at least T.
A boundary installation occurs when the parent predicate is false and the child predicate is true.
PoSA additionally requires a non-genesis block, a PoSA section in the Istanbul configuration, and timestamp at least `T + 1`; the predicate does not inspect the section's contents.
Therefore a block at exactly T can install the contracts while retaining the earlier consensus/fee profile.
A first boundary block whose timestamp skips past T can already satisfy PoSA; initialization, snapshot, and epoch behavior for that case must be verified rather than assuming an intervening block exists.
Without PoSA configuration, the reference skips the whole Breakpoint registry entry, including the CrossEx replacement, and continues the pre-PoSA consensus path, even if the Breakpoint execution table is selected.
The boundary block still discards pending validator votes as specified in OIP-22, and block assembly reserves gas for system transactions from Breakpoint onward.

Cancun, Prague, and Breakpoint are separate timestamp predicates; each requires London and its configured time, and an unset time disables it.
The reference Istanbul rule builder permits these execution upgrades without a proof-of-stake transition.
The Breakpoint predicate also selects Prague-level execution independently of `pragueTime`: the Prague-derived instruction table, a transaction signer that accepts types `0x03` and `0x04`, the Prague precompile map with `0xc0`, the Prague blob schedule entry, and history storage in the active system-contract list.
These Breakpoint selections do not set `pragueTime` or `cancunTime`; header fields, pool admission, the calldata floor, and history installation follow their own predicates.
Configurations MUST therefore activate Cancun and Prague no later than Breakpoint, as also required by OIP-29 and OIP-33.

### Reference Source Presets

| Network | Chain ID | Cancun, Prague, and Breakpoint timestamp |
| --- | --- | --- |
| ONEchain mainnet | 612055 | 1780282800 |
| ZoneZero | 612044 | 1778814000 |

These are values in revision 4c0838f, not independently established network activation records.
The original digest prefix and the optional-call omission rule of OIP-19 remain until the separately configured [OIP-37](oip-37.md) profile applies.

## Rationale

Breakpoint is documented as one profile because the reference presets activate Cancun, Prague, and Breakpoint together and the Breakpoint predicate itself selects Prague-level execution.
Upstream EIPs adopted without ONEchain changes are listed by reference, as in OIP-17, rather than restated in separate proposals.
The one-second gap between the Breakpoint and PoSA predicates is stated explicitly because it separates contract installation from the first PoSA block.

## Backwards Compatibility

This document does not change Adventure or the earlier Final OIPs.
Persistent contracts can no longer use SELFDESTRUCT to erase code and storage; historical Adventure execution keeps its earlier behavior, so replay must select the original table.
Clients lacking any required active execution, contract, or consensus component can diverge even when they recognize the Breakpoint name.

## Test Cases

| Case | Expected result |
| --- | --- |
| Timestamp T-1 | Retain the prior active rules. |
| Timestamp T with PoSA configured | Apply boundary installation and execution changes; the PoSA predicate remains false at exactly T. |
| First eligible non-genesis block at T+1 or later | Select PoSA, subject to consistent initialized contract and snapshot state. |
| Breakpoint without PoSA configuration | Skip the whole Breakpoint registry entry and initialization, discard pending votes at the boundary, and retain pre-PoSA consensus. |
| Boundary also crosses council/validator epochs | Match preparation, contract updates, and imported snapshot behavior. |
| Same SELFDESTRUCT bytecode under the Adventure-only and Breakpoint tables | Observe EIP-6780 deletion behavior only under Breakpoint. |
| EIP-2537 vectors at `0x0b` through `0x11` under Breakpoint | Match the upstream output and gas. |
| Independent clients replay the boundary | Agree on headers, state, receipts, and subsequent validator authority. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Predicates, source schedules, and fork ordering](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Instruction tables](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go).
- [SELFDESTRUCT implementations](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/instructions.go).
- [Precompile maps](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go).
- [Contract registry](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go).
- [Consensus and finalization integration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go).
- [Boundary snapshot handling](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/engine.go).
- [Breakpoint transaction signer](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction_signing.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-34/verification.md).

## Implementation and Activation

The table records source presets only.
A deployment record needs the network genesis, authoritative historical configuration, implementing release, and boundary evidence; those facts are not established by this Draft.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Resolve the required Draft specifications and run a combined boundary replay with their exact contracts.
- Run upstream EIP-6780 and EIP-2537 fixtures at the runtime instruction tables and precompile addresses.
- Check timestamp jumps, genesis-active configuration, first PoSA epochs, and historical network schedules.

## Security Considerations

Partial activation can disagree on transaction validity, validator keys, rewards, or privileged calls.
Operator parameters and initialized contracts must agree with the consensus predicates before block production resumes across a boundary.
Applications must not rely on SELFDESTRUCT to revoke permissions or reset storage across transactions.
A successful EIP-2537 curve operation is not proof that a caller has verified a complete signature protocol.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
