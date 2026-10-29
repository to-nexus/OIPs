---
oip: 32
title: Blob Upgrade Compatibility for Istanbul
description: Prague blob schedule selection on Istanbul chains and the retained full-sidecar availability profile.
author: ONEchain Contributors
status: Draft
type: Standards Track
category: Core
created: 2026-10-29
requires: 10
---

# OIP-32: Blob Upgrade Compatibility for Istanbul

## Abstract

This proposal extends [OIP-10](oip-10.md) with the Prague blob schedule and its selection by Breakpoint on Istanbul chains.
It records compatibility behavior without enabling public blob submission or PeerDAS.

## Motivation

Importing later Ethereum code does not imply adopting every associated blob feature.
Clients must distinguish parameter changes, fee formulas, transaction admission, and data availability.

## Specification

### Schedule Selection

Use the chain-configured blob schedule entry selected for the executing timestamp.
The reference selects the latest configured entry whose predicate holds; entries after Prague belong to later execution profiles such as [OIP-39](oip-39.md).
On Istanbul chains, an active Breakpoint or BreakpointBravo predicate selects the Prague entry even when `pragueTime` is unset.
The baseline defaults relevant to this profile are:

| Entry | Target blobs | Maximum blobs | Base-fee update fraction |
| --- | --- | --- | --- |
| Cancun | 3 | 6 | 3338477 |
| Prague | 6 | 9 | 5007716 |

The Prague defaults implement the parameter increase described by [EIP-7691](https://eips.ethereum.org/EIPS/eip-7691).
This replaces the statement in OIP-10 that these parameters come from the configured Cancun schedule.
On the mainnet and ZoneZero presets, Cancun activates together with Prague and Breakpoint, so the Cancun entry is never selected.
The target used at a boundary is the schedule selected for the child timestamp.

### Fee Formula and Availability

Retain the original excess formula:

```text
excess = max(0, parentExcess + parentBlobGasUsed - targetBlobs * 131072)
```

Retain full-blob/commitment/proof sidecars and the verification/transport rules of OIP-10.
On Istanbul chains, the reference transaction RPC paths and the block producer's pending filter select sidecar version `0`.
No custody, cell-sampling, or data-column protocol is adopted here.
The Istanbul public pool continues rejecting blob transactions even when execution and block-sidecar paths exist.
Later parameter entries do not remove that restriction.

## Rationale

A parameter increase and a new availability protocol are independent changes.
Explicit exclusions keep inherited Ethereum helpers from being mistaken for enabled ONEchain services.

## Backwards Compatibility

Existing OIP-10 encodings and admission restrictions remain in effect.
Different target/max values affect valid block blob counts and the next excess value, so historical configuration must be preserved.

## Test Cases

| Case | Expected result |
| --- | --- |
| Cancun defaults; seven blobs | Exceed the six-blob maximum. |
| Prague defaults; seven blobs | Pass the blob-count bound, subject to all other rules. |
| Breakpoint active and `pragueTime` unset | Select the Prague entry. |
| Parent excess zero, six blobs; child target six | Compute child excess zero. |
| Public Istanbul blob submission | Retain pool rejection. |
| Istanbul transaction submission | Select sidecar version 0. |

These cases define verification work; they are not a report of passing runtime tests.

## Reference Implementation

Reference client: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Schedule defaults](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go).
- [Schedule selection and excess formula](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844.go).
- [Public admission restriction](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go).
- [Sidecar RPC selection](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/internal/ethapi/api.go).
- [Sidecar selection in the block producer](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/miner/worker.go).
- [Existing blob fee tests](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip4844/eip4844_test.go), which use the Ethereum mainnet configuration and do not cover the Istanbul exclusions.

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-32/verification.md).

## Implementation and Activation

Actual schedule entries and fork timestamps come from chain configuration.
Code presence does not demonstrate successful blob production, consensus availability, public submission support, or a network upgrade.

This Draft schedules no new activation.
Source settings and implementation presence do not establish historical deployment or the binaries running on a network.

Before advancing beyond Draft:

- Run schedule-boundary arithmetic, sidecar availability, and full import/assembly tests under each intended configuration.
- Confirm that RPC, storage, and any future pool changes retain an explicit availability and version contract.

## Security Considerations

A correct KZG commitment does not by itself demonstrate data availability.
Mismatched target selection changes header validity and can split clients.

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
