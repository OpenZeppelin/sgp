import sgp_parser

def main():
    input = """
        // SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

struct FreeStruct {
    uint256 x;
}

enum FreeEnum {
    A,
    B,
    C
}

contract X {

    struct NotFreeStruct {
        address someAddress;
    }

    enum NotFreeEnum {
        D, E, G
    }

}

    """
    try:
        ast = sgp_parser.parse(input, dump_json=True)
        print(ast)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
