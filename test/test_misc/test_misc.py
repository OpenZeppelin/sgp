import unittest

from sgp.sgp_parser import parse


class TestMisc(unittest.TestCase):
    def test_misc(self) -> None:
        input = """contract add_your_code_here { }"""

        ast = parse(input)
        self.assertIsNotNone(ast)
