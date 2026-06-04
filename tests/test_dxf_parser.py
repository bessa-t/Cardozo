from pathlib import Path
import unittest

from cardozo.backend.dxf_parser import DXFParser


class DXFParserTests(unittest.TestCase):
    def test_example_dxf_can_be_parsed(self):
        dxf_path = Path("examples/dxf_files/section_7.dxf")

        parsed = DXFParser(str(dxf_path)).parse()

        self.assertTrue(parsed.concrete_polygons)
        self.assertTrue(parsed.steel_bars)


if __name__ == "__main__":
    unittest.main()
