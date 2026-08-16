import update

def cvm_number(value):
    if value is None or value == '':
        return None
    text = str(value).strip()
    try:
        if ',' in text:
            return float(text.replace('.', '').replace(',', '.'))
        return float(text)
    except ValueError:
        return None

_original_rows = update.csv_rows

def all_reported_rows(zf, contains):
    for row in _original_rows(zf, contains) or []:
        row['ST_CONTA_FIXA'] = 'S'
        yield row

update.number = cvm_number
update.csv_rows = all_reported_rows

if __name__ == '__main__':
    update.main()
