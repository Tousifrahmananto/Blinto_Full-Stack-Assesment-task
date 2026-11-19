from collections import Counter


def minimum_bundles(sizes: list[int], group_size: int) -> dict[int, int] | None:
    """Return bundle quantities for an exact match, or None if impossible."""
    sizes = sorted(sizes, reverse=True)
    unreachable = group_size + 1
    counts = [0] + [unreachable] * group_size
    choices = [0] * (group_size + 1)

    for seats in range(1, group_size + 1):
        for size in sizes:
            if size <= seats and counts[seats - size] + 1 < counts[seats]:
                counts[seats] = counts[seats - size] + 1
                choices[seats] = size

    if counts[group_size] == unreachable:
        return None

    bundles: Counter[int] = Counter()
    while group_size:
        size = choices[group_size]
        bundles[size] += 1
        group_size -= size
    return dict(bundles)
