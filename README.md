# Coding Task - Group 9

# Task 1 : Traveling Salesman Problem

////

# Task 2 : Chinese Postman Problem 

////

# Task 3 : Knight's Tour 

## Member
Rida BINDECH / 5999261011


## Problem
Given a rectangular board and a starting square, find a sequence of legal knight moves that visits **every square exactly once**. This is a Hamiltonian **path**, not necessarily a Hamiltonian cycle.

## Prerequisites
- Python 3.8 or newer
- No external libraries

## How to run
From this directory, run:

```bash
python knights_tour.py
```

Enter two lines: first `columns rows`, then `start_x start_y` (zero-based indexing):

```text
5 5
2 2
```

The program prints one `x y` coordinate per line. A complete tour has `columns * rows` lines and starts at the requested starting square.

If there is no complete tour, the output is exactly:

```text
path not found
```

An invalid or incomplete input instead produces `invalid input`. Positive dimensions and a starting coordinate within the board are required.

## Approach
1. Create a graph whose vertices are board squares `(x, y)`.
2. Add undirected edges for the eight legal knight moves, discarding out-of-bounds moves.
3. Apply quick necessary-condition checks: no isolated squares on a nontrivial board, at most two degree-one vertices (if there are two, the start must be one of them), valid start color for odd-sized boards, and graph connectivity.
4. Search using **depth-first search with backtracking**. Keep the current path and the set of visited squares. Never revisit a square.
5. Apply **Warnsdorff's rule** to order next moves: try the unvisited square with the fewest available onward moves first. This is a heuristic, not a proof that a tour exists.
6. If a choice fails, undo it and try the next one. Exhausting all choices means that no complete tour exists.

## Complexity
Let `N = columns * rows`.

- Building the graph takes `O(N)` time and `O(N)` space since each vertex has at most 8 neighbors.
- The graph checks take `O(N)` time.
- In the worst case, DFS backtracking explores exponentially many partial paths: a simple upper bound is `O(8^N)` time. Warnsdorff's rule generally reduces practical search but does not improve that worst-case guarantee.
- Graph, path, visited set, and recursion stack together use `O(N)` space.

## Sample cases

### Example 1: 5 x 5 from (2, 2)

Input:
```text
5 5
2 2
```

One valid output, interpreted as the **move order** placed on each square (rows have increasing `y`, columns increasing `x`):

```text
25 10 15  4 19
16  5 18  9 14
11 24  1 20  3
 6 17 22 13  8
23 12  7  2 21
```

The actual program outputs the coordinates in this order. The first move is `(2, 2)`, followed by `(3, 4)`, `(4, 2)`, etc.

### Example 2: 4 x 4 from (0, 0)

Input:
```text
4 4
0 0
```

Output:
```text
path not found
```

### Example 3: 1 x 1 from (0, 0)

Input:
```text
1 1
0 0
```

Output:
```text
0 0
```

## Tests
Run:
```bash
python -m unittest test_knights_tour.py
```

## AI usage disclosure
The assignment asks for honest disclosure of AI use and the prompt history. Document the assistance used to develop and test the algorithm, and attach the relevant prompt history as required by the course instructions.
