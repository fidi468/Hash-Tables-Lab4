"""Lalə: results/*.csv -> results/*.png (Bölmə 3 üçün xətti qrafiklər). İşlətmək: python3 benchmark/plot.py"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("results/avg_probes.csv")
style = {"Chaining": ("#1565C0", "o"), "LINEAR": ("#D84315", "s"), "QUADRATIC": ("#2E7D32", "^")}
for metric, title, fname in [("avg_successful", "Uğurlu axtarış: orta probe sayı", "probes_successful.png"),
                             ("avg_unsuccessful", "Uğursuz axtarış: orta probe sayı", "probes_unsuccessful.png")]:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, ds in zip(axes, ["ISBN", "IP"]):
        for st, (col, mk) in style.items():
            d = df[(df.dataset == ds) & (df.structure == st)]
            ax.plot(d.actual_lambda, d[metric], color=col, marker=mk, label=st)
        ax.set_title(ds); ax.set_xlabel("λ (yük əmsalı)"); ax.grid(alpha=.3)
    axes[0].set_ylabel("orta probe sayı"); axes[0].legend()
    fig.suptitle(title); fig.tight_layout(); fig.savefig("results/" + fname, dpi=150); plt.close(fig)

c = pd.read_csv("results/collisions.csv")
fig, ax = plt.subplots(figsize=(7, 4))
for i, (st, (col, mk)) in enumerate(style.items()):
    for j, a in enumerate([1, 37]):
        v = c[(c.structure == st) & (c.a == a)].collisions.mean()
        ax.bar(j + i * 0.27, v, 0.25, color=col, alpha=1 if a == 37 else .55, label=st if j == 0 else None)
ax.set_xticks([0.27, 1.27]); ax.set_xticklabels(["a = 1", "a = 37"]); ax.set_ylabel("kolliziya sayı (ISBN/IP ortalaması)")
ax.legend(); ax.set_title("a=1 və a=37 üçün kolliziyalar (N=10007)"); fig.tight_layout()
fig.savefig("results/collisions.png", dpi=150)
