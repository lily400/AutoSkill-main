def solve(input_data):
    """Processed Reviews CSV Conformance Validator with Casing Enforcement.

    SOP source: <input_validation> Validating Processed Reviews (CSV)
    """
    import csv
    import io

    csv_text = input_data.get('csv_text', '')

    # Document-specific constants (SOP: <input_validation> Validating Processed Reviews (CSV))
    REQUIRED_COLUMNS = [
        'review_id', 'review', 'is_sportswear', 'is_apparel_product', 'brand', 'competitor_or_nike'
    ]
    ALLOWED_IS = {'yes', 'no'}
    ALLOWED_COMP = {'nike', 'competitor', 'n/a'}
    MIN_ROWS = 20

    def error(issue):
        # Exact SOP ERROR template for processed reviews
        msg = (
            'ERROR: Invalid processed reviews received from orchestrator.\n\n'
            f'Issue: {issue}\n\n'
            'Required format: CSV output from review_processor with all classification columns.\n\n'
            'Cannot proceed with review analysis. Please provide corrected processed reviews.'
        )
        return {
            'ok': False,
            'message': msg,
            'details': {
                'row_count': 0,
                'missing_columns': [],
                'invalid_values': []
            }
        }

    # 1) Parse CSV
    try:
        f = io.StringIO(csv_text)
        reader = csv.reader(f)
        rows = list(reader)
    except Exception:
        return error('Valid CSV format that can be parsed')

    if not rows:
        return error('Valid CSV format that can be parsed')

    header = rows[0]
    data_rows = rows[1:]

    # Normalize header whitespace only (SOP does not allow value normalization; header trimming is pragmatic)
    header = [h.strip() for h in header]

    col_index = {name: i for i, name in enumerate(header)}

    # 2) Required columns present (precedence #1)
    missing = [c for c in REQUIRED_COLUMNS if c not in col_index]
    if missing:
        # SOP example style: Missing column 'competitor_or_nike'
        issue = f"Missing column '{missing[0]}'"
        out = error(issue)
        out['details']['row_count'] = len(data_rows)
        out['details']['missing_columns'] = missing
        return out

    # 3) Validate classification values (precedence #2)
    invalids = []
    for r_i, row in enumerate(data_rows, start=1):  # 1-based data row index
        # Pad short rows
        if len(row) < len(header):
            row = row + [''] * (len(header) - len(row))

        is_sportswear = row[col_index['is_sportswear']].strip().lower()
        is_apparel = row[col_index['is_apparel_product']].strip().lower()
        comp = row[col_index['competitor_or_nike']].strip().lower()

        if is_sportswear not in ALLOWED_IS:
            invalids.append({'row': r_i, 'column': 'is_sportswear', 'value': is_sportswear})
        elif is_apparel not in ALLOWED_IS:
            invalids.append({'row': r_i, 'column': 'is_apparel_product', 'value': is_apparel})
        elif comp not in ALLOWED_COMP:
            invalids.append({'row': r_i, 'column': 'competitor_or_nike', 'value': comp})

        if invalids:
            break

    if invalids:
        first = invalids[0]
        col = first['column']
        val = first['value']
        # SOP example style includes lowercase requirement when casing is wrong
        if col in ('is_sportswear', 'is_apparel_product'):
            issue = f"Found invalid value '{val}' in {col} column (must be lowercase 'yes')" if val.lower() == 'yes' else f"Found invalid value '{val}' in {col} column"
        else:
            issue = f"Found invalid value '{val}' in {col} column"
        out = error(issue)
        out['details']['row_count'] = len(data_rows)
        out['details']['invalid_values'] = invalids
        return out

    # 4) Minimum row count (precedence #3)
    if len(data_rows) < MIN_ROWS:
        out = error(f'Only {len(data_rows)} rows found, expected at least {MIN_ROWS}')
        out['details']['row_count'] = len(data_rows)
        return out

    # Success
    return {
        'ok': True,
        'message': f'SUCCESS: Processed reviews CSV validated ({len(data_rows)} rows).',
        'details': {
            'row_count': len(data_rows),
            'missing_columns': [],
            'invalid_values': []
        }
    }
