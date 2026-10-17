# Echo Turnstile

Echo Turnstile is an intake gate for repeated public requests. A lane carries one explicit semantic-duplicate rule and a cooldown. Each arriving request is compared only with active admitted tickets; it is admitted when the agreed duplicate set is empty and redirected when one or more active ticket IDs match.

## Operating rule

The model may identify matching active IDs, but it cannot choose the state. The contract validates that every returned ID belongs to the frozen active set, sorts the IDs, and deterministically assigns `ADMITTED` or `REDIRECTED`.

## Receipt anatomy

Every ticket receipt keeps:

- the submitting wallet and lane;
- the complete payload URL and SHA-256 digest;
- the exact duplicate ticket IDs;
- the creation time and final routing state.

Active payloads are fetched again during each scan and must still match their stored digests. The lane is capped at eight active admitted tickets, so operators must expire elapsed tickets instead of silently dropping context.

## Verification

```powershell
genvm-lint contracts\contract.py
pytest -q tests
```

`scripts/live_smoke.py` demonstrates all three paths: a first admission, a semantic redirect, and a distinct second admission. The resulting transaction hashes and ticket receipts are saved under `evidence/`.

The sample requests are controlled fixtures for repeatable review, not claims about third-party production traffic.
