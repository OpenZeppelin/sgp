from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream as ANTLRInputStream
from antlr4.tree.Tree import ParseTreeWalker
from out.SolidityLexer import SolidityLexer
from out.SolidityParser import SolidityParser
from ast_types import ASTNode, astNodeTypes, ASTNodeTypeString, ASTVisitor, SourceUnit
from ast_builder import ASTBuilder
from error_listener import ErrorListener
from tokens import build_token_list
from common_types import ParseOptions, Token, TokenizeOptions
from listener import Listener

class ParserError(Exception):
    def __init__(self, errors):
        super().__init__()
        error = errors[0]
        self.message = f"{error['message']} ({error['line']}:{error['column']})"
        self.errors = errors

def tokenize(input_string, options={}):
    input_stream = ANTLRInputStream(input_string)
    lexer = SolidityLexer(input_stream)
    return build_token_list(lexer.getAllTokens(), options)

def parse(input_string, options={}):
    input_stream = ANTLRInputStream(input_string)
    lexer = SolidityLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SolidityParser(token_stream)

    listener = ErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(listener)

    parser.removeErrorListeners()
    parser.addErrorListener(listener)
    parser.buildParseTree = True

    source_unit = parser.sourceUnit()

    ast_builder = ASTBuilder(options)
    ast = ast_builder.visit(source_unit)
    # ParseTreeWalker.DEFAULT.walk(ast_builder, source_unit);
    # ast_builder.visit(source_unit)
    ast = ast_builder

    if ast is None:
        raise Exception('ast should never be None')

    token_list = []
    if options.get('tokens', False):
        token_list = build_token_list(token_stream.getTokens(), options)

    if not options.get('tolerant', False) and listener.hasErrors():
        raise ParserError(errors=listener.getErrors())

    if options.get('tolerant', False) and listener.hasErrors():
        ast['errors'] = listener.getErrors()

    if options.get('tokens', False):
        ast['tokens'] = token_list

    return ast

def is_ast_node(node):
    if not isinstance(node, dict):
        return False

    if 'type' in node and isinstance(node['type'], str):
        return node['type'] in astNodeTypes

    return False

def visit(node, visitor, node_parent=None):
    if isinstance(node, list):
        for child in node:
            visit(child, visitor, node_parent)

    if not is_ast_node(node):
        return

    cont = True

    if node['type'] in visitor:
        cont = visitor[node['type']](node, node_parent)

    if not cont:
        return

    for prop in node:
        if prop in node:
            visit(node[prop], visitor, node)

    selector = f"{node['type']}:exit"
    if selector in visitor:
        visitor[selector](node, node_parent)
