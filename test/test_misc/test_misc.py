import unittest

from sgp.sgp_parser import parse


class TestMisc(unittest.TestCase):
    def test_misc(self) -> None:
        input = """"""

        ast = parse(input)
        self.assertIsNotNone(ast)
