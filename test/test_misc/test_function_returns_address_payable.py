import unittest

from sgp.sgp_parser import parse


class TestFunctionReturnsAddressPayable(unittest.TestCase):
    def test_function_returns_address_payable(self) -> None:
        input = """function test() public returns(address payable) {}"""
        ast = parse(input)
        self.assertIsNotNone(ast)
        self.assertEqual(1, len(ast.children))
        self.assertEqual("FunctionDefinition", ast.children[0].type)
        self.assertEqual(1, len(ast.children[0].return_parameters))
        self.assertEqual(
            "VariableDeclaration", ast.children[0].return_parameters[0].type
        )
        self.assertIsNone(ast.children[0].return_parameters[0].name)
        self.assertIsNotNone(ast.children[0].return_parameters[0].type_name)
        self.assertEqual(
            "ElementaryTypeName", ast.children[0].return_parameters[0].type_name.type
        )
        self.assertEqual("address", ast.children[0].return_parameters[0].type_name.name)
        self.assertEqual(
            "payable", ast.children[0].return_parameters[0].type_name.state_mutability
        )

    def test_function_returns_address(self) -> None:
        input = """function test() public returns(address) {}"""
        ast = parse(input)
        self.assertIsNotNone(ast)
        self.assertEqual(1, len(ast.children))
        self.assertEqual("FunctionDefinition", ast.children[0].type)
        self.assertEqual(1, len(ast.children[0].return_parameters))
        self.assertEqual(
            "VariableDeclaration", ast.children[0].return_parameters[0].type
        )
        self.assertIsNone(ast.children[0].return_parameters[0].name)
        self.assertIsNotNone(ast.children[0].return_parameters[0].type_name)
        self.assertEqual(
            "ElementaryTypeName", ast.children[0].return_parameters[0].type_name.type
        )
        self.assertEqual("address", ast.children[0].return_parameters[0].type_name.name)
        self.assertIsNone(
            ast.children[0].return_parameters[0].type_name.state_mutability
        )
