import unittest
import pathlib
import os
import simplejson

from sgp.sgp_parser import parse
from sgp.utils import string_from_snake_to_camel_case

class TestParsing(unittest.TestCase):

    def test_parsing(self):
        current_directory = pathlib.Path(__file__).parent.resolve()

        ast_expected = ""
        with open(os.path.join(current_directory, "result.json"), "r") as f:
            ast_expected = f.read()
        self.assertNotEqual(ast_expected, "")

        test_content = ""
        with open(os.path.join(current_directory, "test.sol"), "r") as f:
            test_content = f.read()
        self.assertNotEqual(test_content, "")

        res = parse(test_content, dump_json=True)
        ast_actual = simplejson.dumps(
                res,
                default=lambda obj: {
                    string_from_snake_to_camel_case(k): v
                    for k, v in obj.__dict__.items()
                },
            )
        
        self.assertEqual(ast_expected, ast_actual)
        