import unittest

from cardozo.backend.geometry_builder import GeometryBuilder


class GeometryBuilderTests(unittest.TestCase):
    def test_geometry_builder_can_be_created(self):
        self.assertIsNotNone(GeometryBuilder())


if __name__ == "__main__":
    unittest.main()
