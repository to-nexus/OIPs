# Adventure Hardfork Source Verification

This record describes source inspection performed on 2026-10-28 against [go-cross revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).
It supports [OIP-17](../../OIPs/oip-17.md); it is not a complete protocol specification or proof of network activation.
The inspected revision is the local `main` reference, rather than the separate development checkout's `HEAD`.

## Source Observations

| Area | Inspected source | Observation |
| --- | --- | --- |
| Activation and configuration | [params/config.go][config] | `IsAdventure` requires London and its timestamp; fork ordering places Shanghai before Adventure. Mainnet and ZoneZero default London, Shanghai, and Adventure to zero. `IsPostMerge` returns false when Adventure is active; `Rules` allows Shanghai execution under Istanbul consensus. |
| Block-production scheduling | [Merge-aware engine wrapper][beacon], [engine construction][engine-config] | Istanbul is wrapped by the Beacon engine. Its `Prepare` method uses `IsPostMerge`: Shanghai without Adventure selects zero difficulty, while Adventure routes preparation to Istanbul. Together with fork ordering, this requires simultaneous Shanghai/Adventure activation for continuous reference-client Istanbul production. |
| Instruction availability | [jump_table.go][instructions] | Adventure inherits Shanghai and adds EIP-1153 and EIP-5656. `SELFDESTRUCT` retains its legacy behavior. |
| Shanghai state preparation | [statedb.go][state], [state_transition.go][transition], [pool validation][pool] | Coinbase warming, transaction initcode metering, and initcode-size checks retain Shanghai predicates. |
| Transaction types | [transaction_signing.go][signer], [pool validation][pool] | The Adventure signer admits legacy, access-list, dynamic-fee, and fee-delegated dynamic-fee transactions. Pool validation rejects the delegated type before Adventure. |
| Transfer logs and random value | [core/evm.go][context] | Adventure selects `CrossTransfer`. Istanbul block contexts derive the random value from Keccak-256 of `MixDigest`. |
| Fee calculation and collection | [eip1559.go][fees], [state_transition.go][transition] | Istanbul uses configured gas limits, elasticity, base fee change parameters, and bounds. In the Adventure profile, the entire execution fee goes to the configured beneficiary or execution coinbase; the base fee is not subtracted. |
| Header and body boundaries | [Istanbul engine][engine], [block_validator.go][validator], [genesis.go][genesis] | Ordinary Adventure Istanbul headers reject withdrawal commitments. A body without a withdrawal commitment cannot carry a withdrawal list. Shanghai genesis construction uses an empty commitment and list. |
| Consensus and randomness | [Istanbul engine][engine] | The Adventure random-reveal path verifies validator ECDSA signatures and uses the Istanbul digest construction. |
| Precompiles | [contracts.go][precompiles] | The Adventure profile selects the Berlin precompile map, addresses `0x01` through `0x09`. |
| Contract deployment | [predeploy.go][predeploy], [upgrade.go][upgrades] | The default genesis allocation includes CrossEx, bridge contracts, and Multicall3. The fork-upgrade registry has no Adventure replacement hook. |

## Validation Performed

The documentation's metadata, section order, relative links and anchors, source-reference paths, and whitespace were checked.
The proposal index was updated to reference the proposal.
Existing unrelated working-tree content was preserved.

The earlier [OIP-2 verification record](../oip-2/verification.md) and [OIP-3 verification record](../oip-3/verification.md) retain their own test evidence and limits.
Their tests were not rerun for this Meta document, and they do not establish conformance of the entire Adventure profile.

## Verification Limits

No runtime tests, upstream execution conformance suite, full Istanbul boundary replay, or cross-client comparison were run for this documentation change.
The proposal's test matrix records acceptance criteria that still need execution and evidence.
No RPC query, deployed binary inspection, minimum-release audit, or historical activation audit was performed.
The normative OIP dependencies are 2, 3, 4, 5, 6, 7, 8, 9, and 11; companion interfaces and informative network presets are not required dependencies.
OIP-4 remains in Review because revision 4c0838f can route zero-difficulty headers to proof-of-stake verification and finalization.
The correction has not yet been merged or deployed, so OIP-17 also remains in Review.

[config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/config.go
[instructions]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/jump_table.go
[state]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state/statedb.go
[transition]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go
[pool]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/txpool/validation.go
[signer]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction_signing.go
[context]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/evm.go
[fees]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/misc/eip1559/eip1559.go
[engine]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/istanbul/engine/engine.go
[validator]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/block_validator.go
[genesis]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/genesis.go
[precompiles]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/vm/contracts.go
[predeploy]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/params/predeploy/predeploy.go
[upgrades]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/contracts/upgrade.go
[beacon]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/consensus/beacon/consensus.go
[engine-config]: https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/eth/ethconfig/config.go
