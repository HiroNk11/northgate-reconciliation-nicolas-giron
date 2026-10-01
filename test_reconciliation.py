"""Business regression tests: run with pytest or directly with Python."""

from pathlib import Path
import sys

import pytest

from reconcile import CLAIM_FIELDS, LEDGER_FIELDS, read_csv, reconcile


def invoice(number="INV-10517", po="PO-5521", amount="915.75", day="2025-04-30"):
    return dict(invoice_number=number, po_number=po,
                invoice_amount=amount, invoice_date=day)


def claim(reference="", po="PO-5521", amount="915.75"):
    return dict(claim_id="TEST-1", invoice_ref=reference,
                po_ref=po, claimed_amount=amount)


@pytest.mark.parametrize("reverse", [False, True], ids=["original", "reversed"])
def test_ambiguous_po_5521_is_rejected_even_when_one_amount_matches(reverse):
    ledger = [invoice(), invoice("INV-10519", amount="210.00", day="2025-05-02")]
    if reverse:
        ledger.reverse()
    # One invoice matches $915.75 exactly, but the invoice identity is still ambiguous.
    result = reconcile([claim()], ledger)[0]
    assert result["status_flag"] == "AMBIGUOUS_NO_MATCH"
    assert result["matched_invoice"] == ""
    assert "INV-10517" in result["note"]
    assert "INV-10519" in result["note"]


@pytest.mark.parametrize("amount, expected", [
    ("916.75", "CLEAN_MATCH"),
    ("914.75", "CLEAN_MATCH"),
    ("916.76", "AMOUNT_OVERSTATED"),
    ("914.74", "AMOUNT_OVERSTATED"),
], ids=["above_at_limit", "below_at_limit", "above_beyond_limit", "below_beyond_limit"])
def test_tolerance_is_absolute_and_inclusive(amount, expected):
    # The case requires this same flag for every ABSOLUTE difference greater than $1.
    # Do not introduce AMOUNT_UNDERSTATED or AMOUNT_MISMATCH without changing the rules.
    result = reconcile([claim("INV-10517", amount=amount)], [invoice()])[0]
    assert result["status_flag"] == expected


@pytest.mark.parametrize("day, expected", [
    ("2024-12-31", "OUT_OF_PERIOD"),
    ("2025-01-01", "CLEAN_MATCH"),
    ("2025-12-31", "CLEAN_MATCH"),
    ("2026-01-01", "OUT_OF_PERIOD"),
], ids=["before_window", "first_day", "last_day", "after_window"])
def test_audit_window_boundaries(day, expected):
    result = reconcile([claim("INV-10517")], [invoice(day=day)])[0]
    assert result["status_flag"] == expected


def test_invoice_match_has_priority_over_ambiguous_po():
    result = reconcile([claim("INV-10517")], [invoice(), invoice("INV-10519", amount="210.00")])[0]
    assert result["status_flag"] == "CLEAN_MATCH"
    assert result["matched_invoice"] == "INV-10517"


def test_out_of_period_has_priority_over_amount_mismatch():
    result = reconcile([claim("INV-10517", amount="9999.00")], [invoice(day="2024-11-02")])[0]
    assert result["status_flag"] == "OUT_OF_PERIOD"


def test_out_of_period_candidate_is_still_counted_for_po_ambiguity():
    ledger = [invoice(), invoice("INV-10519", day="2024-11-02")]
    assert reconcile([claim()], ledger)[0]["status_flag"] == "AMBIGUOUS_NO_MATCH"


@pytest.fixture(scope="module")
def supplied_case():
    """The actual CSV files are official fixtures included alongside the test in the ZIP."""
    base = Path(__file__).resolve().parent
    claims_path = base / "fernhill_claims.csv"
    ledger_path = base / "northgate_ledger.csv"
    missing = [path.name for path in (claims_path, ledger_path) if not path.is_file()]
    if missing:
        pytest.fail(
            f"Missing CSV fixtures in {base}: {', '.join(missing)}. "
            "Extract the entire ZIP and keep both CSV files alongside the test.",
            pytrace=False,
        )
    claims = read_csv(claims_path, CLAIM_FIELDS)
    ledger = read_csv(ledger_path, LEDGER_FIELDS)
    return claims, ledger


def test_full_supplied_case(supplied_case):
    claims, ledger = supplied_case
    assert len(claims) == 8
    assert len(ledger) == 10
    assert any(row["invoice_number"] == "0088217" for row in ledger)
    results = reconcile(claims, ledger)
    assert [(row["claim_id"], row["matched_invoice"], row["status_flag"]) for row in results] == [
        ("CLM-4401", "INV-10432", "CLEAN_MATCH"),
        ("CLM-4402", "0088217", "CLEAN_MATCH"),
        ("CLM-4403", "INV-10501", "AMOUNT_OVERSTATED"),
        ("CLM-4404", "", "AMBIGUOUS_NO_MATCH"),
        ("CLM-4405", "INV-10611", "CLEAN_MATCH"),
        ("CLM-4406", "INV-09988", "OUT_OF_PERIOD"),
        ("CLM-4407", "", "PHANTOM"),
        ("CLM-4408", "INV-10600", "CLEAN_MATCH"),
    ]


if __name__ == "__main__":
    # pytest reports each case, continues after failures and returns the exit code.
    # This entry point also requires pytest; it avoids duplicating parametrization logic.
    raise SystemExit(pytest.main([str(Path(__file__).resolve()), *sys.argv[1:]]))
