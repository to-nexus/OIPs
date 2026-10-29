# OIP-2 Implementation Verification

This record describes checks performed on 2026-10-28 against [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).
It is supporting evidence for [OIP-2](../../OIPs/oip-2.md), not a definition of protocol requirements or proof of network activation.

## Existing Regression Tests

The following tests passed in an isolated source snapshot of the reference revision:

| Test | Checked behavior |
| --- | --- |
| [TestFeeDelegationSigning](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction_signing_test.go#L37) | Sender and payer signing, address recovery, and the shared inner/wrapper transaction hash. |
| [TestFeeDelegationMinedChargesPayer](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/feedelegation_test.go#L97) | Gas charged to the payer, value charged to the sender, and beneficiary fee collection. |

To repeat these tests from a checkout of the reference revision:

```sh
go test ./core/types ./core -run '^TestFeeDelegation(Signing|MinedChargesPayer)$' -count=1
```

The execution test uses the state transition path with a fake block-production engine.
It does not exercise full Istanbul block validation or a live network.

## Vector and Balance Checks

The [deterministic vector](fee-delegation.json) was generated and checked against the same revision.
Checks covered nested RLP encoding, both signing hashes, signature recovery, encoding round trips, the shared transaction hash, and the difference between inner and wrapper transaction trie roots.

Temporary checks also exercised gas purchase with `g = 30,000`, `c = 20`, `t = 2`, `b = 12`, and `v = 100`:

| Initial balances | Observed result |
| --- | --- |
| Separate sender `100`, payer `420,000` | Accepted; payer debited `420,000`. |
| Separate sender `100`, payer `419,999` | Rejected for insufficient payer funds. |
| Shared sender/payer `420,100` | Rejected for insufficient funds at the fee cap. |
| Shared sender/payer `600,100` | Accepted; shared account debited `420,000`. |

These temporary checks targeted `buyGas` and are not permanent regression tests in the reference repository.

## Verification Limits

The conformance cases in OIP-2 specify expected behavior; they are not a claim that every case has an executed regression test.
The recorded checks do not establish complete coverage of malformed wrappers, activation boundaries, or all execution outcomes.
They are not a full security audit, a complete client test run, or verification of deployed releases and historical activation blocks.

The reference [network configuration](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go) sets `AdventureTime` to `0` for ONEchain mainnet (`612055`) and ZoneZero (`612044`).
These source settings were checked; deployed binaries, the first accepted fee-delegated transaction, and the applicable adoption decision were not independently verified.
