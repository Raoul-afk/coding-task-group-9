"""Basic automated verification for the Knight's Tour project."""
import unittest
from knights_tour import knights_tour


def is_valid_tour(columns, rows, start, path):
    if path is None or len(path) != columns * rows:
        return False
    if path[0] != start or len(set(path)) != columns * rows:
        return False
    if not all(0 <= x < columns and 0 <= y < rows for x, y in path):
        return False
    return all(
        (abs(x2 - x1), abs(y2 - y1)) in ((1, 2), (2, 1))
        for (x1, y1), (x2, y2) in zip(path, path[1:])
    )


class KnightsTourTests(unittest.TestCase):
    def test_assignment_example(self):
        path = knights_tour(5, 5, (2, 2))
        self.assertTrue(is_valid_tour(5, 5, (2, 2), path))

    def test_standard_board(self):
        path = knights_tour(8, 8, (0, 0))
        self.assertTrue(is_valid_tour(8, 8, (0, 0), path))

    def test_rectangular_board(self):
        path = knights_tour(3, 4, (0, 0))
        self.assertTrue(is_valid_tour(3, 4, (0, 0), path))

    def test_no_solution(self):
        self.assertIsNone(knights_tour(4, 4, (0, 0)))

    def test_wrong_start_color(self):
        self.assertIsNone(knights_tour(5, 5, (1, 2)))

    def test_one_square(self):
        self.assertEqual(knights_tour(1, 1, (0, 0)), [(0, 0)])

    def test_out_of_bounds(self):
        self.assertIsNone(knights_tour(5, 5, (7, 7)))


if __name__ == "__main__":
    unittest.main()
