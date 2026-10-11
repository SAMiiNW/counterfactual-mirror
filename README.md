# COUNTERFACTUAL MIRROR

```text
PAIR LOCKED     same decision system, declared protected axis
FACTOR SWEEP    every non-protected factor partitioned
OUTCOME CHECK   parity | justified difference | disparate result
```

Two decisions can look individually plausible and still fail the simplest fairness test: would the outcome change if only a protected attribute changed?

The owner freezes a public decision policy, a protected axis, two to eight material non-protected factors, the allowed outcome codes, and a separate auditor. The auditor supplies two public case records and their recorded outcomes. Validators retrieve all three sources and agree on whether the protected axis differs, which material factors match, which differ, whether the policy supports an outcome divergence, and the exact byte digests.

Contract code derives the final signal:

- `INVALID_PAIR` when the protected axis does not differ.
- `NOT_COMPARABLE` when any declared material factor differs.
- `PARITY` when a comparable pair received the same outcome.
- `JUSTIFIED_DIFFERENCE` when a comparable pair received different outcomes explicitly supported by the frozen policy.
- `DISPARATE` when only the protected axis differs and the policy does not support the outcome split.

The model does not write the verdict. It returns a bounded factor partition and policy finding; deterministic code applies the state rule. The contract stores no free-form rationale as authority.

## Bench sequence

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```

The repository fixtures are synthetic pair records for technical verification. They do not claim a real discrimination finding or independent institutional authorship.

## StudioNet inspection strip

- Contract: [`0x3863C337Fe34Be7Bb8796Fc634FbaaB6487f922a`](https://explorer-studio.genlayer.com/address/0x3863C337Fe34Be7Bb8796Fc634FbaaB6487f922a)
- Deployment: [`0x2a5254...7fd2c6`](https://explorer-studio.genlayer.com/tx/0x2a5254a6a0553e9346360aad0add689637a5a23b1d70549dea42c76a867fd2c6)
- Pair registration: [`0x085e8a...afb18a`](https://explorer-studio.genlayer.com/tx/0x085e8a274bc8af1c3e334c101a0d755eeb8a65b3bedbb477d3d1d68a80afb18a)
- Pair inspection: [`0xab3d65...1ded16`](https://explorer-studio.genlayer.com/tx/0xab3d657a84c652a5f7c1b30d417c2ad7af9ac9bdc2a0dfd4262f3bc2471ded16)
- Final record: `PAIR-1791754602`, all three material factors equal, `UNSUPPORTED` divergence, state `DISPARATE`.
- Exact deployed source SHA-256: `678afe2fc33f8706708e2b513c241e1f82bbb01f7f6d12340878d073a9e6f83e`.
