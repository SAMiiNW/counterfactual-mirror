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
