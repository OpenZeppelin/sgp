import unittest

from sgp.sgp_parser import parse


class TestMisc(unittest.TestCase):
    def test_misc(self) -> None:
        input = """contract Example4 {
    /// @custom:storage-location erc7201:example.main
    struct MainStorage {
        uint256 x;
        uint256 y;
    }

    // keccak256(abi.encode(uint256(keccak256("example.main")) - 1)) & ~bytes32(uint256(0xff));
    bytes32 private constant MAIN_STORAGE_LOCATION =
        0x183a6125c38840424c4a85fa12bab2ab606c4b6d0e7cc73c0c06ba5300eab500;

    uint256 constant x = 1;

    function _getMainStorage() private pure returns (MainStorage storage $) {
        assembly {
            $.slot := MAIN_STORAGE_LOCATION
        }
    }
}"""

        ast = parse(input)
        self.assertIsNotNone(ast)
        self.assertTrue(ast.children[0].children[1].variables[0].is_declared_const)
        self.assertTrue(ast.children[0].children[2].variables[0].is_declared_const)
