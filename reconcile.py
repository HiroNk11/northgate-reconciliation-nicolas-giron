"""Reconcile claims against the independent ledger without external dependencies."""

import argparse
import csv
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

AUDIT_START = date(2025, 1, 1)
AUDIT_END = date(2025, 12, 31)
TOLERANCE = Decimal("1.00")
OUTPUT_FIELDS = ["claim_id", "matched_invoice", "status_flag", "note"]
CLAIM_FIELDS = {"claim_id", "invoice_ref", "po_ref", "claimed_amount"}
LEDGER_FIELDS = {"invoice_number", "po_number", "invoice_date", "invoice_amount"}


def canonical_invoice(value):
    """Remove INV- and leading zeros; do not guess corrections for OCR letters."""
    text = value.strip().upper()
    if text.startswith("INV-"):
        text = text[4:]
    if not re.fullmatch(r"[0-9]+", text):
        return None
    return text.lstrip("0") or "0"


def canonical_po(value):
    """Normalize surrounding whitespace and case; preserve the PO identifier."""
    return value.strip().upper()


def money(value):
    """Use exact decimal arithmetic and reject invalid amounts."""
    try:
        amount = Decimal(value.strip())
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {value!r}") from exc
    if not amount.is_finite():
        raise ValueError(f"Non-finite amount: {value!r}")
    return amount


def read_csv(path, required_fields):
    """csv.DictReader returns text, preserving leading zeros and blank references."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        missing = required_fields - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        rows = list(reader)
    for number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{path}: row {number} has missing or extra columns")
    return rows


def reconcile(claims, ledger):
    """Return one row per claim in the same order as the source file."""
    by_invoice = {}
    by_po = defaultdict(list)

    # Index the ENTIRE ledger: filtering by date first could conceal ambiguity.
    for invoice in ledger:
        key = canonical_invoice(invoice["invoice_number"])
        if key is None or key in by_invoice:
            raise ValueError("Invalid or duplicate invoice number in the ledger: "
                             + invoice["invoice_number"])
        date.fromisoformat(invoice["invoice_date"].strip())
        money(invoice["invoice_amount"])
        by_invoice[key] = invoice
        po = canonical_po(invoice["po_number"])
        if po:
            by_po[po].append(invoice)

    register = []
    seen_claims = set()
    for claim in claims:
        claim_id = claim["claim_id"].strip()
        if not claim_id or claim_id in seen_claims:
            raise ValueError(f"Empty or duplicate claim_id: {claim_id!r}")
        seen_claims.add(claim_id)
        claimed = money(claim["claimed_amount"])
        invoice_key = canonical_invoice(claim["invoice_ref"])
        invoice = by_invoice.get(invoice_key)
        match_method = "Normalized invoice match"
        row = dict(claim_id=claim_id, matched_invoice="", status_flag="", note="")

        # Priority 1: invoice. Priority 2: PO with exactly one candidate.
        if invoice is None:
            po = canonical_po(claim["po_ref"])
            candidates = by_po.get(po, [])
            if len(candidates) > 1:
                ids = "; ".join(item["invoice_number"] for item in candidates)
                row.update(status_flag="AMBIGUOUS_NO_MATCH",
                           note=f"{po}: {len(candidates)} invoices ({ids}); "
                                "no candidate selected by amount.")
            elif not candidates:
                row.update(status_flag="PHANTOM",
                           note="No invoice or PO match in the ledger.")
            else:
                invoice = candidates[0]
                match_method = f"Fallback through unique PO {po}"
            if invoice is None:
                register.append(row)
                continue

        # Preserve the original ledger ID to keep the evidence traceable.
        row["matched_invoice"] = invoice["invoice_number"]
        invoice_date = date.fromisoformat(invoice["invoice_date"].strip())
        invoice_amount = money(invoice["invoice_amount"])
        difference = abs(claimed - invoice_amount)

        # The INVOICE date takes precedence over any amount difference.
        if not AUDIT_START <= invoice_date <= AUDIT_END:
            row.update(status_flag="OUT_OF_PERIOD",
                       note=f"{match_method}; invoice_date={invoice_date} "
                            "outside the 2025 audit window.")
        elif difference > TOLERANCE:
            # The required flag also applies when the claim is lower by more than $1.
            row.update(status_flag="AMOUNT_OVERSTATED",
                       note=f"{match_method}; claim=${claimed:.2f}, "
                            f"invoice=${invoice_amount:.2f}; "
                            f"absolute difference=${difference:.2f} > $1.00.")
        else:
            row.update(status_flag="CLEAN_MATCH",
                       note=f"{match_method}; absolute difference="
                            f"${difference:.2f} <= $1.00; invoice dated in 2025.")
        register.append(row)
    return register


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, default=Path("fernhill_claims.csv"))
    parser.add_argument("--ledger", type=Path, default=Path("northgate_ledger.csv"))
    parser.add_argument("--output", type=Path, default=Path("reconciliation_register.csv"))
    args = parser.parse_args()
    try:
        claims = read_csv(args.claims, CLAIM_FIELDS)
        ledger = read_csv(args.ledger, LEDGER_FIELDS)
        register = reconcile(claims, ledger)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8-sig", newline="") as destination:
            writer = csv.DictWriter(destination, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(register)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"{len(register)} claims processed. Register: {args.output}")


if __name__ == "__main__":
    main()
