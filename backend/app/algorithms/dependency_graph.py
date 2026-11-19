def prerequisite_order(graph: dict[int, list[int]], target: int) -> list[int]:
    """Return each prerequisite in postorder, or raise ValueError for a cycle."""
    active = {target}
    completed = set()
    order = []
    stack = [(target, iter(graph.get(target, [])))]
    while stack:
        movie_id, prerequisites = stack[-1]
        prerequisite = next(prerequisites, None)
        if prerequisite is None:
            stack.pop()
            active.remove(movie_id)
            completed.add(movie_id)
            if movie_id != target:
                order.append(movie_id)
        elif prerequisite in active:
            raise ValueError("Circular movie dependency")
        elif prerequisite not in completed:
            active.add(prerequisite)
            stack.append((prerequisite, iter(graph.get(prerequisite, []))))
    return order
