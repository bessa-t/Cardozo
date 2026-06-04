import unittest


class ImportTests(unittest.TestCase):
    def test_cardozo_package_imports(self):
        import cardozo

        self.assertIsNotNone(cardozo)


if __name__ == "__main__":
    unittest.main()
