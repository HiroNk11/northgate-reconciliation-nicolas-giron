# Northgate / Fernhill Reconciliation

## Submission files

- `reconcile.py`: reconciliation script.
- `reconciliation_register.csv`: one result per claim, with English notes.
- `executive_summary_fernhill_northgate.pdf`: one-page executive summary.
- `test_reconciliation.py`: parametrized tests, including the PO-5521 ambiguity guard.
- `AI_Working_Log_Final.md`: AI working log.

The repository and ZIP also include `fernhill_claims.csv`, `northgate_ledger.csv` and `requirements-dev.txt`. Keep all files together after extraction; the inputs are the official fixtures for the full-case test.

## Run the reconciliation

```bash
python reconcile.py
```

The reconciliation script uses only the Python standard library. It preserves identifiers as text and uses exact decimal arithmetic for the $1.00 tolerance.

## Run the tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q test_reconciliation.py
```

Alternatively, run `python test_reconciliation.py -q`; this entry point also requires pytest. The 14 parametrized cases are reported independently. The full-case fixture locates the input CSV files relative to the test file, regardless of the working directory.

Final verification (October 1, 2026): all 14 test cases passed under pytest 9.1.1. The generated register matched all eight delivered rows and notes. `requirements-dev.txt` allows `pytest>=8,<10`, including the verified version. Earlier validation details remain in the AI working log as historical context.

## Business interpretation

`AMOUNT_OVERSTATED` is the required flag for any absolute difference above $1.00, including a claim below the invoice amount. A `CLEAN_MATCH` confirms identity, period and amount; it does not automatically authorize a financial concession.

The amounts retain the case's $ symbol without assuming a currency not specified in the source.
