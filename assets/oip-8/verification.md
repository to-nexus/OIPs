# OIP-8 Implementation Verification

This record describes checks performed against [go-cross revision 4c0838f][baseline].
It is supporting evidence for [OIP-8](../../OIPs/oip-8.md), not a definition of protocol requirements or proof of network activation.
Source inspection was performed on 2026-10-28, and the runtime checks below were run on 2026-10-29.

## Source Inspection

| Source | Inspected behavior |
| --- | --- |
| [engine/engine.go][engine] | Minimal height/chain-ID concatenation, ECDSA reveal recovery, proposer membership, digest construction, and genesis exception. |
| [backend/backend.go][backend] | `Sign` hashes input with Keccak-256; committed-seal signing uses the separate direct-digest path. |
| [types/istanbul.go][istanbul-types] | 16-byte digest prefix and extra-data reveal field. |
| [core/evm.go][evm-context], [vm/instructions.go][instructions], [vm/jump_table.go][jump-table] | Keccak-256 of `MixDigest` in the Istanbul execution context, opcode `0x44`, and inherited Adventure instruction behavior. |

The proposal distinguishes canonical signature generation from unverified low-`s` rejection in every recovery path.

## Runtime Checks

Two temporary tests were added to an isolated source snapshot of the reference revision and passed.
They called the reference functions directly and are not permanent regression tests in the reference repository.

| Check | Result |
| --- | --- |
| `makeRandomRevealData` for `(1, 1)`, `(256, 1)`, `(1, 258)`, and `(257, 2)` | `0x0101`, `0x010001`, `0x010102`, and `0x010102`, matching the proposal's message cases. |
| Reveal signed over `K(BE(100) \|\| BE(612055))` with a fixed test key | Signature recovery returns the signing key's address. |
| `MakeIstanbulDigest(makeMixHash(reveal), false)` | Equals the 16-byte prefix followed by `K(reveal)[0:16]`. |
| `NewEVMBlockContext` for a difficulty-`1` header with `mixDigest = 0x43726f737320497374616e62756c2e200123456789abcdef0123456789abcdef` | The random value is `0x8a0657ff121883007437d73266604532ec282b3434f6719c66eb914f8ed66fff`, which is `K(mixDigest)`. |

## Verification Limits

The checks exercise the reveal and digest functions and the block context directly; they do not execute `PREVRANDAO` in a full block, verify a reveal through header import, or test malformed signatures.
No multi-node run, historical replay, or independent-client comparison was performed.
No network activation, deployed binary, or minimum release was verified.

[baseline]: https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156
[engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[backend]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/backend/backend.go
[istanbul-types]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/istanbul.go
[evm-context]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go
[instructions]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/instructions.go
[jump-table]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go
