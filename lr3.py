"""
Лабораторная работа № 3. Вариант 17.
Быстрая сортировка: опорный — случайный, разбиение Ломуто.
Сортировка слиянием: восходящая (bottom-up).
Дополнительное задание: Г5 — устойчивость на записях (регион, выручка).
"""
from __future__ import annotations

import random
import sys

from sorts_common import generate_data, measure
from lr2 import bubble_sort, insertion_sort

# Увеличиваем лимит на случай глубокой рекурсии (для Lomuto + random обычно не нужно)
sys.setrecursionlimit(max(sys.getrecursionlimit(), 5000))


# ---------- Быстрая сортировка (Ломуто, случайный опорный) ----------
def quick_sort(arr):
    a = arr.copy()
    _quick_sort(a, 0, len(a) - 1)
    return a


def _quick_sort(a, lo, hi):
    """Рекурсия в меньшую часть — глубина стека O(log n)."""
    while lo < hi:
        p = _partition_lomuto(a, lo, hi)
        # p — индекс опорного после разбиения
        if p - lo < hi - p:
            _quick_sort(a, lo, p - 1)
            lo = p + 1
        else:
            _quick_sort(a, p + 1, hi)
            hi = p - 1


def _partition_lomuto(a, lo, hi):
    """Схема Ломуто: случайный опорный элемент меняется с a[hi]."""
    pivot_idx = random.randint(lo, hi)
    a[pivot_idx], a[hi] = a[hi], a[pivot_idx]
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


# ---------- Восходящая сортировка слиянием (bottom-up) ----------
def merge_sort(arr):
    a = arr.copy()
    n = len(a)
    width = 1
    while width < n:
        for i in range(0, n, 2 * width):
            left = a[i : i + width]
            right = a[i + width : i + 2 * width]
            a[i : i + 2 * width] = _merge(left, right)
        width *= 2
    return a


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # «<=» — устойчивость
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------- Эксперименты ----------
def run_experiment(algorithms, sizes, kind="random", repeats=3):
    results = {name: [] for name in algorithms}
    header = f"{'n':>8}" + "".join(f"{name:>14}" for name in algorithms)
    print(header)
    for n in sizes:
        data = generate_data(n, kind=kind)
        row = f"{n:>8}"
        for name, func in algorithms.items():
            t = measure(func, data, repeats)
            results[name].append(t)
            row += f"{t:>14.4f}"
        print(row)
    return results


def demo_stability_g5():
    """
    Г5: записи (регион, выручка), сортировка по выручке.
    Проверяем, сохраняется ли порядок регионов при равной выручке.
    """
    records = [
        ("Север", 1000),
        ("Юг", 500),
        ("Восток", 1000),
        ("Запад", 750),
        ("Центр", 1000),
    ]
    print("\n=== Г5: исходные записи ===")
    for r in records:
        print(f"  {r[0]:8} — {r[1]}")

    def by_revenue_key(item):
        return item[1]

    # Merge sort — устойчивая (через ключ-обёртку)
    def merge_sort_records(arr):
        # сортируем по выручке, сохраняя исходный порядок при равенстве
        a = list(arr)
        n = len(a)
        width = 1
        while width < n:
            for i in range(0, n, 2 * width):
                left = a[i : i + width]
                right = a[i + width : i + 2 * width]
                a[i : i + 2 * width] = _merge_rec(left, right)
            width *= 2
        return a

    def _merge_rec(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i][1] <= right[j][1]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def quick_sort_records(arr):
        a = list(arr)
        _qs_rec(a, 0, len(a) - 1)
        return a

    def _qs_rec(a, lo, hi):
        while lo < hi:
            # для демонстрации неустойчивости — фиксированный опорный (последний)
            # (случайный тоже не гарантирует устойчивость)
            p = _part_rec(a, lo, hi)
            if p - lo < hi - p:
                _qs_rec(a, lo, p - 1)
                lo = p + 1
            else:
                _qs_rec(a, p + 1, hi)
                hi = p - 1

    def _part_rec(a, lo, hi):
        pivot = a[hi][1]
        i = lo
        for j in range(lo, hi):
            if a[j][1] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        return i

    merged = merge_sort_records(records)
    quicked = quick_sort_records(records)

    print("\nПосле merge_sort (по выручке):")
    for r in merged:
        print(f"  {r[0]:8} — {r[1]}")
    print("\nПосле quick_sort (по выручке):")
    for r in quicked:
        print(f"  {r[0]:8} — {r[1]}")

    # Относительный порядок записей с выручкой 1000 в исходном: Север, Восток, Центр
    orig_1000 = [r[0] for r in records if r[1] == 1000]
    merge_1000 = [r[0] for r in merged if r[1] == 1000]
    quick_1000 = [r[0] for r in quicked if r[1] == 1000]
    print(f"\nПорядок при выручке 1000 (исходный): {orig_1000}")
    print(f"Merge sort сохранил порядок: {merge_1000 == orig_1000} → {merge_1000}")
    print(f"Quick sort сохранил порядок: {quick_1000 == orig_1000} → {quick_1000}")
    return {
        "original": records,
        "merge": merged,
        "quick": quicked,
        "merge_stable": merge_1000 == orig_1000,
        "quick_stable": quick_1000 == orig_1000,
    }


if __name__ == "__main__":
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    font_path = "/usr/share/fonts/SlidesCarnival/google/Tinos/Tinos-Regular.ttf"
    font_bold = "/usr/share/fonts/SlidesCarnival/google/Tinos/Tinos-Bold.ttf"
    prop = fm.FontProperties(fname=font_path) if __import__("os").path.exists(font_path) else None
    prop_b = fm.FontProperties(fname=font_bold) if __import__("os").path.exists(font_bold) else None

    out = {}

    # Эксперимент 1: четыре алгоритма на малых размерах (из ЛР2)
    print("=== Эксперимент 1 ===")
    small = [1000, 2000, 3000, 4000, 5000]
    res1 = run_experiment(
        {
            "Пузырьком": bubble_sort,
            "Вставками": insertion_sort,
            "Быстрая": quick_sort,
            "Слиянием": merge_sort,
        },
        small,
        kind="random",
        repeats=3,
    )
    out["exp1"] = {"sizes": small, "times": res1}

    # Эксперимент 2: большие размеры (вариант 17)
    print("\n=== Эксперимент 2 ===")
    large = [30_000, 60_000, 120_000, 240_000]
    res2 = run_experiment(
        {
            "Быстрая": quick_sort,
            "Слиянием": merge_sort,
            "sorted()": sorted,
        },
        large,
        kind="random",
        repeats=3,
    )
    out["exp2"] = {"sizes": large, "times": res2}

    # Эксперимент 3: структура данных, n = 50 000
    print("\n=== Эксперимент 3, n = 50 000 ===")
    n3 = 50_000
    kinds = ["random", "sorted", "reversed", "nearly_sorted", "duplicates"]
    res3 = {}
    for kind in kinds:
        data = generate_data(n3, kind=kind)
        tq = measure(quick_sort, data, 3)
        tm = measure(merge_sort, data, 3)
        res3[kind] = {"Быстрая": tq, "Слиянием": tm}
        print(f"{kind:>15}: быстрая {tq:.4f} с, слиянием {tm:.4f} с")
    out["exp3"] = {"n": n3, "times": res3}

    # Г5
    g5 = demo_stability_g5()
    out["g5"] = {
        "merge_stable": g5["merge_stable"],
        "quick_stable": g5["quick_stable"],
        "original": g5["original"],
        "merge": g5["merge"],
        "quick": g5["quick"],
    }

    # Сохранение результатов
    with open("/home/workdir/artifacts/lr3/code/results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nРезультаты сохранены в results.json")

    # Графики
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for name, t in res1.items():
        axes[0].plot(small, t, marker="o", label=name)
    axes[0].set_yscale("log")
    axes[0].set_title("Эксперимент 1 (лог. шкала времени)", fontproperties=prop_b)
    axes[0].set_xlabel("Размер массива n", fontproperties=prop)
    axes[0].set_ylabel("Время, с", fontproperties=prop)
    axes[0].grid(True, which="both", linestyle="--", alpha=0.5)
    axes[0].legend(prop=prop, fontsize=9)

    for name, t in res2.items():
        axes[1].plot(large, t, marker="o", label=name)
    axes[1].set_title("Эксперимент 2 — O(n log n)", fontproperties=prop_b)
    axes[1].set_xlabel("Размер массива n", fontproperties=prop)
    axes[1].set_ylabel("Время, с", fontproperties=prop)
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].legend(prop=prop, fontsize=9)

    for ax in axes:
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            if prop:
                label.set_fontproperties(prop)
            label.set_fontsize(8)

    plt.tight_layout()
    plt.savefig("/home/workdir/artifacts/lr3/diagrams/exp12.png", dpi=150, bbox_inches="tight",
                facecolor="white")
    print("График exp12.png сохранён")

    # График эксперимента 3
    fig2, ax2 = plt.subplots(figsize=(8, 4.5))
    labels = list(res3.keys())
    x = range(len(labels))
    w = 0.35
    tq = [res3[k]["Быстрая"] for k in labels]
    tm = [res3[k]["Слиянием"] for k in labels]
    ax2.bar([i - w / 2 for i in x], tq, w, label="Быстрая", color="#1565c0")
    ax2.bar([i + w / 2 for i in x], tm, w, label="Слиянием", color="#c62828")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(["R", "S", "V", "N", "D"], fontproperties=prop)
    ax2.set_ylabel("Время, с", fontproperties=prop)
    ax2.set_title("Эксперимент 3 — влияние структуры данных (n = 50 000)", fontproperties=prop_b)
    ax2.legend(prop=prop)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("/home/workdir/artifacts/lr3/diagrams/exp3.png", dpi=150, bbox_inches="tight",
                facecolor="white")
    print("График exp3.png сохранён")
