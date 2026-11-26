"""Ortaq riyazi baza (Fidan). Hər iki hash cədvəli bu funksiyalardan istifadə edir."""

HASH_MOD = 2147483647   # 2^31 - 1 (Mersenn sadə ədədi)
DEFAULT_A = 37


def is_prime(n: int) -> bool:
    """n sadə ədəddirmi? Yalnız tək bölənlər sqrt(n)-ə qədər yoxlanır."""
    if n < 2:
        return False
    if n < 4:
        return True            # 2 və 3
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def next_prime(n: int) -> int:
    """n-dən böyük və ya n-ə bərabər ən yaxın sadə ədəd."""
    if n <= 2:
        return 2
    c = n + 1 if n % 2 == 0 else n
    while not is_prime(c):
        c += 2
    return c


def poly_hash(s: str, a: int = DEFAULT_A) -> int:
    """
    Polinom həş (Horner qaydası): h = (...((c0*a + c1)*a + c2)*a ...) + c(n-1).
    Hər addımda HASH_MOD-a görə mod alınır; nəticə [0, HASH_MOD) aralığındadır.
    """
    h = 0
    for ch in s:
        h = (h * a + ord(ch)) % HASH_MOD
    return h
