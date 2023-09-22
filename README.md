# Solidity Language Grammar ANTLR Python parser

The [ANTLR (ANother Tool for Language Recognition) ](https://www.antlr.org/) grammar for [Solidity](https://solidity.readthedocs.io/) is maintained in [Solidity.g4](./Solidity.g4).

This is a fork of [@solidity-parser](solidity-parser/antlr) with some amendments in the [build.sh]() script that automatically installs all required dependencies and uses ANTLR to generate `Python` parser.

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

Run [run-tests.sh](./run-tests.sh) to parse [test.sol](./test.sol).

## License

[MIT](./LICENSE)
