import sys
import heapq

def fail(msg):
    sys.exit(f'Invalid input: {msg}')

def main():
    data = sys.stdin.read().split()
    try:
        n, k, m = (int(data[0]), int(data[1]), int(data[2]))
    except (IndexError, ValueError):
        fail('first line must be: n k m')
    if not (1 <= n <= 100000 and 1 <= k <= 50 and (1 <= m <= 12)):
        fail('n, k or m out of range')
    by_sem = {}
    best_mark = [-1] * m
    best_ids = [[] for _ in range(m)]
    pos = 3
    for _ in range(n):
        if pos + 4 + m > len(data):
            fail('truncated records')
        enr, name = (data[pos], data[pos + 1])
        try:
            sem = int(data[pos + 2])
            cpi = float(data[pos + 3])
            marks = tuple((int(x) for x in data[pos + 4:pos + 4 + m]))
        except ValueError:
            fail(f'non-numeric value in record of {enr}')
        if not (1 <= sem <= 8 and 0.0 <= cpi <= 10.0 and all((0 <= x <= 100 for x in marks))):
            fail(f'value out of range in record of {enr}')
        pos += 4 + m
        record = (enr, name, sem, cpi, marks)
        by_sem.setdefault(sem, []).append((-record[3], -sum(marks), enr))
        for i, mk in enumerate(marks):
            if mk > best_mark[i]:
                best_mark[i], best_ids[i] = (mk, [enr])
            elif mk == best_mark[i]:
                best_ids[i].append(enr)
    for sem in sorted(by_sem):
        top = heapq.nsmallest(k, by_sem[sem])
        print(f'Semester {sem}: ' + ' '.join((t[2] for t in top)))
    for i in range(m):
        print(f'S{i + 1}: ' + ' '.join(sorted(best_ids[i])))
if __name__ == '__main__':
    main()
