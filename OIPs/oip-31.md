---
oip: 31
title: Historical Block Hash Storage
description: Prague parent-hash storage calls, the history contract interface, and installation-boundary behavior.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 21
---

# OIP-31: Historical Block Hash Storage

## Abstract

This proposal documents the EIP-2935 history-storage integration on Istanbul networks.
It distinguishes the pre-transaction parent-hash call from fork-time installation of the contract.

## Motivation

The presence of a history contract address does not prove that every expected historical slot was populated.
Clients must agree on installation and call ordering at the first active block.

## Specification

### Contract and Call Interface

Adopt the history contract interface and ring-buffer behavior of [EIP-2935](https://eips.ethereum.org/EIPS/eip-2935), subject to the installation ordering below.
The reference address is `0x0000F90827F1C53a10cb7A02335B175320002935`, with a history window of `8191` blocks.
The ring stores a parent hash at the slot derived from its block number modulo 8191.
Ordinary queries use the contract's block-number calldata and range checks; the EVM BLOCKHASH opcode is not widened to this window by this Draft.

Before ordinary transactions, the reference processor calls the contract with the 32-byte parent hash from system address `0xfffffffffffffffffffffffffffffffffffffffe`, zero value and gas price, and 30000000 call gas.
This is an unsigned EVM system call, not a signed transaction in the block body or the [OIP-19](oip-19.md) suffix.
The reference call finalizes its state changes; as in upstream go-ethereum, an execution error is treated as a fatal processing error rather than as an invalid block.
Prague selects this path on the scoped Istanbul execution profile.

### Installation Boundary

[OIP-21](oip-21.md) installs the configured history runtime when crossing the Prague boundary.
In the inspected Istanbul path, installation happens in finalization after ordinary transactions, whereas the parent-hash call happens before them.
If the address has no code in the parent state, that first call cannot write the history ring; the code is installed later in the same block.
Subsequent blocks call the installed runtime.
Do not claim that the first Prague block has already stored its parent hash without checking preexisting code or genesis installation.

This ordering is a reference-client observation, not a proposal to move the installation hook.
A correction that changes the first populated slot or the state visible to transactions requires its own compatibility analysis and activation decision.
When Prague is active at genesis, no boundary occurs and OIP-21 installs nothing; the history code MUST then come from the genesis allocation.

### Query Semantics

After installation, the contract's query range and ring overwrite behavior follow the adopted interface.
A value read from a slot MUST be interpreted together with its requested height and the allowed history window.
An unpopulated boundary slot MUST NOT be represented as proof of the requested historical block.

## Rationale

Separating the call from installation exposes a boundary difference that a simple EIP-adopted label would hide.
The specification retains source behavior while leaving full first-block conformance verification explicit.

## Backwards Compatibility

This does not change the existing BLOCKHASH opcode or introduce Beacon history.
Moving installation earlier can change transaction-visible code and state in the fork block, even if later blocks agree.

## Test Cases

| Case | Expected result |
| --- | --- |
| Installed contract at Prague block n | Write parent hash for n-1 before ordinary transactions. |
| First Prague block with no preexisting history code | Check the reference ordering: the early call performs no ring write; finalization installs code. |
| Following block | Write its parent hash using installed code. |
| Query outside the contract window | Apply the contract range rejection. |
| Ring wraps after 8191 positions | Use the correct height and slot rather than treating stale data as current. |
| Genesis has Prague active | Take the history code from the genesis allocation; block 1 writes the genesis hash. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Parent-hash processing](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_processor.go).
- [Mining call path](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go).
- [History installation](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go).
- [Address, window, and runtime](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/protocol_params.go).
- [Upstream specification](https://eips.ethereum.org/EIPS/eip-2935).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-31/verification.md).

## Implementation and Activation

The scoped activation predicate is Prague.
The shared record identifies source ordering only; the first stored height and historical deployment state were not queried from a live network.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Reproduce the first Prague block and the next block from actual parent state, including transaction-visible queries.
- Verify genesis-active installation, runtime identity, ring wraparound, and upstream compatibility differences.

## Security Considerations

Missing boundary writes, stale ring slots, or an unexpected runtime at the reserved address can give applications incorrect historical evidence.
A block hash is not independently a finality proof.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
