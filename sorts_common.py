"""Общие утилиты для лабораторных работ по сортировкам."""
import random
import statistics
import time


def generate_data(n, kind="random", seed=42):
    """
    Генерация тестовых данных.
    kind: random | sorted | reversed | nearly_sorted | duplicates
    """
    rng = random.Random(seed + n + hash(kind) % 10000)
    if kind in ("random", "R"):
        return [rng.randint(0, n * 10) for _ in range(n)]
    if kind in ("sorted", "S"):
        return list(range(n))
    if kind in ("reversed", "V"):
        return list(range(n, 0, -1))
    if kind in ("nearly_sorted", "N"):
        data = list(range(n))
        for _ in range(max(1, n // 100)):
            i, j = rng.randrange(n), rng.randrange(n)
            data[i], data[j] = data[j], data[i]
        return data
    if kind in ("duplicates", "D"):
        return [rng.randint(0, 10) for _ in range(n)]
    raise ValueError(f"Unknown kind: {kind}")


def measure(sort_func, data, repeats=3):
    """Медиана времени (с) из repeats запусков. Корректность — через sorted()."""
    times = []
    expected = sorted(data)
    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        times.append(time.perf_counter() - start)
        assert result == expected, f"{sort_func.__name__} failed correctness"
    return statistics.median(times)
