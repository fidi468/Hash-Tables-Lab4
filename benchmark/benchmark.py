"""Empirik ölçmələr (Lalə). İşlətmək (kökdən): python3 benchmark/benchmark.py
Nəticələr results/*.csv fayllarına və konsola yazılır."""
import csv
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from book import Book
from data_generator import generate_ips, generate_isbns
from math_utils import next_prime
from open_addressing_hash import LINEAR, QUADRATIC, OpenAddressingHash
from separate_chaining_hash import SeparateChainingHash

N_ELEMENTS, TABLE_SIZE = 5000, 10007
LAMBDAS = [0.25, 0.50, 0.75, 0.90]

os.makedirs("results", exist_ok=True)
data = {"ISBN": generate_isbns(N_ELEMENTS, 42), "IP": generate_ips(N_ELEMENTS, 42)}


def chain(n, a, keys):
    t = SeparateChainingHash(n, SeparateChainingHash.MOD, a, False)
    for k in keys:
        t.insert(Book(k))
    return t


def open_tbl(n, probe, a, keys):
    t = OpenAddressingHash(n, probe, a, False)
    placed = [k for k in keys if t.insert(k)]
    return t, placed


# ---------- 1) Kolliziyalar: a=1 vs a=37 ----------
print(f"\n== 1) Kolliziya sayı (N={TABLE_SIZE}, {N_ELEMENTS} element) ==")
with open("results/collisions.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["dataset", "a", "structure", "collisions", "failed_inserts"])
    for ds, keys in data.items():
        for a in (1, 37):
            rows = [("Chaining", chain(TABLE_SIZE, a, keys).count_collisions(), 0)]
            for p in (LINEAR, QUADRATIC):
                t, placed = open_tbl(TABLE_SIZE, p, a, keys)
                rows.append((p, t.collisions, len(keys) - len(placed)))
            for st, col, fail in rows:
                w.writerow([ds, a, st, col, fail])
                print(f"{ds:5s} a={a:<2d} {st:10s} kolliziya={col:<6d} uğursuz insert={fail}")

# ---------- 2) Maksimum klaster / zəncir (a=37, N=10007) ----------
print(f"\n== 2) Maksimum zəncir/klaster uzunluğu (a=37, N={TABLE_SIZE}) ==")
with open("results/max_cluster.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["dataset", "structure", "max_length"])
    for ds, keys in data.items():
        res = [("Chaining", chain(TABLE_SIZE, 37, keys).max_chain_length())]
        for p in (LINEAR, QUADRATIC):
            res.append((p, open_tbl(TABLE_SIZE, p, 37, keys)[0].max_cluster_length()))
        for st, m in res:
            w.writerow([ds, st, m]); print(f"{ds:5s} {st:10s} max={m}")

# ---------- 3) Orta probe sayı vs lambda ----------
# 5000 element sabit; N = nextPrime(5000/lambda) ki, lambda hədəf nöqtəyə düşsün.
print("\n== 3) Orta probe sayı (a=37) ==")
with open("results/avg_probes.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dataset", "target_lambda", "table_size", "actual_lambda", "structure",
                "avg_successful", "avg_unsuccessful", "failed_inserts"])
    for ds, keys in data.items():
        inset = set(keys)
        pool = generate_isbns(8000, 99) if ds == "ISBN" else generate_ips(8000, 99)
        absent = [s for s in pool if s not in inset][:2000]
        for lam in LAMBDAS:
            n = next_prime(math.ceil(N_ELEMENTS / lam))
            actual = N_ELEMENTS / n
            ch = chain(n, 37, keys)
            results = [("Chaining",
                        sum(ch.search_probes(k) for k in keys) / len(keys),
                        sum(ch.search_probes(k) for k in absent) / len(absent), 0)]
            for p in (LINEAR, QUADRATIC):
                t, placed = open_tbl(n, p, 37, keys)
                results.append((p,
                                sum(t.search_probes(k) for k in placed) / len(placed),
                                sum(t.search_probes(k) for k in absent) / len(absent),
                                len(keys) - len(placed)))
            for st, s, u, fail in results:
                w.writerow([ds, f"{lam:.2f}", n, f"{actual:.4f}", st, f"{s:.3f}", f"{u:.3f}", fail])
                print(f"{ds:5s} λ={lam:.2f}(N={n:<6d}) {st:10s} uğurlu={s:.3f} uğursuz={u:.3f} çatışmayan={fail}")

print("\nCSV faylları results/ qovluğunda.")
