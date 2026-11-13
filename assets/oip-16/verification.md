# GasAbs Interface Verification

This record supports [OIP-16](../../OIPs/oip-16.md).
Checks were performed on 2026-10-28 using isolated source snapshots.

References to `to-nexus/gasabs` are [internal verification sources](../../README.md#verification-sources) and require access to the cited repositories.

## Source Baselines

| Component | Revision and scope |
| --- | --- |
| Submission node | [go-cross `4c0838f`](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156), the local `main` snapshot. |
| GasAbs service | [gasabs `f5e0af7`](https://github.com/to-nexus/gasabs/commit/f5e0af72bf0ce283015974011783df62f57dd8a0), the local `origin/dev` snapshot and default branch. |
| Service transaction library | go-cross `v1.1.2`, as declared in the service's [go.mod](https://github.com/to-nexus/gasabs/blob/f5e0af72bf0ce283015974011783df62f57dd8a0/go.mod). |

The service checkout was detached at an older revision, so its default-branch snapshot was inspected without changing that checkout.
The local `origin/master` revision `d7318268aa1de25cb71b64037be658bc6fefc15d` differs from the chosen service baseline only by a production SQL migration.
No deployed release or remote branch freshness was established by these local snapshots.

## Existing Tests

The following commands passed against the service baseline:

```sh
go test ./internal/gasabs/filter -count=1
go test ./internal/gasabs/mysql -run '^TestGetAccessList_MethodFiltering$' -count=1
```

The [filter tests](https://github.com/to-nexus/gasabs/blob/f5e0af72bf0ce283015974011783df62f57dd8a0/internal/gasabs/filter/filter_test.go) and [legacy comparison tests](https://github.com/to-nexus/gasabs/blob/f5e0af72bf0ce283015974011783df62f57dd8a0/internal/gasabs/filter/filter_comparison_test.go) cover selector matching, unrestricted destinations, approval-spender checks, and sender-first policy behavior.
The [MySQL package test](https://github.com/to-nexus/gasabs/blob/f5e0af72bf0ce283015974011783df62f57dd8a0/internal/gasabs/mysql/mysql_test.go) checks conversion of in-memory address-filter rows into policy maps; it does not connect to MySQL.

## Additional Policy and RPC Checks

A temporary `TestGasAbs_OIPProfile` passed these eight cases using in-process JSON-RPC, fixed public test keys, a mock simulation node, and an in-memory retry-marker substitute:

| Case | Verified result |
| --- | --- |
| Successful signing and simulation request | Returned type `0x07` with the original hash and a recoverable payer signature; simulation used `latest` and omitted nonce, chain ID, fee caps, access list, and payer fields. |
| Approved sender with a restrictive destination filter | Sender approval skipped that method filter. |
| Destination selector miss | Returned the original transaction without simulation. |
| Excessive tip cap | Sequential requests produced error, unchanged original transaction, then error. |
| Simulation failure | The same sequential retry behavior applied. |
| Neither address approved | Repeated requests continued to return an error. |
| Approved sender and blacklisted destination on direct service call | The service still returned a payer-signed wrapper, confirming the separate node-side enforcement boundary. |
| Both access-list method spellings | Both returned a full changed-version snapshot and an object with `null` list fields for an unchanged version. |

These temporary checks are not permanent regression tests in the service repository.
The source for node-side eligibility, asynchronous policy synchronization, and submission handling was inspected separately; these tests did not run the complete node-to-service-to-pool route.

## Verification Limits

The mock simulation does not prove that an actual transaction executes successfully or that a sponsor has funds.
The marker substitute checks sequential control flow, not real Redis expiry, failures, or concurrent access.
Database polling, keystore loading, startup failure behavior, live policy changes, full signed-transaction admission, and block inclusion were not exercised end to end.
Existing service tests that submit transactions to local endpoints were not run.
The complete test suites, a security audit, deployed configuration, and actual network operation were not verified.
