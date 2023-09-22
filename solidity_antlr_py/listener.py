from out.SolidityListener import SolidityListener

class Listener(SolidityListener):

    def __init__(self, res) -> None:
        super().__init__()
        self._res = res
    
    # implement all functions from SolidityListener

    def enterSourceUnit(self, ctx):
        self._res['type'] = 'SourceUnit'
        self._res['children'] = []

    def exitSourceUnit(self, ctx):
        pass

    def enterPragmaDirective(self, ctx):
        pass

    def exitPragmaDirective(self, ctx):
        pass
