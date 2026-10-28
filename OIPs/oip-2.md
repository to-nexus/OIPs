---
oip: 2
title: Fee-Delegated Dynamic Fee Transactions
description: A typed transaction that allows a separately authorized account to pay for a sender's execution gas.
author: ONEchain Contributors
status: Final
type: Standards Track
category: Core
created: 2026-10-28
---

# OIP-2: Fee-Delegated Dynamic Fee Transactions

## Abstract

This proposal specifies ONEchain transaction type `0x07`, which wraps a signed dynamic fee transaction with a fee payer address and a second signature.
The sender authorizes the operation, while the fee payer authorizes payment for its execution gas.
The transaction keeps the hash of the signed inner transaction, and the block transaction root commits to the complete wrapper.

## Motivation

Requiring every sender to acquire native coin before submitting a transaction creates an additional funding step for applications and their users.
A separate account can sponsor gas while the sender retains control over the destination, value, calldata, nonce, and fee limits.
An application can therefore accept a familiar signed dynamic fee transaction and arrange sponsorship without asking the sender to sign a different operation.

A shared specification is needed for clients, wallets, signing services, and transaction indexers to agree on serialization, authorization, transaction identity, and balance changes.
JSON-RPC conventions are described separately in the [Fee Delegation JSON-RPC Extensions draft](oip-draft-fee-delegation-rpc.md).
Sponsorship service eligibility and reward distribution are outside this proposal's scope.

## Specification

### Conventions and Scope

`K(x)` denotes Keccak-256, `RLP(x)` denotes canonical Recursive Length Prefix encoding, and `||` denotes byte concatenation.
Amounts are unsigned integers in wei, and gas quantities are unsigned integers.
An address is exactly 20 bytes.

Other transaction validity and execution rules remain those of the active ONEchain fork, except where explicitly changed below.
The envelope follows [EIP-2718](https://eips.ethereum.org/EIPS/eip-2718), and the inner transaction uses the dynamic fee fields and sender authorization of [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559).

### Transaction Encoding

Define the unsigned sender fields `U` and signed sender fields `S` as the following RLP lists:

```text
U = [chain_id, nonce, max_priority_fee_per_gas, max_fee_per_gas,
     gas_limit, destination, value, data, access_list]

S = [chain_id, nonce, max_priority_fee_per_gas, max_fee_per_gas,
     gas_limit, destination, value, data, access_list,
     sender_y_parity, sender_r, sender_s]

transaction = 0x07 || RLP([
    S, fee_payer, fee_payer_y_parity, fee_payer_r, fee_payer_s
])
```

`S` MUST be an embedded RLP list, not a byte string containing a serialized `0x02` transaction.
There is no `0x02` prefix inside the wrapper.
The outer payload MUST have exactly five elements, and `S` MUST have exactly twelve elements.
Integers MUST use canonical RLP integer encoding; zero is the empty byte string and leading zero bytes are invalid.

| Field | Meaning and constraints |
| --- | --- |
| `chain_id` | The positive chain ID of the network on which the transaction is executed. |
| `nonce` | The sender's transaction nonce, encoded as an unsigned 64-bit integer. |
| `max_priority_fee_per_gas` | The priority fee cap, at most 256 bits. |
| `max_fee_per_gas` | The total execution gas price cap, at most 256 bits. |
| `gas_limit` | The execution gas allowance, encoded as an unsigned 64-bit integer. |
| `destination` | A 20-byte address, or an empty byte string for contract creation. |
| `value` | Native coin transferred from the sender, subject to the balance and overflow checks below. |
| `data` | Call data or contract initialization code. |
| `access_list` | The usual list of `[address, storage_keys]` entries, with 20-byte addresses and 32-byte storage keys. |
| `fee_payer` | A 20-byte address; an absent or empty fee payer MUST be rejected for execution. |
| Signature fields | Two secp256k1 signatures, with parity and scalar constraints defined below. |

This type contains no independent fee payer nonce, expiration, blob fields, or EIP-7702 authorization list.
It wraps only a dynamic fee transaction, not an arbitrary typed transaction.
When embedded in an RLP block body, the complete typed transaction bytes are represented as an RLP byte string, as for other typed transactions.

### Sender and Fee Payer Authorization

The sender signing hash MUST be:

```text
sender_signing_hash = K(0x02 || RLP(U))
```

The sender is the address recovered from this hash and `(sender_y_parity, sender_r, sender_s)`.
The sender's existing dynamic fee signature MUST be preserved when constructing `S`.

The fee payer signing hash MUST be:

```text
fee_payer_signing_hash = K(0x07 || RLP([S, fee_payer]))
```

The fee payer signature commits to the complete signed sender transaction and the fee payer address.
It excludes only the fee payer's own signature fields.
The address recovered from this hash and `(fee_payer_y_parity, fee_payer_r, fee_payer_s)` MUST equal the encoded `fee_payer`.

For both signatures, parity MUST be `0` or `1`, `0 < r < n`, and `0 < s <= n / 2`, where `n` is the secp256k1 group order.
The low-`s` restriction follows [EIP-2](https://eips.ethereum.org/EIPS/eip-2).
Invalid recovery, a mismatched fee payer, or a chain ID different from the execution network MUST cause rejection before EVM execution.
There is no contract-signature callback or additional fee payer nonce check.

The fee payer MAY be the sender itself, but both signatures are still required.
A sender signature does not select or restrict the sponsor: any account able to provide a valid wrapper signature can sponsor the signed operation.

### Transaction Identity and Block Commitment

The transaction hash MUST be:

```text
transaction_hash = K(0x02 || RLP(S))
```

Consequently, the ordinary signed `0x02` transaction and every valid `0x07` wrapper around the same `S` have the same transaction hash.
The hash MUST NOT be computed as `K(transaction)` for this type.
Changing only the fee payer or its signature does not change the transaction hash.

The transaction trie MUST nevertheless store the complete `0x07 || RLP(...)` encoding at the transaction's RLP-encoded block index.
Replacing a wrapper with another wrapper or with the inner `0x02` transaction changes that trie value and its root.
A transaction hash alone therefore cannot authenticate the sponsor; verification requires the full transaction and, when proving inclusion, the block transaction root.

### Validity and Execution Identity

The block's active transaction rules MUST support type `0x07`.
Sender nonce, sender account eligibility, intrinsic gas, access list, creation limits, fee caps, and block gas accounting follow the active fork's dynamic fee execution rules.
In particular, the sender nonce MUST match the pre-execution state, the fee cap MUST cover the block base fee, and the priority fee cap MUST NOT exceed the fee cap.
Successful signature decoding alone is insufficient for transaction validity.

The sender remains the transaction origin and the caller of the initial EVM operation.
Contract creation uses the sender and its nonce.
Value is transferred from the sender, and ordinary call or creation processing advances the sender's nonce even when EVM execution fails.
The fee payer's nonce MUST NOT be advanced merely because it sponsors the transaction; when sender and payer are the same account, the sender's normal nonce advancement still applies.

This transaction type adds no intrinsic gas surcharge for the wrapper or its second signature.
The fee payer MUST NOT be added to the EVM's initially warm address set solely because it pays for gas.
It can still be warm for ordinary reasons, such as appearing in the access list or also being the sender or destination.

### Gas Payment and Refunds

Let:

```text
g = gas_limit
c = max_fee_per_gas
t = max_priority_fee_per_gas
b = the block base fee
p = min(c, b + t)
v = value
```

`p` is the effective gas price and the value exposed by the EVM `GASPRICE` opcode.
Before purchasing gas, `g * c + v` MUST fit in an unsigned 256-bit integer, including when sender and payer differ.
All balances below are measured immediately before gas purchase for this transaction, after any preceding transactions in the block.

| Relationship | Required balance before execution |
| --- | --- |
| Fee payer differs from sender | Payer balance MUST cover `g * p`; sender balance MUST cover `v`. |
| Fee payer equals sender | The shared balance MUST cover `g * c + v`. |

Transaction pools may apply additional admission checks, as described below.

The implementation MUST reserve `g` from the block gas pool and debit `g * p` from the fee payer before EVM execution.
The sender pays the transferred value according to normal execution and rollback rules.
The applicable fork's gas refund cap and minimum gas charge, including any calldata gas floor, remain unchanged.

After those rules determine the remaining refundable gas `r`, the implementation MUST credit `r * p` to the fee payer and return `r` gas to the block gas pool.
The final execution gas charge is `(g - r) * p`.
An EVM revert or out-of-gas failure does not move the gas charge to the sender or cancel that charge; ordinary EVM rollback still applies to value transfers and other execution effects.
Protocol distribution of the charged fee follows the active ONEchain rules and is not changed by this proposal.

### Receipts

The consensus receipt encoding MUST use type `0x07`:

```text
receipt = 0x07 || RLP([status, cumulative_gas_used, logs_bloom, logs])
```

The receipt type MUST match the included wrapper, even though its transaction hash is derived from the signed inner transaction.
Fee payer metadata is not an additional consensus receipt field.
JSON-RPC receipt metadata does not change this consensus encoding.

### Transaction Pool Policy

Pool admission, replacement, ordering, and sponsorship service decisions are not additional block validity rules.
A pool may reserve potential payer expenditure using the gas fee cap, including cumulative reservations across transactions sharing a payer and expenditure from the payer's own transactions.
Such a pool may reject a transaction whose separate payer can cover `g * p` but cannot cover the fee-cap reservation.
Clients MUST NOT apply these local cumulative reservations as consensus checks when importing a block.

Implementations MUST validate the full wrapper before trusting its fee payer authorization; an inner transaction hash match is not evidence that a different wrapper is valid.
Applications MUST NOT assume that changing only the sponsor creates a new transaction identity or guarantees pool replacement.
Whitelist, blacklist, sponsorship approval, and external GasAbs service availability do not determine consensus validity.

## Rationale

Keeping the sender authorization identical to a dynamic fee transaction allows existing signing flows to produce the operation before a sponsor is chosen.
The second signature binds a sponsor to that exact signed operation, including fee caps and gas limit, and uses a distinct type prefix for its signing domain.

Preserving the inner transaction hash lets applications track an operation before and after sponsorship.
This intentionally makes transaction identity different from the hash of the complete wire encoding.
The transaction trie still commits to the full wrapper, so block inclusion authenticates both authorizations.

The sender nonce provides execution ordering without introducing a second nonce sequence for a sponsor serving many senders.
Refunding the payer returns unused prepaid gas to the account that supplied it.

## Backwards Compatibility

Ordinary dynamic fee transactions retain their encoding, signature, hash, and sender-funded execution.
Clients that do not support `0x07` cannot validate or execute a block containing this type.
Wallets and indexers must recognize that the wrapper's transaction hash is not the Keccak-256 hash of its raw bytes.

This proposal also does not add fee delegation to blob or set-code transactions.
Calling an account that has delegated code remains subject to the ordinary rules of the active fork; it does not add an authorization list to the wrapper.

## Test Cases

The [deterministic encoding vector](../assets/oip-2/fee-delegation.json) provides fixed test keys, sender fields, both signatures, signing preimages and hashes, raw transactions, the shared transaction hash, and a single-transaction trie root.
Decimal strings represent integer inputs unless a value starts with `0x`.
The keys are public test fixtures and MUST NOT be used to hold funds.
Independent implementations should reproduce the expected encodings and hashes and recover the listed addresses.

The following cases define the expected behavior.

| Case | Expected result |
| --- | --- |
| Encode, decode, and re-encode the vector | Identical canonical bytes; both addresses recover correctly. |
| Compare the vector's inner transaction and wrapper | Equal transaction hashes; different raw encodings and transaction trie roots. |
| Re-sign the same `S` with another declared payer | Valid new sponsorship, unchanged transaction hash, changed trie value. |
| Change the declared payer without a matching signature | Reject before execution. |
| Empty payer, malformed list, noncanonical integer, invalid parity, zero scalar, or high-`s` signature | Reject the malformed encoding or invalid authorization. |
| Execute on another chain ID | Reject. |
| Submit after the sender nonce has been consumed | Reject, regardless of the fee payer or wrapper signature. |
| Execute just before type support and at its activation boundary | Reject before support; evaluate normally once supported. |
| Separate payer with sufficient gas funds and sender with exactly `value` | Execute, charging gas to the payer and transferred value to the sender. |
| Sender equals payer | Require the combined fee-cap and value balance; advance one nonce. |
| EVM revert or out-of-gas failure | Failure receipt, sender nonce consumed, gas charged to payer, normal execution rollback. |
| Contract creation | Sender-derived creation address and nonce; payer funds gas. |
| Same payer sponsors several senders | Evaluate each transaction against the evolving block state; no separate payer nonce. |
| Access to a payer that is otherwise cold | Ordinary cold-access charge; sponsorship alone does not warm it. |

For concrete balance boundaries, take `g = 30,000`, `c = 20`, `t = 2`, `b = 12`, and `v = 100`, with prices in wei per gas.
Then `p = 14`, the upfront charge is `420,000`, and `g * c + v = 600,100`.

| Initial balances | Expected gas-purchase result |
| --- | --- |
| Separate sender `100`, payer `420,000` | Pass execution balance checks; a pool using fee-cap reservations may reject the transaction. |
| Separate sender `100`, payer `419,999` | Reject for insufficient payer funds. |
| Shared sender/payer `420,100` | Reject because the shared balance does not cover `600,100`. |
| Shared sender/payer `600,100` | Pass and debit `420,000` before execution. |

If execution finally charges `21,000` gas in this example, the gas refund is `126,000` wei and the net gas charge is `294,000` wei.
These amounts describe gas accounting only; execution may independently transfer value or change balances.

## Reference Implementation

Reference implementation: [go-cross at revision 4c0838f](https://github.com/to-nexus/go-cross/commit/4c0838f828f3a6300a1bd09fc70fec474a07a156).

- [Transaction payload and signing hashes](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/tx_feedelegate_dynamic_fee.go).
- [Transaction encoding and identity](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/types/transaction.go).
- [State transition and gas accounting](https://github.com/to-nexus/go-cross/blob/4c0838f828f3a6300a1bd09fc70fec474a07a156/core/state_transition.go).

Implementation checks and their scope are recorded in the separate [verification record](../assets/oip-2/verification.md).

## Implementation and Activation

Type `0x07` is supported by the Adventure signer and subsequent execution signers.
The reference client's default configurations set `AdventureTime` to `0` for ONEchain mainnet (`612055`) and ZoneZero (`612044`).
These settings do not establish the activation history of deployed networks.

New deployments require coordination among execution clients, wallets, sponsoring services, and indexers, together with the applicable network activation decision.
This specification records existing protocol behavior and schedules no new fork.

## Security Considerations

Both authorizations must be checked against the execution chain ID and their distinct signing hashes.
The payer's signature must be bound to the encoded payer address and the complete signed sender transaction; trusting an address field or a cached transaction hash is insufficient.
Because the hash omits the wrapper, a hash match must not bypass signature validation or be treated as proof of a particular payer's authorization.

The sender signature also authorizes the ordinary `0x02` transaction.
Anyone holding `S` can submit that transaction without sponsorship, and ordinary balance checks may then allow gas to be charged to the sender.
This format does not express a sponsorship-only intent or guarantee that a chosen sponsor will pay.

A sponsor authorizes a maximum execution allowance through the signed gas limit and fee cap.
It must evaluate execution failure, gas consumption, concurrent sponsorship, and the absence of an expiration or independent cancellation nonce.
Reverts still cost gas, and a valid authorization may be submitted later while the sender nonce remains usable.
On the canonical chain, the sender nonce prevents repeated execution; reorganizations can make the authorization usable again.

The extra signature and wrapper consume validation and propagation resources without a new intrinsic gas surcharge.
Clients should bound untrusted input and manage pool expenditure and duplicate identities without changing consensus rules.
Distinct transaction encodings with the same hash require particular care in caches, relays, and indexers.

The separate-payer effective-price balance check and the stricter pool reservation must not be confused.
Replacing either behavior without compatibility analysis can change admission or block validity.

## References

- [EIP-1559: Fee market change for ETH 1.0 chain](https://eips.ethereum.org/EIPS/eip-1559).
- [EIP-2718: Typed Transaction Envelope](https://eips.ethereum.org/EIPS/eip-2718).
- [EIP-2: Homestead Hard-fork Changes](https://eips.ethereum.org/EIPS/eip-2).

## Copyright

Copyright and related rights waived via [CC0](../LICENSE.md).
