"""Test datası generatoru (Lalə). Sabit seed ilə hər dəfə eyni nəticə verir.
İşlətmək (layihənin kökündən):  python3 src/data_generator.py
"""
import os
import random

SEED = 42


def generate_isbns(count: int, seed: int = SEED) -> list:
    """Düzgün ISBN-13: 978 + 9 təsadüfi rəqəm + yoxlama rəqəmi. Unikallıq set ilə təmin olunur."""
    rnd = random.Random(seed)
    seen, out = set(), []
    while len(out) < count:
        digits = [9, 7, 8] + [rnd.randrange(10) for _ in range(9)]
        total = sum(d if i % 2 == 0 else 3 * d for i, d in enumerate(digits))
        digits.append((10 - total % 10) % 10)
        s = "".join(map(str, digits))
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def generate_ips(count: int, seed: int = SEED) -> list:
    """Unikal IPv4 ünvanları (hər oktet 1..254)."""
    rnd = random.Random(seed)
    seen, out = set(), []
    while len(out) < count:
        s = ".".join(str(rnd.randint(1, 254)) for _ in range(4))
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _write(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    _write("data/isbn.txt", generate_isbns(5000))
    _write("data/ip.txt", generate_ips(5000))
    print(f"data/isbn.txt və data/ip.txt yaradıldı (5000 sətir, seed={SEED})")
