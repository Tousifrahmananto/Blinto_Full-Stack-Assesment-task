def minimum_bundles(sizes: list[int], group_size: int) -> dict[int, int] | None:
    sizes = sorted(sizes, reverse=True)  
    fewest = [0] + [float("inf")] * group_size  
    last_size = [0] * (group_size + 1)  

    for seats in range(1, group_size + 1):
        for size in sizes:
            if size <= seats and fewest[seats - size] + 1 < fewest[seats]:
                fewest[seats] = fewest[seats - size] + 1
                last_size[seats] = size

    if fewest[group_size] == float("inf"):
        return None
    quantities: dict[int, int] = {}
    seats = group_size
    while seats > 0:
        size = last_size[seats]
        quantities[size] = quantities.get(size, 0) + 1
        seats -= size
    return quantities
