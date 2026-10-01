# Northgate / Fernhill Reconciliation

## Submission files

- `reconcile.py`: reconciliation script.
- `reconciliation_register.csv`: one result per claim, with English notes.
- `executive_summary_fernhill_northgate.pdf`: one-page executive summary.
- `test_reconciliation.py`: parametrized tests, including the PO-5521 ambiguity guard.
- `AI_Working_Log_Final.md`: AI working log.

The ZIP also includes the two original CSV inputs and `requirements-dev.txt`. Keep all files together after extraction; the inputs are the official fixtures for the full-case test.

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

Translation verification: syntax and reconciliation outputs were checked. The 14 test cases were checked through auxiliary execution of their assertions without pytest decorators. pytest collection and fixture resolution were not executed in the translation environment because pytest was unavailable. The working log retains its historical record of seven test functions executed before the parametrization update.

## Business interpretation

`AMOUNT_OVERSTATED` is the required flag for any absolute difference above $1.00, including a claim below the invoice amount. A `CLEAN_MATCH` confirms identity, period and amount; it does not automatically authorize a financial concession.

The amounts retain the case's $ symbol without assuming a currency not specified in the source.
