# AI Working Log

**Case:** Northgate Outdoor Supply / Fernhill Mart  
**Analyst:** Nicolás Girón  
**Sources:** `fernhill_claims.csv`, `northgate_ledger.csv` and the case instructions.  
**Audit period:** invoices issued from 2025-01-01 through 2025-12-31, inclusive.

## Scope and transparency

This log organizes the work into four key interactions: specification, ambiguity control, exception review and consolidation. Prompts are summarized or reconstructed rather than reproduced verbatim. Personal checks and the initial interventions concerning ambiguity and OCR are described based on the candidate's account. Those initial exchanges are not present in the reviewed ChatGPT history; their exact sequence should be supported by the original conversation. The results and the assistant's executions were checked against the available files.

## 1. Rule specification and initial proposal

### Prompt submitted

**Summary of the documented prompt:**

> Act as a financial analyst and Python engineer specializing in reconciliation. Use the supplier's ledger as the only source of truth. Normalize invoice references; search by invoice first, then by PO only if it identifies exactly one invoice. Apply the 2025 audit window and the $1.00 tolerance. Generate the script, register, executive memo, ambiguity test and AI working log. Present the results row by row first.

### AI response / proposal

The AI produced a reconciliation proposal and a register with one row per claim. The documented version used normalized references, retained the original ledger identifiers in the output and applied the five specified status flags.

### Human verification and criteria applied

Based on my personal review, I checked all eight claims row by row against the original CSV files, using the ledger as independent evidence. I reviewed identity, PO uniqueness, invoice date and amount. For example, I confirmed that `88217` and `0088217` represent the same invoice, and that CLM-4403 claims $412.00 against an invoice for $380.00: a $32.00 difference.

### Adjustments / decisions made

The criterion was to accept only associations supported by the ledger. Format normalization is valid; a similar amount or an incomplete reference is insufficient to identify an invoice. Amount comparisons use `invoice_amount`, not `paid_amount`.

## 2. Human intervention: ambiguity guard for PO-5521

### Prompt submitted

**Summarized reconstruction of the intervention reported by the candidate:**

> Do not assign CLM-4404 to an invoice because its amount matches $915.75. Review every invoice associated with PO-5521 in the ledger. If there is more than one, the result must be AMBIGUOUS_NO_MATCH with no matched invoice. Add a test that prevents resolution by amount.

### AI response / proposal

In the initial exchange I describe, the AI suggested selecting an invoice based on an amount match. That proposal was rejected. This suggestion does not appear in the available ChatGPT session: its first documented version already follows the ambiguity guard.

### Human verification and criteria applied

I reviewed the ledger rows for PO-5521 and confirmed two independent invoices: `INV-10517`, for $915.75, and `INV-10519`, for $210.00. CLM-4404 has no invoice reference. Although its amount matches the first candidate, the invoice cannot be uniquely identified.

### Adjustments / decisions made

I corrected the amount-based selection described in my account. The final result is `AMBIGUOUS_NO_MATCH`, with `matched_invoice` left blank. Uniqueness is assessed across the entire ledger before applying the audit window. The test confirms that the result is unchanged even when one candidate matches the amount exactly and when the invoice order is reversed.

## 3. Human verification: OCR reference and audit window

### Prompt submitted

**Summarized reconstruction of the checks reported by the candidate:**

> Review CLM-4408 without arbitrarily replacing the letter O with zero. If INV-1O6OO does not resolve, check whether PO-5530 is unique. For CLM-4406, use the issue date of INV-09988, rather than the claim date, to assess the audit period.

### AI response / proposal

A direct search for `INV-1O6OO` does not identify a valid invoice. The final output resolves it through the unique PO. For `INV-09988`, it identifies an existing invoice outside the audit period.

### Human verification and criteria applied

I reviewed the rows in both CSV files and confirmed:

- **CLM-4408:** PO-5530 has exactly one invoice in the entire ledger, `INV-10600`, issued on 2025-06-18. Its amount of $1,502.40 matches the claim. The evidence supporting the association is the unique PO, not an assumed OCR correction.
- **CLM-4406:** `INV-09988` was issued on **2024-11-02**. The claim date, 2025-01-10, does not bring that invoice into the 2025 audit window.

### Adjustments / decisions made

`CLEAN_MATCH` is retained for CLM-4408 and `OUT_OF_PERIOD` for CLM-4406. I rejected the use of the claim date to determine scope. An invoice outside the audit period is excluded from the audited batch; that does not establish that the claim is invalid under every other audit window.

## 4. Result consolidation and review of financial decisions

### Prompt submitted

**Summary of the second documented work prompt:**

> Write an Executive Summary of no more than one page for a nontechnical manager. Explain the output register, the five scenarios and the recommendations for approval or dispute. Use a total claimed amount of $6,357.65, with $3,324.90 valid and $3,032.75 to dispute.

### AI response / proposal

The AI identified that the subtotals supplied in the prompt shifted $300.00 from matches to exceptions. It checked CLM-4405 and corrected the amounts to **$3,624.90 in CLEAN_MATCH** and **$2,732.75 in exceptions**. It also distinguished a technical match from a financial concession.

### Human verification and criteria applied

The reported row-by-row review supports checking CLM-4405: it claims $300.00 against an invoice for $299.99, a difference of **$0.01**, within tolerance. The payment of $299.97 and the arithmetic balance of $0.02 inform the commercial decision but do not change that classification. The AI identified and corrected the subtotals in this conversation; this is not attributed to a human correction.

### Adjustments / decisions made

The final documented version incorporates the corrected subtotals. `CLEAN_MATCH` is retained for CLM-4405, and matches are not all described as deductions already authorized. Recorded payments should be reviewed alongside remittance advice, credit notes and commercial evidence before conceding a deduction.

## Evidence of row-by-row review

The following matrix links each decision to verifiable data in the CSV files. It documents the candidate's reported personal review and the assistant's cross-check.

| Claim | Matched invoice | Final status | Evidence / criterion |
|---|---|---|---|
| CLM-4401 | INV-10432 | CLEAN_MATCH | Invoice dated 2025-02-14; $1,180.00 in both files. |
| CLM-4402 | 0088217 | CLEAN_MATCH | ID equivalent to 88217; invoice dated 2025-03-22; $642.50. |
| CLM-4403 | INV-10501 | AMOUNT_OVERSTATED | Invoice dated 2025-04-10; $412.00 claimed versus $380.00. |
| CLM-4404 | Blank | AMBIGUOUS_NO_MATCH | PO-5521 has two invoices; no selection by amount. |
| CLM-4405 | INV-10611 | CLEAN_MATCH | Invoice dated 2025-06-25; $300.00 versus $299.99; $0.01 difference. |
| CLM-4406 | INV-09988 | OUT_OF_PERIOD | Invoice issued on 2024-11-02; outside scope. |
| CLM-4407 | Blank | PHANTOM | INV-99981 and PO-5599 do not appear in the ledger. |
| CLM-4408 | INV-10600 | CLEAN_MATCH | Unique PO-5530; invoice dated 2025-06-18; $1,502.40. |

## Basis for the result and accountability

- **Coverage:** eight claims and eight results; the described review covers 100% of the batch rows.
- **Amount integrity:** $3,624.90 + $2,732.75 = **$6,357.65**. Exceptions consist of $412.00 for an amount discrepancy, $915.75 for ambiguity, $875.00 outside the audit period and $530.00 without a ledger record.
- **Documented automated validation:** the assistant executed seven test functions through the direct runner; all passed. They cover the ambiguous case, the complete result and the date and tolerance boundaries. The file is compatible with pytest, but pytest was unavailable in that earlier environment. The final validation below supersedes that limitation.
- **Ownership:** AI supported drafting and verification; the candidate takes responsibility for explaining each row, applying the rules and supporting commercial decisions with independent evidence.

The register is reproducible and defensible for the supplied data and the six case rules: every classification has identifiable evidence and has been checked against the expected output. This conclusion is not an absolute guarantee concerning unavailable external information or an automatic authorization of financial deductions.

## 5. Final submission review - October 1, 2026

### Prompt submitted

**English summary of the final review request:**

> Review the submission for inconsistencies and filename differences. Correct the findings, keep all deliverables and comments in English, upload the corrected files to GitHub and provide an updated ZIP.

### AI response and verification

The assistant corrected the input filenames in this log, updated the README's validation record and changed the executive summary's retailer contact to Fernhill's Accounts Payable or deductions team. The original reconciliation rules and claim classifications were retained.

The final suite was executed with Python and pytest 9.1.1: all 14 test cases passed. The development requirement now permits pytest versions from 8 up to, but excluding, 10, including the verified version. An attempted installation of pytest 8 failed because of filesystem permissions; pytest 8 execution is not claimed.

The regenerated register was compared with the delivered CSV, including every note: all eight rows matched. The claimed total is $6,357.65, consisting of $3,624.90 in CLEAN_MATCH and $2,732.75 in exceptions. The executive summary was checked to remain one page.

This final verification was performed by the assistant. It does not establish that the candidate personally repeated these checks. The candidate remains responsible for reviewing the final submission and explaining its decisions.
