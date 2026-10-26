import sys

class BankError(Exception):
    pass

class InsufficientFundsError(BankError):
    pass

class AccountNotFoundError(BankError):
    pass

class InvalidAmountError(BankError):
    pass

class BatchStateError(BankError):
    pass

class Account:

    def __init__(self, acc_id, balance=0):
        self._id = acc_id
        self._balance = 0
        self.balance = balance

    @property
    def acc_id(self):
        return self._id

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise InsufficientFundsError(f'{self._id}: negative balance not allowed')
        self._balance = value

class Transaction:

    def __init__(self, kind, source=None, target=None, amount=0):
        self.kind, self.source, self.target, self.amount = (kind, source, target, amount)
        self.status = 'PENDING'

class Bank:

    def __init__(self):
        self._accounts = {}
        self.history = []
        self._undo = None
        self._batch_txs = []
        self._batch_failed = False
        self.batch_count = 0
        self.failed_batches = []

    def add_account(self, acc_id, balance):
        self._accounts[acc_id] = Account(acc_id, balance)

    def _get(self, acc_id):
        try:
            return self._accounts[acc_id]
        except KeyError:
            raise AccountNotFoundError(f'unknown account {acc_id}') from None

    def _apply(self, tx):
        if tx.amount <= 0:
            raise InvalidAmountError('amount must be positive')
        src = self._get(tx.source) if tx.source is not None else None
        dst = self._get(tx.target) if tx.target is not None else None
        if src is not None and src.balance < tx.amount:
            raise InsufficientFundsError(f'{src.acc_id} has {src.balance}, needs {tx.amount}')
        for acc in (src, dst):
            if acc is not None and self._undo is not None:
                self._undo.append((acc, acc.balance))
        if src is not None:
            src.balance -= tx.amount
        if dst is not None:
            dst.balance += tx.amount

    def execute(self, tx):
        if self._undo is not None and self._batch_failed:
            tx.status = 'SKIPPED'
            self._batch_txs.append(tx)
            return
        try:
            self._apply(tx)
            tx.status = 'OK'
        except BankError as exc:
            tx.status = 'FAILED'
            if self._undo is not None:
                self._batch_failed = True
            else:
                print(f'REJECTED {tx.kind}: {exc}', file=sys.stderr)
        if self._undo is not None:
            self._batch_txs.append(tx)
        self.history.append(tx)

    def begin_batch(self):
        if self._undo is not None:
            raise BatchStateError('nested batch')
        self.batch_count += 1
        self._undo, self._batch_txs, self._batch_failed = ([], [], False)

    def end_batch(self):
        if self._undo is None:
            raise BatchStateError('BATCH_END without BATCH_BEGIN')
        if self._batch_failed:
            for acc, old in reversed(self._undo):
                acc.balance = old
            for tx in self._batch_txs:
                tx.status = 'ROLLED_BACK'
            self.failed_batches.append(self.batch_count)
        self._undo = None

    def in_batch(self):
        return self._undo is not None

    def report(self):
        lines = [f'FAILED {b}' for b in self.failed_batches]
        for acc_id in sorted(self._accounts):
            lines.append(f'{acc_id} {self._accounts[acc_id].balance}')
        return '\n'.join(lines)

def main():
    lines = [ln.strip() for ln in sys.stdin.read().split('\n')]
    lines = [ln for ln in lines if ln]
    bank = Bank()
    try:
        n = int(lines[0])
        for ln in lines[1:1 + n]:
            acc_id, bal = ln.split()
            bank.add_account(acc_id, int(bal))
        q = int(lines[1 + n])
        ops = lines[2 + n:2 + n + q]
    except (ValueError, IndexError, BankError):
        sys.exit('Invalid input format')
    for ln in ops:
        parts = ln.split()
        cmd = parts[0].upper()
        try:
            if cmd == 'BATCH_BEGIN':
                bank.begin_batch()
            elif cmd == 'BATCH_END':
                bank.end_batch()
            elif cmd == 'DEPOSIT' and len(parts) == 3:
                bank.execute(Transaction(cmd, None, parts[1], int(parts[2])))
            elif cmd == 'WITHDRAW' and len(parts) == 3:
                bank.execute(Transaction(cmd, parts[1], None, int(parts[2])))
            elif cmd == 'TRANSFER' and len(parts) == 4:
                bank.execute(Transaction(cmd, parts[1], parts[2], int(parts[3])))
            else:
                print(f'IGNORED: {ln}', file=sys.stderr)
        except ValueError:
            print(f'IGNORED (bad amount): {ln}', file=sys.stderr)
        except BankError as exc:
            print(f'IGNORED: {exc}', file=sys.stderr)
    if bank.in_batch():
        bank.end_batch()
    print(bank.report())
if __name__ == '__main__':
    main()
