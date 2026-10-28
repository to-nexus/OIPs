# OIP-3 Implementation Verification

This record describes checks performed on 2026-10-28 against [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).
It is supporting evidence for [OIP-3](../../OIPs/oip-3.md), not a definition of protocol requirements or proof of network activation.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Test | Checked behavior |
| --- | --- |
| [TestCrossTransferSig](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/cross_transfer_log_test.go#L56) | Fixed CrossEx address and event topic. |
| [TestAddTransferLog_transferTx](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/cross_transfer_log_test.go#L65) | Transfer receipts with Adventure enabled or disabled, including operation without CrossEx code. |
| [TestAddTransferLog_callContract](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/cross_transfer_log_test.go#L212) | Nested transfers and ordering relative to application logs. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./core -run '^(TestCrossTransferSig|TestAddTransferLog_transferTx|TestAddTransferLog_callContract)$' -count=1
```

The chain tests use a fake block-production engine and exercise local block generation and import.
Their receipt comparison checks status, log addresses, and topics; it does not compare the 96-byte log data against an independent expected value.

## Additional Execution Checks

A temporary `TestOIP3_TransferProfile` test passed 24 leaf cases using the reference client's block-context selection, EVM, and in-memory state database.
It checked the following behavior:

| Cases | Checks |
| --- | --- |
| Five activation cases | Unset Adventure time; timestamps before, at, and after activation; the London prerequisite; no extra execution gas consumption for an empty-code call. |
| Eleven call cases | The proposal's encoding values, zero-value calls, self-transfers, insufficient balance, reverting and invalid-opcode callees, successful and failing precompiles, and `CALLCODE`, `DELEGATECALL`, and `STATICCALL` entry. |
| Three creation cases | Endowment logs from `CREATE` and `CREATE2`, and rollback of a reverting constructor. |
| Three nested-call cases | Per-transfer balance snapshots, ordering before an application log, caught child reverts, parent reverts, and contiguous surviving log indexes. |
| Two self-destruct cases | Beneficiary balance updates without a protocol transfer log, under legacy and Cancun rules. |

The event signature's Keccak-256 digest was also checked against the specified topic.
The execution checks compare log data against independently specified amounts and balances, including `(100, 900, 150)` for the encoding vector and `(100, 1000, 1000)` for a self-transfer.
These temporary checks are not permanent regression tests in the reference repository.

## Verification Limits

The additional cases invoke the EVM directly and do not validate a complete signed transaction, full Istanbul consensus, or a live network.
The proposal's execution table describes expected behavior; it is not a claim that every listed case has an executed regression test.
System-transaction integration, fee-accounting exclusions, and creation-collision behavior were inspected in source but were not independently exercised by the temporary tests.
Cross-client receipt-root agreement at the activation boundary, the complete client test suite, deployed binaries, and historical activation blocks were not checked.

The reference [network configuration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go) sets `AdventureTime` to `0` for ONEchain mainnet (`612055`) and ZoneZero (`612044`).
These source settings do not establish the deployed activation history or an adoption decision.
