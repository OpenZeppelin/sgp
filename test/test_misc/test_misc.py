import unittest

from sgp.sgp_parser import parse


class TestMisc(unittest.TestCase):
    def test_misc(self) -> None:
        input = """function test() public pure returns(address payable) {
        return payable(address(0));
    }"""

        ast = parse(input)
        self.assertIsNotNone(ast)
