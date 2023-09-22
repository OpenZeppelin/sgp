from antlr4.tree.Tree import ParseTreeVisitor

class Visitor(ParseTreeVisitor):
    def __init__(self):
        super().__init__()

    def visitChildren(self, node):
        return self.visit(node)
