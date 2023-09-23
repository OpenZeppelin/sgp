import unittest
import pathlib
import os

from src.sgp_parser import parse

class TestParsing(unittest.TestCase):

    def test_parsing(self):
        current_directory = pathlib.Path(__file__).parent.resolve()
        dir = os.path.join(current_directory, "sol_files")
        content = ""
        with open(os.path.join(dir, "test.sol"), "r") as f:
            content = f.read()

        self.assertNotEqual(content, "")

        parse(content, dump_json=True)

        