"""Tapşırıq 2: Open Addressing (Fatimə). Firewall üçün IP açarları (str).
Linear və Quadratic probing, Lazy Deletion (DELETED), lambda > 0.5 olduqda təmizləyici rehash.
"""
from math_utils import DEFAULT_A, next_prime, poly_hash

EMPTY, ACTIVE, DELETED = "EMPTY", "ACTIVE", "DELETED"
LINEAR, QUADRATIC = "LINEAR", "QUADRATIC"
MIN_CAPACITY = 11


def probe_index(h0: int, i: int, probe: str, n: int) -> int:
    """Test üçün: i-ci probe indeksi. LINEAR: H_i=(H_{i-1}+1) mod N;
    QUADRATIC: H_i=(H_{i-1}+2i-1) mod N."""
    h = h0
    for j in range(1, i + 1):
        h = (h + 1) % n if probe == LINEAR else (h + 2 * j - 1) % n
    return h


class OpenAddressingHash:
    def __init__(self, capacity=MIN_CAPACITY, probe=LINEAR, poly_a=DEFAULT_A, auto_rehash=True):
        self.probe = probe
        self.poly_a = poly_a
        self.auto_rehash = auto_rehash
        self.rehash_count = 0
        self.collisions = 0          # ilk xanası dolu olduğu üçün əlavə probe tələb edən insertlər
        self._last_probes = 0
        self._allocate(next_prime(max(capacity, MIN_CAPACITY)))

    def _allocate(self, n):
        self._keys = [None] * n
        self._status = [EMPTY] * n
        self._active = 0
        self._deleted = 0

    def _home(self, key):
        return poly_hash(key, self.poly_a) % len(self._keys)

    def _next(self, h, i):
        n = len(self._keys)
        return (h + 1) % n if self.probe == LINEAR else (h + 2 * i - 1) % n

    @staticmethod
    def _check(key):
        if key is None:
            raise ValueError("açar None ola bilməz")

    def _locate(self, key):
        """Açarın indeksi (yoxdursa -1). EMPTY-də dayanır, DELETED-dən keçir."""
        h = self._home(key)
        self._last_probes = 0
        for i in range(len(self._keys)):
            if i > 0:
                h = self._next(h, i)
            self._last_probes += 1
            if self._status[h] == EMPTY:
                return -1
            if self._status[h] == ACTIVE and self._keys[h] == key:
                return h
        return -1

    def _place(self, key):
        """Qoyulan yerin probe sayı; yer tapılmasa 0."""
        h = self._home(key)
        for i in range(len(self._keys)):
            if i > 0:
                h = self._next(h, i)
            if self._status[h] != ACTIVE:
                if self._status[h] == DELETED:
                    self._deleted -= 1          # tombstone təkrar istifadə olunur
                self._keys[h] = key
                self._status[h] = ACTIVE
                self._active += 1
                return i + 1
        return 0

    # ---------- əsas əməliyyatlar ----------
    def insert(self, key: str) -> bool:
        self._check(key)
        if self._locate(key) >= 0:
            return False                          # təkrar
        probes = self._place(key)
        if probes == 0:                           # yer tapılmadı (məs. quadratic dövrü)
            if not self.auto_rehash:
                return False
            self._rebuild(next_prime(2 * len(self._keys)))
            probes = self._place(key)
            if probes == 0:
                return False
        if probes > 1:
            self.collisions += 1
        if self.auto_rehash and (self._active + self._deleted) > 0.5 * len(self._keys):
            self._rehash()
        return True

    def search(self, key: str) -> bool:
        self._check(key)
        return self._locate(key) >= 0

    def delete(self, key: str) -> bool:
        """Lazy deletion: xana DELETED kimi işarələnir, zəncir qırılmır."""
        self._check(key)
        idx = self._locate(key)
        if idx < 0:
            return False
        self._status[idx] = DELETED
        self._keys[idx] = None
        self._active -= 1
        self._deleted += 1
        return True

    def _rehash(self):
        """Təmizləyici rehash: DELETED-lər atılır. Aktiv lambda > 0.5 isə ölçü də artırılır."""
        n = len(self._keys)
        self._rebuild(next_prime(2 * n) if self._active / n > 0.5 else n)

    def _rebuild(self, new_n):
        old_keys, old_status = self._keys, self._status
        self._allocate(new_n)
        for k, s in zip(old_keys, old_status):
            if s == ACTIVE:
                self._place(k)
        self.rehash_count += 1

    # ---------- statistika ----------
    def size(self): return self._active
    def deleted_count(self): return self._deleted
    def capacity(self): return len(self._keys)
    def load_factor(self): return self._active / len(self._keys)

    def search_probes(self, key):
        """Axtarışda yoxlanan xana sayı (tapılıb-tapılmamasından asılı olmayaraq)."""
        self._locate(key)
        return self._last_probes

    def max_cluster_length(self):
        """Ən uzun ardıcıl dolu (EMPTY olmayan) xanalar zənciri (klaster)."""
        best = cur = 0
        for s in self._status:
            cur = cur + 1 if s != EMPTY else 0
            best = max(best, cur)
        return best
