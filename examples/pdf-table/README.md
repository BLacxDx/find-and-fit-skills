# One complete PDF-to-CSV case

Date: 2026-10-23. Windows, Python 3.12.10, pdfplumber 0.11.10.

## Task and selection

Representative user task: extract the jurisdiction table from a public PDF into a usable CSV on Windows, without a paid API or uploading the document. This task was selected by the maintainer's assistant, not supplied by an external user.

Find and Fit was explicitly read and followed in the current conversation. An existing PDF skill already recommended pdfplumber, so the correct decision was reuse rather than installing another skill. Its Python runtime was missing; pdfplumber was installed from PyPI into an isolated test environment. The discovery helper inspected jsvine/pdfplumber and returned a non-archived repository with MIT license metadata and commit-pinned documentation. This is a library candidate, not a newly discovered installable Skill.

Constraints: Windows and CSV output were executed; no paid API or account was needed. Installation and source download used the network. Extraction was rerun with Python socket connect/create_connection blocked. This demonstrates that extraction completed without those network calls, not a general security audit.

## Source and reproduction

Source: [November 2015 NICS public table, mirrored in pdfplumber's examples](https://raw.githubusercontent.com/jsvine/pdfplumber/4c64b92d5caccd71c645e98e0fabb0c4dba7ff45/examples/pdfs/background-checks.pdf).

SHA-256: `4f0ae6e017b0e97de211da8fd97316e55bd927af5740d6ce95e1b7b1539f9407`.

This is a real published table but also an upstream demonstration fixture; it is not an unseen or unbiased benchmark. Source notes say the figures are background checks, not firearm sales. Blank entries are preserved, not converted into recorded zero values.

Download the pinned PDF as `source.pdf`, then in an isolated environment:

```text
python -m pip install pdfplumber==0.11.10
python examples/pdf-table/extract.py source.pdf output
```

The adapter writes `baseline.csv`, `table.csv` and `result.json`. It is specific to this sample and rejects incompatible structure. It does not download or execute repository code. Review the script before running.

## Failure, narrow fix and checks

The default `extract_table()` returned 17 physical rows: groups of five jurisdictions were joined inside cells, alongside title/header/footer rows. That output was unsuitable for one-jurisdiction-per-row CSV. The adapter expands multiline cells only when their lengths agree, assigns the hierarchical column labels from the rendered source, excludes title/footnotes from data rows, and preserves blanks. This fixes the task adapter; it is not an upstream pdfplumber bug fix.

Acceptance results:

- 55 unique jurisdictions, 25 columns; 57 CSV rows including header and national total.
- All 55 row sums and 24 column sums agree when summing known numeric entries.
- 13 numeric values transcribed from the rendered source agree: Permit, Handgun and Total for Alabama, California, Michigan and Wyoming, plus national total 2,236,457.
- CSV reread equals the in-memory structured table.
- An additional run with Python socket connections blocked passes the same checks.

We visually inspected the source page and headers; we did not independently transcribe every cell. Sum checks do not exclude every possible compensating error. The sample and adapter were developed together, so this is a demonstration of a repaired workflow, not held-out validation.

## Change to the Skill and limits

Added a specific output-verification step: reopen results and check record boundaries, field names, missing values and source-derived samples before declaring success. It also distinguishes upstream sample tests and reuse of installed skills from new discovery.

No baseline/skill A/B model sessions were run. We do not claim that Find and Fit improved model accuracy, that it independently found this tool, or that this works for scanned PDFs. The tool plus the small adapter completed this one task; broader discovery relevance and user adoption remain unproven.
