from typing import Dict

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream as ANTLRInputStream

from out.SolidityLexer import SolidityLexer
from out.SolidityParser import SolidityParser

from sgp_visitor import SGPVisitorOptions, SGPVisitor
from sgp_error_listener import SGPErrorListener
from tokens import build_token_list

class ParserError(Exception):
    def __init__(self, errors):
        super().__init__()
        error = errors[0]
        self.message = f"{error['message']} ({error['line']}:{error['column']})"
        self.errors = errors

def parse(input_string: str, options: SGPVisitorOptions = SGPVisitorOptions()) -> Dict:
    input_stream = ANTLRInputStream(input_string)
    lexer = SolidityLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SolidityParser(token_stream)

    listener = SGPErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(listener)

    parser.removeErrorListeners()
    parser.addErrorListener(listener)
    source_unit = parser.sourceUnit()

    ast_builder = SGPVisitor(options)
    ast = ast_builder.visit(source_unit)

    if ast is None:
        raise Exception("AST was not generated")

    #TODO: token_list what is this for?
    token_list = []
    if options.tokens:
        token_list = build_token_list(token_stream.getTokens(), options)

    if not options.errors_tolerant and listener.has_errors():
        raise ParserError(errors=listener.getErrors())

    if options.errors_tolerant and listener.has_errors():
        ast["errors"] = listener.getErrors()

    #TODO: options.tokens what is this for?
    if options.tokens:
        ast["tokens"] = token_list

    return ast
