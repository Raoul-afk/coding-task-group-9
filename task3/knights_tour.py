"""Knight's Tour solver using DFS backtracking and Warnsdorff's rule.

Input format (zero-based coordinates):
    columns rows
    start_x start_y

Output: one coordinate per line, or exactly "path not found".
"""

MOVES = [
    (1, 2), (2, 1), (-1, 2), (-2, 1),
    (1, -2), (2, -1), (-1, -2), (-2, -1),
]


def cavalier(x, y, columns, rows):
    """Return the squares reachable by one legal knight's move."""
    neighbors = []
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < columns and 0 <= ny < rows:
            neighbors.append((nx, ny))
    return neighbors


def knights_tour(columns, rows, start):
    """Return a complete knight's tour starting at start, or None if none exists."""
    sx, sy = start
    if columns <= 0 or rows <= 0 or not (0 <= sx < columns and 0 <= sy < rows):
        return None

    total = columns * rows

    # Adjacency list: each chessboard square is a vertex.
    graph = {
        (x, y): cavalier(x, y, columns, rows)
        for y in range(rows)
        for x in range(columns)
    }

    # Fast necessary conditions (not sufficient) for a Hamiltonian path.
    if total > 1:
        if any(len(neighbors) == 0 for neighbors in graph.values()):
            return None

        degree_one = [square for square, neighbors in graph.items() if len(neighbors) == 1]
        if len(degree_one) > 2 or (len(degree_one) == 2 and start not in degree_one):
            return None

        # The knight alternates chessboard colors. On an odd-sized board,
        # a complete path must start on the more frequent color (even parity).
        if total % 2 == 1 and (sx + sy) % 2 != 0:
            return None

        # Every square needs to be reachable from the starting square.
        reachable = {start}
        stack = [start]
        while stack:
            square = stack.pop()
            for neighbor in graph[square]:
                if neighbor not in reachable:
                    reachable.add(neighbor)
                    stack.append(neighbor)
        if len(reachable) != total:
            return None

    path = [start]
    visited = {start}

    def dfs(square):
        if len(path) == total:
            return True

        candidates = [neighbor for neighbor in graph[square] if neighbor not in visited]

        # Warnsdorff's rule: prioritize the next square with the fewest
        # onward moves to reduce the risk of trapping ourselves later.
        candidates.sort(
            key=lambda candidate: sum(
                next_square not in visited for next_square in graph[candidate]
            )
        )

        for neighbor in candidates:
            visited.add(neighbor)
            path.append(neighbor)

            if dfs(neighbor):
                return True

            # Backtracking: undo a choice that did not lead to a full tour.
            path.pop()
            visited.remove(neighbor)

        return False

    return path if dfs(start) else None


def main():
    try:
        columns, rows = map(int, input().split())
        start_x, start_y = map(int, input().split())
    except (ValueError, EOFError):
        print("invalid input")
        return

    path = knights_tour(columns, rows, (start_x, start_y))
    if path is None:
        print("path not found")
    else:
        for x, y in path:
            print(x, y)


if __name__ == "__main__":
    main()
