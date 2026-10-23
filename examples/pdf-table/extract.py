"""Case-specific adapter for the pinned November 2015 NICS sample, not generic PDF extraction.

Usage: python extract.py source.pdf output-directory
Requires pdfplumber==0.11.10. No network requests during extraction.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys
import pdfplumber


def require(condition, message):
    if not condition:
        raise ValueError(message)


def extract(source, output):
    output.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(source) as pdf:
        require(len(pdf.pages) == 1, 'This adapter expects the one-page sample.')
        table = pdf.pages[0].extract_table()
    require(table and 'November - 2015' in table[0][0], 'Unexpected document.')
    with (output / 'baseline.csv').open('w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerows(table)
    header = ['State / Territory', 'Permit', 'Handgun', 'Long Gun', 'Other', 'Multiple', 'Admin']
    for group in ['Pre-Pawn', 'Redemption', 'Returned/Disposition']:
        header.extend(f'{group} {kind}' for kind in ['Handgun', 'Long Gun', 'Other'])
    header.extend(['Rentals Handgun', 'Rentals Long Gun'])
    for group in ['Private Sale', 'Return to Seller - Private Sale']:
        header.extend(f'{group} {kind}' for kind in ['Handgun', 'Long Gun', 'Other'])
    header.append('Totals')
    end = next(i for i, row in enumerate(table) if row[0] == 'Totals')
    rows = []
    for row in table[2:end]:
        require(len(row) == len(header), 'Unexpected column count.')
        names = row[0].splitlines()
        columns = []
        for cell in row:
            values = cell.splitlines() if cell else [''] * len(names)
            require(len(values) == len(names), 'Ambiguous row alignment; refusing to guess.')
            columns.append(values)
        rows.extend([list(values) for values in zip(*columns)])
    require(len(rows) == 55 and len({r[0] for r in rows}) == 55, 'Expected 55 unique jurisdictions.')
    def number(value):
        return int(value.replace(',', ''))
    def known_sum(values):
        return sum(number(v) for v in values if v != '')
    total = table[end]
    # Blanks remain blank in CSV; these checks sum known numeric entries only.
    require(all(known_sum(row[1:-1]) == number(row[-1]) for row in rows), 'Row sums disagree.')
    require(all(known_sum([row[col] for row in rows]) == number(total[col])
                for col in range(1, 25)), 'Column sums disagree.')
    # Independently transcribed from rendered source, including beginning/middle/end.
    expected = {'Alabama': (18870, 23022, 71137), 'California': (98452, 41181, 180116),
                'Michigan': (16786, 13634, 50278), 'Wyoming': (383, 1745, 5017)}
    lookup = {row[0]: row for row in rows}
    for name, values in expected.items():
        require(tuple(number(lookup[name][col]) for col in (1, 2, 24)) == values,
                f'Visual reference mismatch: {name}')
    require(number(total[-1]) == 2236457, 'Grand total disagrees with visual reference.')
    with (output / 'table.csv').open('w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerows([header] + rows + [total])
    with (output / 'table.csv').open(newline='', encoding='utf-8-sig') as f:
        saved = list(csv.reader(f))
    require(saved == [header] + rows + [total], 'CSV round-trip mismatch.')
    report = {'pdfplumber': pdfplumber.__version__, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'baseline_rows': len(table), 'jurisdictions': len(rows), 'columns': len(header),
              'csv_rows_including_header_and_total': len(saved), 'row_sum_checks': 55,
              'column_sum_checks': 24, 'visual_numeric_spot_checks': 13,
              'grand_total': number(total[-1]), 'blank_cells_preserved': True,
              'status': 'passed', 'scope': 'One upstream sample; not a held-out or A/B evaluation.'}
    (output / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    extract(Path(sys.argv[1]), Path(sys.argv[2]))
