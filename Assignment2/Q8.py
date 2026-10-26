import sys

MOD = 1_000_000_007


def main():
    data = sys.stdin.buffer.read().split()
    if len(data) < 2:
        print("Error: invalid input")
        return
    n, m = int(data[0]), int(data[1])
    if not (1 <= n <= 2000 and 1 <= m <= 2000) or len(data) < 2 + n * m:
        print("Error: invalid input")
        return

    prev_s = [None] * (m + 1)
    prev_c = [0] * (m + 1)
    idx = 2
    for i in range(n):
        cur_s = [None] * (m + 1)
        cur_c = [0] * (m + 1)
        for j in range(m):
            tok = data[idx]
            idx += 1
            if tok == b"X" or tok == b"x":
                continue
            v = int(tok)
            if i == 0 and j == 0:
                cur_s[1] = v
                cur_c[1] = 1
                continue
            up, left, diag = prev_s[j + 1], cur_s[j], prev_s[j]
            best = None
            for s in (up, left, diag):
                if s is not None and (best is None or s > best):
                    best = s
            if best is None:
                continue
            cnt = 0
            if up == best:
                cnt += prev_c[j + 1]
            if left == best:
                cnt += cur_c[j]
            if diag == best:
                cnt += prev_c[j]
            cur_s[j + 1] = best + v
            cur_c[j + 1] = cnt % MOD
        prev_s, prev_c = cur_s, cur_c

    if prev_s[m] is None:
        print("IMPOSSIBLE")
    else:
        print(prev_s[m], prev_c[m] % MOD)


if __name__ == "__main__":
    main()
