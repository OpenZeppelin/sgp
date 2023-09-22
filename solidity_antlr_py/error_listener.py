from antlr4.error.ErrorListener import ErrorListener

class CustomErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self._errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self._errors.append({"message": msg, "line": line, "column": column})

    def getErrors(self):
        return self._errors

    def hasErrors(self):
        return len(self._errors) > 0
