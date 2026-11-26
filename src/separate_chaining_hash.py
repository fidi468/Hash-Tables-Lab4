"""Tapşırıq 1: Separate Chaining (Fidan) + dinamik böyümə/kiçilmə (Fidan M.).
Sıxışdırma: sadə modul (k mod N) və ya MAD: ((a*(k mod p) + b) mod p) mod N.
"""
import random

from book import Book
from math_utils import HASH_MOD, DEFAULT_A, next_prime, poly_hash

P = HASH_MOD            # MAD üçün sadə p (2^31 - 1)
MIN_CAPACITY = 11
GROW_LAMBDA = 1.0       # lambda >= 1.0 -> böyüt
SHRINK_LAMBDA = 0.25    # lambda < 0.25 -> kiçilt


class _Node:
    __slots__ = ("book", "next")

    def __init__(self, book, nxt):
        self.book = book
        self.next = nxt


class SeparateChainingHash:
    MOD = "MOD"
    MAD = "MAD"

    def __init__(self, capacity=MIN_CAPACITY, compression="MAD", poly_a=DEFAULT_A, dynamic_resize=True):
        self._table = [None] * next_prime(max(capacity, MIN_CAPACITY))
        self._size = 0
        self.resize_count = 0
        self.compression = compression
        self.poly_a = poly_a
        self.dynamic_resize = dynamic_resize
        rnd = random.Random(42)                       # təkrarlana bilən a, b
        self._mad_a = rnd.randrange(1, P)             # a in [1, p-1]
        self._mad_b = rnd.randrange(0, P)             # b in [0, p-1]

    # ---------- hash + sıxışdırma ----------
    def _index(self, key, cap):
        k = poly_hash(key, self.poly_a)
        if self.compression == self.MOD:
            return k % cap
        return ((self._mad_a * (k % P) + self._mad_b) % P) % cap

    @staticmethod
    def _check(key):
        if key is None:
            raise ValueError("ISBN None ola bilməz")

    # ---------- əsas əməliyyatlar ----------
    def insert(self, book: Book) -> bool:
        """Əlavə edir. Eyni ISBN varsa əlavə etmir və False qaytarır."""
        if book is None:
            raise ValueError("book None ola bilməz")
        self._check(book.isbn)
        idx = self._index(book.isbn, len(self._table))
        n = self._table[idx]
        while n:
            if n.book.isbn == book.isbn:
                return False
            n = n.next
        self._table[idx] = _Node(book, self._table[idx])   # zəncirin başına
        self._size += 1
        if self.dynamic_resize and self.load_factor() >= GROW_LAMBDA:
            self._resize(next_prime(2 * len(self._table)))
        return True

    def remove(self, isbn: str) -> bool:
        """Silir. Tapılmasa False."""
        self._check(isbn)
        idx = self._index(isbn, len(self._table))
        prev, n = None, self._table[idx]
        while n:
            if n.book.isbn == isbn:
                if prev is None:
                    self._table[idx] = n.next
                else:
                    prev.next = n.next
                self._size -= 1
                if self.dynamic_resize:
                    while self.load_factor() < SHRINK_LAMBDA and len(self._table) > MIN_CAPACITY:
                        self._resize(max(MIN_CAPACITY, next_prime(len(self._table) // 2)))
                return True
            prev, n = n, n.next
        return False

    def find_by_isbn(self, isbn: str):
        """ISBN ilə axtarır; tapılmasa None."""
        self._check(isbn)
        n = self._table[self._index(isbn, len(self._table))]
        while n:
            if n.book.isbn == isbn:
                return n.book
            n = n.next
        return None

    findByISBN = find_by_isbn   # təlimatdakı ad

    def _resize(self, new_cap):
        """Bütün elementləri yeni ölçülü cədvələ yenidən həşləyir."""
        old = self._table
        self._table = [None] * new_cap
        for head in old:
            n = head
            while n:
                nxt = n.next
                idx = self._index(n.book.isbn, new_cap)
                n.next = self._table[idx]
                self._table[idx] = n
                n = nxt
        self.resize_count += 1

    # ---------- statistika ----------
    def size(self): return self._size
    def capacity(self): return len(self._table)
    def load_factor(self): return self._size / len(self._table)

    def max_chain_length(self):
        best = 0
        for head in self._table:
            ln, n = 0, head
            while n:
                ln += 1
                n = n.next
            best = max(best, ln)
        return best

    def count_collisions(self):
        """Kolliziya sayı = element sayı - dolu bucket sayı."""
        return self._size - sum(1 for h in self._table if h is not None)

    def search_probes(self, isbn):
        """Axtarışda yoxlanan node sayı (tapılarsa mövqe, tapılmazsa zəncir uzunluğu)."""
        count, n = 0, self._table[self._index(isbn, len(self._table))]
        while n:
            count += 1
            if n.book.isbn == isbn:
                return count
            n = n.next
        return count
