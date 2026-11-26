# Kodların izahı (15 dəqiqəlik görüş üçün)

Hər üzv öz hissəsini **özü başa düşməli və izah edə bilməlidir**. Aşağıda hər hissənin məntiqi,
əsas qərarlar və görüşdə ehtimal olunan suallar var. Kodu oxuyub başa düşmədən təhvil verməyin.

---

## 1. Fidan — `math_utils.py`, `book.py`, `separate_chaining_hash.py`

### `is_prime(n)`
n < 2 sadə deyil; 2 və 3 sadədir; cüt ədədlər sadə deyil. Qalanı üçün yalnız **tək** bölənlər 3-dən √n-ə qədər yoxlanır
(`i*i <= n`). Mürəkkəbliyi O(√n). Cədvəl ölçüsü üçün yoxlamalar nadir çağırılır, ona görə sürət problem deyil.

### `next_prime(n)`
n-dən kiçik olmayan ilk sadə ədəd. Cütdürsə +1 edib tək edir, sonra 2-2 artıraraq `is_prime` ilə yoxlayır.
Niyə sadə ölçü? Sadə N olduqda `k mod N` açarları daha bərabər paylayır və quadratic probing-in
yarısını (N/2-ni) tapmaq zəmanəti işləyir.

### `poly_hash(s, a)` — Horner qaydası
`h = h*a + ord(c)` hər simvol üçün. Nəticə:
h = c0·a^(n-1) + c1·a^(n-2) + … + c(n-1). Hər addımda `2^31-1`-ə görə mod alınır (böyük ədəd yığılmasın deyə).
**Niyə a=37?** a=1 olduqda həş sadəcə simvolların cəmidir ("ab" və "ba" eyni həş verir); ISBN-lər üçün cəm
dar aralıqda qalır (5000 ISBN-dən cəmi 32 fərqli həş dəyəri alınır; IP-lər üçün 241), kolliziyalar kütləvi olur. a=37 isə simvolların mövqeyini nəzərə alır.

### `Book`
Dəyişməz (`frozen`) dataclass: `isbn` (açar), `title`, `author`.

### `SeparateChainingHash`
- **Cədvəl:** `_table` — hər xana bağlı siyahının başıdır (`_Node`).
- **Sıxışdırma:**
  - `MOD`: `k % N`.
  - `MAD`: `((a·(k mod p) + b) mod p) mod N`, `p = 2^31-1` (sadə, bütün həş dəyərlərindən böyük), `a∈[1,p-1]`, `b∈[0,p-1]`
    (seed=42 ilə təyin olunur ki, nəticə təkrarlansın).
  - **Fərq:** `k mod N` N-in bölənləri ilə əlaqəli açar nümunələrində pis paylana bilər. MAD isə əvvəlcə açarı
    təsadüfi xətti çevirmədən keçirir (universal həşə yaxın), buna görə paylanma N-dən asılı qanunauyğunluqlara həssas deyil.
- **insert:** zənciri gəzib təkrar ISBN-i yoxlayır (varsa `False`), yoxdursa zəncirin **başına** qoyur (O(1)).
- **remove:** zəncirdə `prev` göstəricisi ilə node-u ayırır.
- **find_by_isbn:** zənciri gəzir; tapılmasa `None`. `findByISBN` təlimatdakı ad üçün alias-dır.
- **Statistika:** `count_collisions = element sayı − dolu bucket sayı`, `max_chain_length`, `search_probes`.

### Görüşdə ehtimal olunan suallar
- Niyə siyahının başına əlavə edirik? (O(1); sıra vacib deyil.)
- Orta axtarış mürəkkəbliyi? (O(1+λ).)
- MAD-də niyə p sadə olmalıdır? (a-nın tərsi / bərabər paylanma xassəsi üçün.)

---

## 2. Fatimə — `open_addressing_hash.py`

### Məlumat quruluşu
İki paralel massiv: `_keys` (açarlar) və `_status` (`EMPTY / ACTIVE / DELETED`). Açarlar Firewall üçün IP sətirləridir.

### Probing
- **Linear:** `H_i = (H_{i-1} + 1) mod N` (yəni `H0 + i`).
- **Quadratic:** `H_i = (H_{i-1} + 2i − 1) mod N`. Açarsa sadələşir: `H_i = H0 + i²`
  (çünki 1+3+5+…+(2i−1) = i²). Test bunu birbaşa yoxlayır.
- Quadratic üçün **sadə N və λ ≤ 0.5** olduqda yer tapılması zəmanətlidir; ona görə rehash həddi 0.5-dir.

### `_locate(key)` (axtarış)
Probe ardıcıllığı ilə gedir: **EMPTY** xanada dayanır (açar yoxdur), **DELETED** xanadan **keçir**,
**ACTIVE** və açar bərabərdirsə tapılıb. Probe sayını `_last_probes`-da saxlayır (benchmark üçün).

### Lazy Deletion
`delete` xananı boşaltmır, `DELETED` işarələyir. Əgər EMPTY etsəydik, eyni home-a düşmüş və ondan sonra yerləşmiş
açarların axtarış zənciri qırılardı və onlar "yoxdur" kimi görünərdi. `DELETED` zənciri saxlayır.
`insert` isə ilk **EMPTY və ya DELETED** xananı istifadə edir (tombstone təkrar istifadə), amma əvvəlcə açarın
mövcud olmadığını yoxlayır.

### Rehash (λ > 0.5)
`insert`-dən sonra `(active + deleted) > 0.5·N` olarsa çağırılır. DELETED xanalar da probe-ları uzatdığı üçün
say hər ikisini nəzərə alır. `_rehash`: cədvəl yenidən qurulur, bütün DELETED-lər atılır. Əgər **aktiv** λ özü də
0.5-dən böyükdürsə, ölçü `next_prime(2N)`-ə artırılır; əks halda eyni ölçüdə təmizlənir.
`auto_rehash=False` benchmark üçündür (λ=0.9-a qədər doldurmaq lazımdır).

### Görüşdə ehtimal olunan suallar
- DELETED olmasa nə baş verərdi? (zəncir qırılar.)
- Linear-də niyə "primary clustering" var, quadratic bunu necə azaldır? (Ardıcıl dolu bloklar böyüyür; quadratic addımları
  böyüdüb blokdan sıçrayır, amma "secondary clustering" qalır: eyni home → eyni ardıcıllıq.)
- Niyə quadratic üçün N sadə olmalıdır?

---

## 3. Fidan M. — resize məntiqi və testlər

### Dinamik resize (`SeparateChainingHash`)
- **Böyümə:** `insert`-dən sonra `λ ≥ 1.0` → ölçü `next_prime(2N)`.
- **Kiçilmə:** `remove`-dan sonra `λ < 0.25` və `N > 11` → ölçü `max(11, next_prime(N//2))`; `while` ilə, λ normallaşana qədər.
  Minimum ölçü 11-dir ki, cədvəl sıfıra kimi kiçilməsin.
- `_resize` bütün node-ları **yenidən həşləyir** (indeks N-dən asılıdır, ona görə köhnə indekslər etibarsızdır).
- Niyə eşiklər fərqlidir (1.0 və 0.25)? Böyütmə ilə kiçiltmə arasında boşluq olmasa "thrashing" (hər əlavə/silmədə
  ardıcıl böyümə-kiçilmə) baş verərdi. Böyüdəndən sonra λ≈0.5, kiçildəndən sonra λ≈0.5 olur.

### Testlər (`tests/test_all.py`, 9 test)
Riyaziyyat (10001 = 73·137 sadə deyil, Horner "ab" = 97·37+98), data (seed təkrarlanır, 5000 unikal), chaining (MOD və MAD):
boş cədvəl, təkrar, silmə, 1000 element → böyümə, 990 silmə → kiçilmə, min ölçü, `None` açar, `dynamic_resize=False`,
a=1 kolliziyası. Open addressing (LINEAR və QUADRATIC): DELETED zənciri, tombstone təkrar istifadəsi, avto-rehash
və DELETED-lərin təmizlənməsi, probe düsturu.

---

## 4. Lalə — `data_generator.py`, `benchmark/`

### Data
`random.Random(42)`: ISBN-13 = `978` + 9 təsadüfi rəqəm + yoxlama rəqəmi (çəkilər 1,3,1,3…). IP = 4 oktet (1–254).
Unikallıq `seen` çoxluğu ilə: təkrar çıxsa atılır və yenisi yaradılır.

### Ölçmələr (`benchmark.py`)
1. **Kolliziya (a=1 vs a=37):** N=10007, 5000 element. Chaining: element − dolu bucket. Open addressing: ilk xanası dolu olduğu üçün
   əlavə probe tələb edən insert-lərin sayı.
2. **Maksimum zəncir/klaster (a=37, N=10007):** chaining üçün ən uzun zəncir; probing üçün ən uzun ardıcıl dolu blok (dairəvi hesablanmır).
3. **Orta probe sayı:** λ ∈ {0.25, 0.50, 0.75, 0.90}. 5000 elementlə λ=0.9 üçün N=10007 kifayət etmədiyindən
   **N = next_prime(5000/λ)** seçilir (λ hədəfə düşür). Həm uğurlu, həm uğursuz axtarış (uğursuz üçün 2000 cədvəldə olmayan açar).

### Nəticələrin şərhi (hesabat üçün)
- a=1 → kolliziyalar ~4760–4980 (5000-dən), a=37 → ~1030–1230. a=1 həşi simvol cəmidir, açarlar dar aralığa yığılır.
- Chaining maksimum zəncir ≈ 5; Linear klaster 25–28; Quadratic 14–16 (quadratic primary clustering-i azaldır).
- Linear probing λ artdıqca kəskin pisləşir (λ=0.9 uğursuz axtarış ≈ 35–49 probe), quadratic ≈ 11, chaining < 1 node.
  Nəzəri düstur (linear): uğurlu ≈ ½(1+1/(1−λ)), uğursuz ≈ ½(1+1/(1−λ)²); λ=0.5-də 1.5 və 2.5, ölçmə ilə üst-üstə düşür.

### Qrafiklər
`plot.py` → `results/probes_successful.png`, `probes_unsuccessful.png`, `collisions.png`.

---

## 5. Fidan M. — Bölmə 4.2 üçün əsas fikir (λ > 0.5 olduqda Open Addressing niyə pisləşir)
Probing-də hər kolliziya növbəti xananı da tutur və **klasterlər birləşir**: dolu blok böyüdükcə yeni açarın onun
içinə düşmə ehtimalı artır (öz-özünə güclənən effekt). Uğursuz axtarış boş xana tapana qədər bütün klasteri gəzməlidir, ona
görə ≈ 1/(1−λ)² kimi böyüyür (grafiklərdəki kəskin əyri). Chaining-də isə λ>1 olsa belə yalnız həmin bucket-in zənciri
gəzilir, buna görə yük xətti artır. Bu hissəni öz sözlərinizlə, Lalənin qrafiklərinə istinad edərək yazın.

---

## Qəbul edilmiş fərziyyələr (təlimatla yoxlayın!)
- Rehash şərti `(aktiv + DELETED) / N > 0.5` kimi başa düşülüb; aktiv λ özü > 0.5 olarsa ölçü də böyüdülür.
- Chaining resize: böyümə `next_prime(2N)`, kiçilmə `next_prime(N/2)`, minimum 11.
- MAD-də `p = 2^31−1` sabitdir (N-dən asılı deyil).
- Kolliziya sayının tərifi yuxarıda yazılıb; təlimatın tərifi fərqlidirsə `count_collisions`/`collisions` dəyişdirilməlidir.
- Sİ bəyannaməsində bu kodun Claude ilə hazırlandığını dürüst göstərin.
