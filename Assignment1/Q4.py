import csv
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
TS_FORMAT = '%Y-%m-%dT%H:%M:%S'
HEADER = ['transaction_id', 'account_id', 'type', 'amount', 'timestamp']

class ValidationError(Exception):
    pass

def validate(row):
    if len(row) != 5:
        raise ValidationError(f'expected 5 columns, got {len(row)}')
    tid, acc, ttype, amount, ts = (c.strip() for c in row)
    if not tid:
        raise ValidationError('empty transaction_id')
    if not acc:
        raise ValidationError('empty account_id')
    ttype = ttype.upper()
    if ttype not in ('CREDIT', 'DEBIT'):
        raise ValidationError(f"invalid type '{row[2].strip()}'")
    try:
        amt = Decimal(amount)
    except InvalidOperation:
        raise ValidationError('amount is not numeric') from None
    if not amt.is_finite():
        raise ValidationError('amount is not finite')
    if amt <= 0:
        raise ValidationError('amount must be > 0')
    try:
        datetime.strptime(ts, TS_FORMAT)
    except ValueError:
        raise ValidationError('invalid timestamp (need yyyy-mm-ddThh:mm:ss)') from None
    return (tid, acc, ttype, amt, ts)

def fmt(d):
    return format(d.normalize(), 'f') if d != 0 else '0'

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else input('Input CSV path: ').strip()
    balances = defaultdict(Decimal)
    try:
        with open(path, newline='', encoding='utf-8', errors='replace') as src, open('credit.csv', 'w', newline='') as fc, open('debit.csv', 'w', newline='') as fd, open('error.csv', 'w', newline='') as fe:
            reader = csv.reader(src)
            wc, wd, we = (csv.writer(fc), csv.writer(fd), csv.writer(fe))
            wc.writerow(HEADER)
            wd.writerow(HEADER)
            we.writerow(['line', 'row', 'reason'])
            next(reader, None)
            while True:
                try:
                    row = next(reader)
                except StopIteration:
                    break
                except csv.Error as exc:
                    we.writerow([reader.line_num, '', f'CSV error: {exc}'])
                    continue
                if not row:
                    continue
                try:
                    tid, acc, ttype, amt, ts = validate(row)
                except ValidationError as exc:
                    we.writerow([reader.line_num, ','.join(row), str(exc)])
                    continue
                out = [tid, acc, ttype, fmt(amt), ts]
                if ttype == 'CREDIT':
                    wc.writerow(out)
                    balances[acc] += amt
                else:
                    wd.writerow(out)
                    balances[acc] -= amt
    except FileNotFoundError:
        sys.exit(f'File not found: {path}')
    except PermissionError as exc:
        sys.exit(f'Permission problem: {exc}')
    for acc, bal in sorted(balances.items(), key=lambda kv: (-abs(kv[1]), kv[0])):
        print(acc, fmt(bal))
if __name__ == '__main__':
    main()
