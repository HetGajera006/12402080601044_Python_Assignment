import re
import sys
from collections import deque
SPECIAL = set('$#@')
REPEAT = re.compile('(.)\\1{3}')

class AhoCorasick:

    def __init__(self, words):
        self.go = [{}]
        self.fail = [0]
        self.out = [False]
        for w in words:
            self._insert(w)
        self._build()

    def _insert(self, word):
        node = 0
        for ch in word:
            nxt = self.go[node].get(ch)
            if nxt is None:
                self.go.append({})
                self.fail.append(0)
                self.out.append(False)
                nxt = len(self.go) - 1
                self.go[node][ch] = nxt
            node = nxt
        self.out[node] = True

    def _build(self):
        queue = deque(self.go[0].values())
        while queue:
            u = queue.popleft()
            for ch, v in self.go[u].items():
                f = self.fail[u]
                while f and ch not in self.go[f]:
                    f = self.fail[f]
                self.fail[v] = self.go[f].get(ch, 0)
                self.out[v] = self.out[v] or self.out[self.fail[v]]
                queue.append(v)

    def contains(self, text):
        state = 0
        for ch in text:
            while state and ch not in self.go[state]:
                state = self.fail[state]
            state = self.go[state].get(ch, 0)
            if self.out[state]:
                return True
        return False

def classify(pw, automaton):
    if not 6 <= len(pw) <= 12:
        return 'WEAK_LENGTH'
    if automaton.contains(pw.lower()):
        return 'COMPROMISED'
    if REPEAT.search(pw):
        return 'WEAK_PATTERN'
    has_lower = any((c.islower() for c in pw))
    has_upper = any((c.isupper() for c in pw))
    has_digit = any((c.isdigit() for c in pw))
    has_special = any((c in SPECIAL for c in pw))
    if not (has_lower and has_upper and has_digit and has_special):
        return 'WEAK_PATTERN'
    return 'STRONG'

def main():
    lines = sys.stdin.read().split('\n')
    lines = [ln.rstrip('\r') for ln in lines]
    try:
        b = int(lines[0])
        banned = [w.strip().lower() for w in lines[1:1 + b] if w.strip()]
        n = int(lines[1 + b])
    except (ValueError, IndexError):
        sys.exit('Invalid input format')
    passwords = lines[2 + b:2 + b + n]
    passwords += [''] * (n - len(passwords))
    automaton = AhoCorasick(banned)
    out = [f'{i}: {classify(pw, automaton)}' for i, pw in enumerate(passwords, 1)]
    print('\n'.join(out))
if __name__ == '__main__':
    main()
