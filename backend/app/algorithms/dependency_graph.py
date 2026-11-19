def prerequisite_order(graph: dict[int, list[int]], target: int) -> list[int]:
    order: list[int] = []
    finished: set[int] = set()
    on_path: set[int] = set()
    stack = [(target, False)]

    while stack:
        movie, prerequisites_handled = stack.pop()
        if prerequisites_handled:
            on_path.remove(movie)
            finished.add(movie)
            if movie != target:
                order.append(movie)
        elif movie not in finished:
            on_path.add(movie)
            stack.append((movie, True))
            for prerequisite in reversed(graph.get(movie, [])):
                if prerequisite in on_path:
                    raise ValueError("Circular movie dependency")
                if prerequisite not in finished:
                    stack.append((prerequisite, False))
    return order
