import sgp_parser

def main():
    input = """
        contract test {
            uint256 a;
            function f() {}
        }
    """
    try:
        ast = sgp_parser.parse(input, dump_json=True)
        print(ast)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
