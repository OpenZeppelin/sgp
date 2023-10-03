[![Lint and test + coverage](https://github.com/OpenZeppelin/sgp/actions/workflows/lint-and-test.yml/badge.svg?branch=main)](https://github.com/OpenZeppelin/sgp/actions/workflows/lint-and-test.yml) [![ANTLR4 test](https://github.com/OpenZeppelin/sgp/actions/workflows/antlr4-test.yml/badge.svg)](https://github.com/OpenZeppelin/sgp/actions/workflows/antlr4-test.yml)

# Solidity Grammar Parser

**SGP** - is a `Python` package that allows to build an [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) for a given [Solidity](https://solidity.readthedocs.io/)  source code.

## Kudos

- The original grammar [Solidity.g4](./Solidity.g4) was developed and maintained by [solidity-parser-antlr](https://github.com/solidity-parser/antlr).
- The node types system and AST visitor are based on [solidity-parser-parser](https://github.com/solidity-parser/parser).

## Build

Run [build.sh](./build.sh) that does the following:
- checks if `Python` is installed and downloads it if not
  - including `pip`
  - including `antlr4-python3-runtime` package
- checks if `Java` is installed and downloads it if not
  - including `jre`
  - including `jdk`
- checks if `antlr4.jar` is downloaded and downloads it if not
- runs the ANTLR jar file and compiles the [Solidity.g4](./Solidity.g4) file.

The output result can be found in the [./out](./out) directory

## Tests

Run:
- `python -m coverage run -m unittest discover -v && python -m coverage report` for the `Python` tests
- [run-tests.sh](./test/test_parsing/run-tests.sh) to execute `antlr4` parse testing

## License

[MIT](./LICENSE)
