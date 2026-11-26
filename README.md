# Hash-Tables-Lab4

# Hash Cədvəlləri Layihəsi (Python 3)

Heç bir xarici kitabxana lazım deyil (yalnız qrafiklər üçün `pandas` və `matplotlib`).

```
src/        math_utils.py, book.py, data_generator.py, separate_chaining_hash.py, open_addressing_hash.py
tests/      test_all.py
benchmark/  benchmark.py, plot.py
data/       isbn.txt, ip.txt (seed=42)
results/    *.csv, *.png
```

Layihənin kök qovluğundan işlədin:

```
python3 src/data_generator.py                      # data/ faylları (Lalə)
python3 -m unittest discover -s tests -v           # testlər (Fidan M.)
python3 benchmark/benchmark.py                     # ölçmələr -> results/*.csv (Lalə)
python3 benchmark/plot.py                          # qrafiklər -> results/*.png (Lalə)
```

| Fayl | Müəllif |
|---|---|
| repo strukturu, skeletlər, tests/test_all.py, resize məntiqi | Fidan M. |
| math_utils.py, book.py, separate_chaining_hash.py (əsas hissə) | Fidan |
| open_addressing_hash.py | Fatimə |
| data_generator.py, benchmark/ | Lalə |
