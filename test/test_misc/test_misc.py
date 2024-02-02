import unittest

from sgp.sgp_parser import parse


class TestMisc(unittest.TestCase):
    def test_misc(self) -> None:
        input = """add_your_solidity_code_here"""

        ast = parse(input)
        self.assertIsNotNone(ast)
