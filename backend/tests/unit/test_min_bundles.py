from itertools import combinations, combinations_with_replacement

import pytest

from app.algorithms.min_bundles import minimum_bundles


@pytest.mark.parametrize(("sizes", "group_size", "expected"), [
    ([1, 3, 4], 6, {3: 2}),
    ([2, 5], 11, {5: 1, 2: 3}),
    ([6, 9, 20], 44, {20: 1, 9: 2, 6: 1}),
    ([4, 6], 7, None),
    ([2, 3, 4], 6, {4: 1, 2: 1}),
    ([1], 10_000, {1: 10_000}),
])
def test_quote_examples_and_edges(sizes, group_size, expected):
    assert minimum_bundles(sizes, group_size) == expected


def test_matches_exhaustive_search_for_small_groups():
    for size_count in range(1, 4):
        for sizes in combinations(range(1, 6), size_count):
            for seats in range(1, 11):
                expected_count = next((
                    count for count in range(1, seats + 1)
                    if any(sum(choice) == seats
                           for choice in combinations_with_replacement(sizes, count))
                ), None)
                quote = minimum_bundles(list(sizes), seats)
                if expected_count is None:
                    assert quote is None
                else:
                    assert quote is not None
                    assert quote.keys() <= set(sizes)
                    assert sum(quote.values()) == expected_count
                    assert sum(size * quantity for size, quantity in quote.items()) == seats
