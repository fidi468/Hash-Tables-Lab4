"""Testlər və kənar hallar (Fidan M.). İşlətmək (kökdən): python3 -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from book import Book
from data_generator import generate_ips, generate_isbns
from math_utils import HASH_MOD, is_prime, next_prime, poly_hash
from open_addressing_hash import LINEAR, QUADRATIC, OpenAddressingHash, probe_index
from separate_chaining_hash import SeparateChainingHash


def b(isbn):
    return Book(isbn, "t" + isbn, "a")


class TestMath(unittest.TestCase):
    def test_is_prime(self):
        self.assertFalse(is_prime(0) or is_prime(1) or is_prime(4) or is_prime(10001))  # 10001 = 73*137
        self.assertTrue(is_prime(2) and is_prime(3) and is_prime(10007))

    def test_next_prime(self):
        self.assertEqual(next_prime(10000), 10007)
        self.assertEqual(next_prime(10007), 10007)
        self.assertEqual((next_prime(14), next_prime(-5)), (17, 2))

    def test_horner(self):
        self.assertEqual(poly_hash("ab", 37), 97 * 37 + 98)
        self.assertEqual((poly_hash("ab", 1), poly_hash("ba", 1)), (195, 195))   # a=1 -> simvol cəmi
        self.assertEqual(poly_hash("", 37), 0)
        self.assertTrue(0 <= poly_hash("978123456789123456789" * 5, 37) < HASH_MOD)


class TestData(unittest.TestCase):
    def test_seed_and_uniqueness(self):
        a = generate_isbns(5000, 42)
        self.assertEqual(a, generate_isbns(5000, 42))
        self.assertEqual(len(set(a)), 5000)
        self.assertEqual(len(a[0]), 13)
        self.assertEqual(len(set(generate_ips(5000, 42))), 5000)


class TestChaining(unittest.TestCase):
    def run_for(self, comp):
        t = SeparateChainingHash(11, comp, 37, True)
        self.assertIsNone(t.find_by_isbn("x"))
        self.assertFalse(t.remove("x"))
        self.assertEqual(t.size(), 0)
        self.assertTrue(t.insert(b("111")))
        self.assertFalse(t.insert(b("111")))                  # təkrar
        self.assertEqual(t.size(), 1)
        self.assertEqual(t.findByISBN("111").title, "t111")
        self.assertTrue(t.remove("111"))
        self.assertIsNone(t.find_by_isbn("111"))
        self.assertFalse(t.remove("111"))

        for i in range(1000):                                  # böyümə
            t.insert(b(f"isbn{i}"))
        self.assertEqual(t.size(), 1000)
        self.assertLess(t.load_factor(), 1.0)
        self.assertGreater(t.capacity(), 11)
        self.assertGreater(t.resize_count, 0)
        self.assertTrue(all(t.find_by_isbn(f"isbn{i}") for i in range(1000)))

        big = t.capacity()                                     # kiçilmə
        for i in range(990):
            t.remove(f"isbn{i}")
        self.assertEqual(t.size(), 10)
        self.assertLess(t.capacity(), big)
        self.assertTrue(t.load_factor() >= 0.25 or t.capacity() == 11)
        self.assertTrue(all(t.find_by_isbn(f"isbn{i}") for i in range(990, 1000)))
        for i in range(990, 1000):
            t.remove(f"isbn{i}")
        self.assertEqual((t.size(), t.capacity()), (0, 11))    # min ölçü

        with self.assertRaises(ValueError):
            t.insert(None)
        with self.assertRaises(ValueError):
            t.find_by_isbn(None)

        f = SeparateChainingHash(11, comp, 37, False)          # resize söndürülüb
        for i in range(100):
            f.insert(b(f"k{i}"))
        self.assertEqual((f.capacity(), f.size(), f.resize_count), (11, 100, 0))

        c = SeparateChainingHash(11, comp, 1, False)           # a=1: "ab","ba" toqquşur
        c.insert(b("ab")); c.insert(b("ba"))
        self.assertTrue(c.find_by_isbn("ab") and c.find_by_isbn("ba"))
        self.assertTrue(c.remove("ab"))
        self.assertIsNotNone(c.find_by_isbn("ba"))             # zəncirdən silmə digərinə toxunmur

    def test_mod(self): self.run_for(SeparateChainingHash.MOD)
    def test_mad(self): self.run_for(SeparateChainingHash.MAD)


class TestOpenAddressing(unittest.TestCase):
    def run_for(self, p):
        t = OpenAddressingHash(11, p, 37, True)
        self.assertFalse(t.search("1.1.1.1") or t.delete("1.1.1.1"))
        self.assertTrue(t.insert("1.1.1.1") and t.search("1.1.1.1"))
        self.assertFalse(t.insert("1.1.1.1"))
        self.assertEqual(t.size(), 1)
        self.assertTrue(t.delete("1.1.1.1"))
        self.assertFalse(t.search("1.1.1.1"))
        self.assertFalse(t.delete("1.1.1.1"))

        # Lazy deletion: a=1 -> "ab" və "ba" eyni home xanaya düşür
        l = OpenAddressingHash(101, p, 1, False)
        l.insert("ab"); l.insert("ba")
        self.assertTrue(l.delete("ab"))
        self.assertTrue(l.search("ba"))                        # DELETED zənciri qırmır
        self.assertEqual(l.deleted_count(), 1)
        self.assertGreaterEqual(l.search_probes("ba"), 2)      # DELETED xanadan keçir
        l.insert("ab")                                         # tombstone təkrar istifadə
        self.assertEqual(l.deleted_count(), 0)
        self.assertTrue(l.search("ab") and l.search("ba"))

        # avtomatik rehash (lambda > 0.5)
        r = OpenAddressingHash(11, p, 37, True)
        ips = generate_ips(500, 7)
        for ip in ips:
            r.insert(ip)
        self.assertEqual(r.size(), 500)
        self.assertGreater(r.rehash_count, 0)
        self.assertGreater(r.capacity(), 11)
        self.assertLessEqual(r.size() / r.capacity(), 0.5 + 1e-9)
        self.assertTrue(all(r.search(ip) for ip in ips))

        # silmələr + rehash: DELETED-lər təmizlənir
        d = OpenAddressingHash(101, p, 37, True)
        few = generate_ips(60, 9)
        for ip in few[:40]: d.insert(ip)
        for ip in few[:30]: d.delete(ip)
        self.assertEqual(d.deleted_count(), 30)
        for ip in few[40:]: d.insert(ip)                       # active+deleted > 0.5N -> rehash
        self.assertEqual(d.deleted_count(), 0)
        self.assertTrue(all(d.search(ip) for ip in few[30:]))
        self.assertFalse(any(d.search(ip) for ip in few[:30]))

        # sadə N və lambda <= 0.5 -> hər insert uğurlu (a=1: pis həş, çox toqquşma)
        q = OpenAddressingHash(1009, p, 1, False)
        self.assertTrue(all(q.insert(k) for k in generate_isbns(504, 3)))

        with self.assertRaises(ValueError):
            t.insert(None)

    def test_linear(self): self.run_for(LINEAR)
    def test_quadratic(self): self.run_for(QUADRATIC)

    def test_probe_formula(self):
        n, h0 = 11, 3
        self.assertEqual([probe_index(h0, i, LINEAR, n) for i in range(4)], [3, 4, 5, 6])
        for i in range(8):                                     # H_i = H_{i-1}+2i-1  =>  h0 + i^2
            self.assertEqual(probe_index(h0, i, QUADRATIC, n), (h0 + i * i) % n)


if __name__ == "__main__":
    unittest.main()
