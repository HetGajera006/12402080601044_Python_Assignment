import math
import sys
from functools import total_ordering


def to_num(s):
    try:
        v = int(s)
    except ValueError:
        v = float(s)
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError("non-finite number")
    if v < 0:
        raise ValueError("negative number")
    return v


class Product:
    __slots__ = ("pid", "name", "stock", "purchase", "selling")

    def __init__(self, pid, name, stock, purchase, selling):
        self.pid = pid
        self.name = name
        self.stock = stock
        self.purchase = purchase
        self.selling = selling

    def __add__(self, other):
        if not isinstance(other, Product) or self.pid != other.pid:
            return NotImplemented
        return Product(
            self.pid,
            self.name,
            self.stock + other.stock,
            min(self.purchase, other.purchase),
            max(self.selling, other.selling),
        )

    def value(self):
        return self.stock * self.purchase

    def copy(self):
        return Product(self.pid, self.name, self.stock, self.purchase, self.selling)

    def __str__(self):
        return f"{self.pid} {self.name} stock={self.stock} purchase={self.purchase} selling={self.selling}"


@total_ordering
class Inventory:
    def __init__(self):
        self.items = {}
        self._total = 0

    def add_product(self, p):
        if p.pid in self.items:
            return False
        self.items[p.pid] = p
        self._total += p.value()
        return True

    def delete_product(self, pid):
        p = self.items.pop(pid, None)
        if p is None:
            return False
        self._total -= p.value()
        return True

    def update_stock(self, pid, stock):
        p = self.items.get(pid)
        if p is None:
            return False
        self._total += (stock - p.stock) * p.purchase
        p.stock = stock
        return True

    def total_value(self):
        return self._total

    def __len__(self):
        return len(self.items)

    def __contains__(self, pid):
        return pid in self.items

    def __iter__(self):
        for pid in sorted(self.items):
            yield self.items[pid]

    def __add__(self, other):
        if not isinstance(other, Inventory):
            return NotImplemented
        merged = Inventory()
        for p in self.items.values():
            merged.add_product(p.copy())
        for p in other.items.values():
            if p.pid in merged.items:
                old = merged.items[p.pid]
                merged.delete_product(p.pid)
                merged.add_product(old + p)
            else:
                merged.add_product(p.copy())
        return merged

    def __eq__(self, other):
        if not isinstance(other, Inventory):
            return NotImplemented
        return self._total == other._total

    def __lt__(self, other):
        if not isinstance(other, Inventory):
            return NotImplemented
        return self._total < other._total


def load_inventory(path):
    inv = Inventory()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 5:
                continue
            try:
                p = Product(parts[0], parts[1], to_num(parts[2]), to_num(parts[3]), to_num(parts[4]))
            except ValueError:
                continue
            inv.add_product(p)
    return inv


def print_summary(inv):
    for p in inv:
        print(p)
    print("TOTAL_VALUATION =", inv.total_value())


def main():
    path_a = sys.stdin.readline().strip()
    path_b = sys.stdin.readline().strip()
    try:
        q = int(sys.stdin.readline())
        invs = {"A": load_inventory(path_a), "B": load_inventory(path_b)}
    except (ValueError, OSError) as e:
        print("Error:", e)
        sys.exit(1)

    for _ in range(q):
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.split()
        if not parts:
            continue
        cmd = parts[0].upper()
        try:
            if cmd == "ADD" and len(parts) == 7 and parts[1] in invs:
                p = Product(parts[2], parts[3], to_num(parts[4]), to_num(parts[5]), to_num(parts[6]))
                print("ADD OK" if invs[parts[1]].add_product(p) else "ADD FAILED: product exists")
            elif cmd == "DELETE" and len(parts) == 3 and parts[1] in invs:
                print("DELETE OK" if invs[parts[1]].delete_product(parts[2]) else "DELETE FAILED: not found")
            elif cmd == "UPDATE" and len(parts) == 4 and parts[1] in invs:
                ok = invs[parts[1]].update_stock(parts[2], to_num(parts[3]))
                print("UPDATE OK" if ok else "UPDATE FAILED: not found")
            elif cmd == "MERGE" and len(parts) == 1:
                print("MERGE OK")
                print_summary(invs["A"] + invs["B"])
            elif cmd == "COMPARE" and len(parts) == 1:
                a, b = invs["A"], invs["B"]
                sign = ">" if a > b else "<" if a < b else "=="
                print(f"COMPARE A {sign} B (A={a.total_value()}, B={b.total_value()})")
            else:
                print("INVALID OPERATION")
        except ValueError:
            print("INVALID NUMBER")


if __name__ == "__main__":
    main()
