import heapq
import sys

def find_cycle(remaining, deps):
    start = min(remaining)
    seen_at, path, cur = ({}, [], start)
    while cur not in seen_at:
        seen_at[cur] = len(path)
        path.append(cur)
        cur = min((d for d in deps[cur] if d in remaining))
    return path[seen_at[cur]:]

def main():
    lines = [ln.strip() for ln in sys.stdin.read().split('\n')]
    lines = [ln for ln in lines if ln]
    try:
        n, e = map(int, lines[0].split())
        names = lines[1:1 + n]
        edges = lines[1 + n:1 + n + e]
    except (ValueError, IndexError):
        sys.exit('Invalid input format')
    deps = {name: set() for name in names}
    rev = {name: [] for name in names}
    for ln in edges:
        parts = [p for p in ln.split() if p != 'imports']
        if len(parts) != 2:
            sys.exit(f'Bad import line: {ln}')
        a, b = parts
        for x in (a, b):
            if x not in deps:
                deps[x], rev[x] = (set(), [])
        if b not in deps[a]:
            deps[a].add(b)
            rev[b].append(a)
    indeg = {m: len(d) for m, d in deps.items()}
    heap = [m for m, d in indeg.items() if d == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        mod = heapq.heappop(heap)
        order.append(mod)
        for importer in rev[mod]:
            indeg[importer] -= 1
            if indeg[importer] == 0:
                heapq.heappush(heap, importer)
    if len(order) == len(deps):
        print(' '.join(order))
    else:
        done = set(order)
        remaining = {m for m in deps if m not in done}
        print('CYCLE', ' '.join(find_cycle(remaining, deps)))
if __name__ == '__main__':
    main()
