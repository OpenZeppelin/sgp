import parser

def main():
    input = """
        contract test {
            uint256 a;
            function f() {}
        }
    """
    try:
        ast = parser.parse(input)
        print(ast)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
