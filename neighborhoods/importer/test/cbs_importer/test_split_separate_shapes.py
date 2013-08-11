import unittest
from neighborhoods.importer.cbs_importer import CBSImporter


class SplitSeparateShapes(unittest.TestCase):
    def setUp(self):
        self._cbs_importer = CBSImporter(None)

    def test_all_points_attached__returns_input(self):
        points = [[0, 2], [1, 0], [2, 2], [0, 2]]
        split_points = self._cbs_importer._split_detached_shapes(points)

        self.assertEqual(1, len(split_points))
        self.assertSequenceEqual(points, split_points[0])

    def test_two_separate_shapes__returns_points_separated(self):
        points = [
            [0, 2], [1, 0], [2, 2], [0, 2],
            [2, 0], [3, 2], [4, 0], [2, 0]
        ]
        split_points = self._cbs_importer._split_detached_shapes(points)

        self.assertEqual(2, len(split_points))
        self.assertSequenceEqual(points[0:4], split_points[0])
        self.assertSequenceEqual(points[4:8], split_points[1])
