import heapq
import html
import re
import sys

START_RE = re.compile(
    r"""<(?:div|li|article|tr|section)\b[^>]*class\s*=\s*["'][^"']*(?<![\w-])product(?![\w-])[^"']*["'][^>]*>""",
    re.I,
)
NAME_RE = re.compile(r"""class\s*=\s*["'][^"']*(?:name|title)[^"']*["'][^>]*>(.*?)</""", re.I | re.S)
PRICE_RE = re.compile(r"""class\s*=\s*["'][^"']*price[^"']*["'][^>]*>(.*?)</""", re.I | re.S)
RATING_RE = re.compile(r"""class\s*=\s*["'][^"']*rating[^"']*["'][^>]*>(.*?)</""", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def clean_text(s):
    return " ".join(html.unescape(TAG_RE.sub("", s)).split())


def parse_number(s):
    m = NUM_RE.search(clean_text(s).replace(",", ""))
    return float(m.group()) if m else None


def fmt_price(p):
    return str(int(p)) if p == int(p) else f"{p:.2f}"


def parse_page(text):
    for chunk in START_RE.split(text)[1:]:
        n, p, r = NAME_RE.search(chunk), PRICE_RE.search(chunk), RATING_RE.search(chunk)
        if not (n and p and r):
            continue
        name = clean_text(n.group(1))
        price = parse_number(p.group(1))
        rating = parse_number(r.group(1))
        if not name or price is None or rating is None:
            continue
        yield name, price, rating


def main():
    first = sys.stdin.readline().split()
    if len(first) != 2 or not all(x.isdigit() for x in first):
        print("Error: first line must be 'p k'")
        sys.exit(1)
    p, k = int(first[0]), int(first[1])
    if not (1 <= p <= 5000 and 1 <= k <= 1000):
        print("Error: constraints 1<=p<=5000 and 1<=k<=1000")
        sys.exit(1)
    best = {}
    for _ in range(p):
        path = sys.stdin.readline().strip()
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError as e:
            print(f"Skipping {path}: {e}", file=sys.stderr)
            continue
        for name, price, rating in parse_page(text):
            old = best.get(name)
            if old is None or (-rating, price) < (-old[1], old[0]):
                best[name] = (price, rating)
    top = heapq.nsmallest(k, ((-r, pr, n) for n, (pr, r) in best.items()))
    for neg_r, pr, n in top:
        print(n, fmt_price(pr), f"{-neg_r:g}")


if __name__ == "__main__":
    main()
