import re
import sys
import threading
TOKEN = re.compile('\\s*(?:(\\d+)|([A-Za-z_]\\w*)|([-+*()]))')

class InvalidExpr(Exception):
    pass

class CycleError(Exception):
    pass

def tokenize(text):
    text = text.rstrip()
    pos, out = (0, [])
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise InvalidExpr
        if m.group(1) is not None:
            out.append(('num', int(m.group(1))))
        elif m.group(2) is not None:
            out.append(('id', m.group(2)))
        else:
            out.append(('op', m.group(3)))
        pos = m.end()
    return out

class Engine:

    def __init__(self, definitions):
        self.defs = definitions
        self.memo = {}
        self.visiting = set()

    def value_of(self, name):
        if name in self.memo:
            return self.memo[name]
        if name not in self.defs:
            raise InvalidExpr
        if name in self.visiting:
            raise CycleError
        self.visiting.add(name)
        result = Parser(tokenize(self.defs[name]), self).parse()
        self.visiting.discard(name)
        self.memo[name] = result
        return result

class Parser:

    def __init__(self, tokens, engine):
        self.t, self.i, self.engine = (tokens, 0, engine)

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def parse(self):
        value = self.expr()
        if self.i != len(self.t):
            raise InvalidExpr
        return value

    def expr(self):
        value = self.term()
        while self.peek() in (('op', '+'), ('op', '-')):
            op = self.t[self.i][1]
            self.i += 1
            rhs = self.term()
            value = value + rhs if op == '+' else value - rhs
        return value

    def term(self):
        value = self.factor()
        while self.peek() == ('op', '*'):
            self.i += 1
            value *= self.factor()
        return value

    def factor(self):
        kind, val = self.peek()
        if kind == 'num':
            self.i += 1
            return val
        if kind == 'id':
            self.i += 1
            return self.engine.value_of(val)
        if (kind, val) == ('op', '('):
            self.i += 1
            value = self.expr()
            if self.peek() != ('op', ')'):
                raise InvalidExpr
            self.i += 1
            return value
        raise InvalidExpr

def solve():
    lines = sys.stdin.read().split('\n')
    try:
        v = int(lines[0])
    except (ValueError, IndexError):
        print('INVALID')
        return
    defs = {}
    try:
        for ln in lines[1:1 + v]:
            name, expr = ln.split('=', 1)
            name = name.strip()
            if not name.isidentifier():
                raise ValueError
            defs[name] = expr
        target = lines[1 + v]
    except (ValueError, IndexError):
        print('INVALID')
        return
    try:
        print(Parser(tokenize(target), Engine(defs)).parse())
    except CycleError:
        print('CYCLE')
    except InvalidExpr:
        print('INVALID')
if __name__ == '__main__':
    sys.setrecursionlimit(10 ** 7)
    threading.stack_size(512 * 1024 * 1024)
    t = threading.Thread(target=solve)
    t.start()
    t.join()
