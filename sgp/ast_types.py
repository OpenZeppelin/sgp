from typing import List, Optional, Tuple

class Location:
    def __init__(self, start: dict, end: dict):
        self.start = start
        self.end = end

class BaseASTNode:
    def __init__(self, type: str, range: Optional[List[int]] = None, loc: Optional[Location] = None):
        self.type = type
        self.range = range
        self.loc = loc

class SourceUnit(BaseASTNode):
    def __init__(self, loc: Location, children: List[BaseASTNode]):
        super().__init__('SourceUnit', loc=loc)
        self.children = children

class ContractDefinition(BaseASTNode):
    def __init__(self, name: str, baseContracts: List['InheritanceSpecifier'], kind: str, subNodes: List[BaseASTNode], 
                 range: Optional[List[int]] = None, loc: Optional[Location] = None):
        super().__init__('ContractDefinition', range=range, loc=loc)
        self.name = name
        self.baseContracts = baseContracts
        self.kind = kind
        self.subNodes = subNodes

class InheritanceSpecifier(BaseASTNode):
    def __init__(self, baseName: 'UserDefinedTypeName', arguments: List['Expression'], 
                 range: Optional[List[int]] = None, loc: Optional[Location] = None):
        super().__init__('InheritanceSpecifier', range=range, loc=loc)
        self.baseName = baseName
        self.arguments = arguments

class UserDefinedTypeName(BaseASTNode):
    def __init__(self, namePath: str, range: Optional[List[int]] = None, loc: Optional[Location] = None):
        super().__init__('UserDefinedTypeName', range=range, loc=loc)
        self.namePath = namePath

astNodeTypes = (
    'SourceUnit',
    'PragmaDirective',
    'ImportDirective',
    'ContractDefinition',
    'InheritanceSpecifier',
    'StateVariableDeclaration',
    'UsingForDeclaration',
    'StructDefinition',
    'ModifierDefinition',
    'ModifierInvocation',
    'FunctionDefinition',
    'EventDefinition',
    'CustomErrorDefinition',
    'RevertStatement',
    'EnumValue',
    'EnumDefinition',
    'VariableDeclaration',
    'UserDefinedTypeName',
    'Mapping',
    'ArrayTypeName',
    'FunctionTypeName',
    'Block',
    'ExpressionStatement',
    'IfStatement',
    'WhileStatement',
    'ForStatement',
    'InlineAssemblyStatement',
    'DoWhileStatement',
    'ContinueStatement',
    'Break',
    'Continue',
    'BreakStatement',
    'ReturnStatement',
    'EmitStatement',
    'ThrowStatement',
    'VariableDeclarationStatement',
    'ElementaryTypeName',
    'FunctionCall',
    'AssemblyBlock',
    'AssemblyCall',
    'AssemblyLocalDefinition',
    'AssemblyAssignment',
    'AssemblyStackAssignment',
    'LabelDefinition',
    'AssemblySwitch',
    'AssemblyCase',
    'AssemblyFunctionDefinition',
    'AssemblyFor',
    'AssemblyIf',
    'TupleExpression',
    'NameValueExpression',
    'BooleanLiteral',
    'NumberLiteral',
    'Identifier',
    'BinaryOperation',
    'UnaryOperation',
    'NewExpression',
    'Conditional',
    'StringLiteral',
    'HexLiteral',
    'HexNumber',
    'DecimalNumber',
    'MemberAccess',
    'IndexAccess',
    'IndexRangeAccess',
    'NameValueList',
    'UncheckedStatement',
    'TryStatement',
    'CatchClause',
    'FileLevelConstant',
    'AssemblyMemberAccess',
    'TypeDefinition',
)

from typing import List, Optional, Union

class ASTNodeTypeString:
    pass  # Placeholder class for ASTNodeTypeString

class BaseASTNode:
    def __init__(self, type: str):
        self.type = type

class PragmaDirective(BaseASTNode):
    def __init__(self, name: str, value: str):
        super().__init__('PragmaDirective')
        self.name = name
        self.value = value

class ImportDirective(BaseASTNode):
    def __init__(self, path: str, pathLiteral: 'StringLiteral', unitAlias: Optional[str] = None,
                 unitAliasIdentifier: Optional['Identifier'] = None,
                 symbolAliases: Optional[List[Tuple[str, Optional[str]]]] = None,
                 symbolAliasesIdentifiers: Optional[List[Tuple['Identifier', Optional['Identifier']]]] = None):
        super().__init__('ImportDirective')
        self.path = path
        self.pathLiteral = pathLiteral
        self.unitAlias = unitAlias
        self.unitAliasIdentifier = unitAliasIdentifier
        self.symbolAliases = symbolAliases
        self.symbolAliasesIdentifiers = symbolAliasesIdentifiers

class StateVariableDeclaration(BaseASTNode):
    def __init__(self, variables: List['StateVariableDeclarationVariable'], initialValue: Optional['Expression'] = None):
        super().__init__('StateVariableDeclaration')
        self.variables = variables
        self.initialValue = initialValue

class FileLevelConstant(BaseASTNode):
    def __init__(self, typeName: 'TypeName', name: str, initialValue: 'Expression', isDeclaredConst: bool, isImmutable: bool):
        super().__init__('FileLevelConstant')
        self.typeName = typeName
        self.name = name
        self.initialValue = initialValue
        self.isDeclaredConst = isDeclaredConst
        self.isImmutable = isImmutable

class UsingForDeclaration(BaseASTNode):
    def __init__(self, typeName: Optional['TypeName'], functions: List[str], operators: List[Optional[str]],
                 libraryName: Optional[str] = None, isGlobal: bool = False):
        super().__init__('UsingForDeclaration')
        self.typeName = typeName
        self.functions = functions
        self.operators = operators
        self.libraryName = libraryName
        self.isGlobal = isGlobal

class StructDefinition(BaseASTNode):
    def __init__(self, name: str, members: List['VariableDeclaration']):
        super().__init__('StructDefinition')
        self.name = name
        self.members = members

class ModifierDefinition(BaseASTNode):
    def __init__(self, name: str, parameters: Optional[List['VariableDeclaration']] = None, isVirtual: bool = False,
                 override: Optional[List['UserDefinedTypeName']] = None, body: Optional['Block'] = None):
        super().__init__('ModifierDefinition')
        self.name = name
        self.parameters = parameters
        self.isVirtual = isVirtual
        self.override = override
        self.body = body

class ModifierInvocation(BaseASTNode):
    def __init__(self, name: str, arguments: Optional[List['Expression']] = None):
        super().__init__('ModifierInvocation')
        self.name = name
        self.arguments = arguments

class FunctionDefinition(BaseASTNode):
    def __init__(self, name: Optional[str], parameters: List['VariableDeclaration'], modifiers: List['ModifierInvocation'],
                 stateMutability: Optional[str] = None, visibility: str = 'default',
                 returnParameters: Optional[List['VariableDeclaration']] = None, body: Optional['Block'] = None,
                 override: Optional[List['UserDefinedTypeName']] = None, isConstructor: bool = False,
                 isReceiveEther: bool = False, isFallback: bool = False, isVirtual: bool = False):
        super().__init__('FunctionDefinition')
        self.name = name
        self.parameters = parameters
        self.modifiers = modifiers
        self.stateMutability = stateMutability
        self.visibility = visibility
        self.returnParameters = returnParameters
        self.body = body
        self.override = override
        self.isConstructor = isConstructor
        self.isReceiveEther = isReceiveEther
        self.isFallback = isFallback
        self.isVirtual = isVirtual

class CustomErrorDefinition(BaseASTNode):
    def __init__(self, name: str, parameters: List['VariableDeclaration']):
        super().__init__('CustomErrorDefinition')
        self.name = name
        self.parameters = parameters

class TypeDefinition(BaseASTNode):
    def __init__(self, name: str, definition: 'ElementaryTypeName'):
        super().__init__('TypeDefinition')
        self.name = name
        self.definition = definition

class RevertStatement(BaseASTNode):
    def __init__(self, revertCall: 'FunctionCall'):
        super().__init__('RevertStatement')
        self.revertCall = revertCall

class EventDefinition(BaseASTNode):
    def __init__(self, name: str, parameters: List['VariableDeclaration'], isAnonymous: bool):
        super().__init__('EventDefinition')
        self.name = name
        self.parameters = parameters
        self.isAnonymous = isAnonymous

class EnumValue(BaseASTNode):
    def __init__(self, name: str):
        super().__init__('EnumValue')
        self.name = name

class EnumDefinition(BaseASTNode):
    def __init__(self, name: str, members: List[EnumValue]):
        super().__init__('EnumDefinition')
        self.name = name
        self.members = members

class VariableDeclaration(BaseASTNode):
    def __init__(self, isIndexed: bool, isStateVar: bool, typeName: Optional['TypeName'] = None,
                 name: Optional[str] = None, identifier: Optional['Identifier'] = None, isDeclaredConst: Optional[bool] = None,
                 storageLocation: Optional[str] = None, expression: Optional['Expression'] = None,
                 visibility: Optional[str] = None):
        super().__init__('VariableDeclaration')
        self.isIndexed = isIndexed
        self.isStateVar = isStateVar
        self.typeName = typeName
        self.name = name
        self.identifier = identifier
        self.isDeclaredConst = isDeclaredConst
        self.storageLocation = storageLocation
        self.expression = expression
        self.visibility = visibility

class StateVariableDeclarationVariable(VariableDeclaration):
    def __init__(self, isImmutable: bool, override: Optional[List['UserDefinedTypeName']] = None, **kwargs):
        super().__init__(**kwargs)
        self.isImmutable = isImmutable
        self.override = override

class ArrayTypeName(BaseASTNode):
    def __init__(self, baseTypeName: 'TypeName', length: Optional['Expression'] = None):
        super().__init__('ArrayTypeName')
        self.baseTypeName = baseTypeName
        self.length = length

class Mapping(BaseASTNode):
    def __init__(self, keyType: Union['ElementaryTypeName', 'UserDefinedTypeName'],
                 keyName: Optional['Identifier'] = None,
                 valueType: 'TypeName' = None,
                 valueName: Optional['Identifier'] = None):
        super().__init__('Mapping')
        self.keyType = keyType
        self.keyName = keyName
        self.valueType = valueType
        self.valueName = valueName

class FunctionTypeName(BaseASTNode):
    def __init__(self, parameterTypes: List['VariableDeclaration'], returnTypes: List['VariableDeclaration'],
                 visibility: str, stateMutability: Optional[str] = None):
        super().__init__('FunctionTypeName')
        self.parameterTypes = parameterTypes
        self.returnTypes = returnTypes
        self.visibility = visibility
        self.stateMutability = stateMutability

class Block(BaseASTNode):
    def __init__(self, statements: List[BaseASTNode]):
        super().__init__('Block')
        self.statements = statements

class ExpressionStatement(BaseASTNode):
    def __init__(self, expression: Optional['Expression'] = None):
        super().__init__('ExpressionStatement')
        self.expression = expression

class IfStatement(BaseASTNode):
    def __init__(self, condition: 'Expression', trueBody: 'Statement', falseBody: Optional['Statement'] = None):
        super().__init__('IfStatement')
        self.condition = condition
        self.trueBody = trueBody
        self.falseBody = falseBody

class UncheckedStatement(BaseASTNode):
    def __init__(self, block: 'Block'):
        super().__init__('UncheckedStatement')
        self.block = block

class TryStatement(BaseASTNode):
    def __init__(self,
                 expression: 'Expression',
                 returnParameters: Optional[List['VariableDeclaration']] = None,
                 body: 'Block' = None,
                 catchClauses: List['CatchClause'] = None):
        super().__init__('TryStatement')
        self.expression = expression
        self.returnParameters = returnParameters
        self.body = body
        self.catchClauses = catchClauses or []

class CatchClause(BaseASTNode):
    def __init__(self, isReasonStringType: bool, kind: Optional[str] = None,
                 parameters: Optional[List['VariableDeclaration']] = None, body: 'Block' = None):
        super().__init__('CatchClause')
        self.isReasonStringType = isReasonStringType
        self.kind = kind
        self.parameters = parameters
        self.body = body

class WhileStatement(BaseASTNode):
    def __init__(self, condition: 'Expression', body: 'Statement'):
        super().__init__('WhileStatement')
        self.condition = condition
        self.body = body

class ForStatement(BaseASTNode):
    def __init__(self, initExpression: Optional['SimpleStatement'] = None,
                 conditionExpression: Optional['Expression'] = None, loopExpression: 'ExpressionStatement' = None,
                 body: 'Statement' = None):
        super().__init__('ForStatement')
        self.initExpression = initExpression
        self.conditionExpression = conditionExpression
        self.loopExpression = loopExpression
        self.body = body

class InlineAssemblyStatement(BaseASTNode):
    def __init__(self, language: Optional[str] = None, flags: List[str] = None, body: 'AssemblyBlock' = None):
        super().__init__('InlineAssemblyStatement')
        self.language = language
        self.flags = flags or []
        self.body = body

class DoWhileStatement(BaseASTNode):
    def __init__(self, condition: 'Expression', body: 'Statement'):
        super().__init__('DoWhileStatement')
        self.condition = condition
        self.body = body

class ContinueStatement(BaseASTNode):
    def __init__(self):
        super().__init__('ContinueStatement')

class Break(BaseASTNode):
    def __init__(self):
        super().__init__('Break')

class Continue(BaseASTNode):
    def __init__(self):
        super().__init__('Continue')

class BreakStatement(BaseASTNode):
    def __init__(self):
        super().__init__('BreakStatement')

class ReturnStatement(BaseASTNode):
    def __init__(self, expression: Optional['Expression'] = None):
        super().__init__('ReturnStatement')
        self.expression = expression

class EmitStatement(BaseASTNode):
    def __init__(self, eventCall: 'FunctionCall'):
        super().__init__('EmitStatement')
        self.eventCall = eventCall

class ThrowStatement(BaseASTNode):
    def __init__(self):
        super().__init__('ThrowStatement')

class VariableDeclarationStatement(BaseASTNode):
    def __init__(self, variables: List[Union[BaseASTNode, None]], initialValue: Optional['Expression'] = None):
        super().__init__('VariableDeclarationStatement')
        self.variables = variables
        self.initialValue = initialValue

class ElementaryTypeName(BaseASTNode):
    def __init__(self, name: str, stateMutability: Optional[str] = None):
        super().__init__('ElementaryTypeName')
        self.name = name
        self.stateMutability = stateMutability

class FunctionCall(BaseASTNode):
    def __init__(self, expression: 'Expression', arguments: List['Expression'], names: List[str], identifiers: List['Identifier']):
        super().__init__('FunctionCall')
        self.expression = expression
        self.arguments = arguments
        self.names = names
        self.identifiers = identifiers

class AssemblyBlock(BaseASTNode):
    def __init__(self, operations: List['AssemblyItem']):
        super().__init__('AssemblyBlock')
        self.operations = operations

class AssemblyCall(BaseASTNode):
    def __init__(self, functionName: str, arguments: List['AssemblyExpression']):
        super().__init__('AssemblyCall')
        self.functionName = functionName
        self.arguments = arguments

class AssemblyLocalDefinition(BaseASTNode):
    def __init__(self, names: Union[List['Identifier'], List['AssemblyMemberAccess']], expression: Optional['AssemblyExpression'] = None):
        super().__init__('AssemblyLocalDefinition')
        self.names = names
        self.expression = expression

class AssemblyAssignment(BaseASTNode):
    def __init__(self, names: Union[List['Identifier'], List['AssemblyMemberAccess']], expression: 'AssemblyExpression'):
        super().__init__('AssemblyAssignment')
        self.names = names
        self.expression = expression

class AssemblyStackAssignment(BaseASTNode):
    def __init__(self, name: str, expression: 'AssemblyExpression'):
        super().__init__('AssemblyStackAssignment')
        self.name = name
        self.expression = expression

class LabelDefinition(BaseASTNode):
    def __init__(self, name: str):
        super().__init__('LabelDefinition')
        self.name = name

class AssemblySwitch(BaseASTNode):
    def __init__(self, expression: 'AssemblyExpression', cases: List['AssemblyCase']):
        super().__init__('AssemblySwitch')
        self.expression = expression
        self.cases = cases

class AssemblyCase(BaseASTNode):
    def __init__(self, value: Union['AssemblyLiteral', None], block: 'AssemblyBlock', default: bool):
        super().__init__('AssemblyCase')
        self.value = value
        self.block = block
        self.default = default

class AssemblyFunctionDefinition(BaseASTNode):
    def __init__(self, name: str, arguments: List['Identifier'], returnArguments: List['Identifier'], body: 'AssemblyBlock'):
        super().__init__('AssemblyFunctionDefinition')
        self.name = name
        self.arguments = arguments
        self.returnArguments = returnArguments
        self.body = body

class AssemblyFor(BaseASTNode):
    def __init__(self, pre: Union['AssemblyBlock', 'AssemblyExpression'], condition: 'AssemblyExpression',
                 post: Union['AssemblyBlock', 'AssemblyExpression'], body: 'AssemblyBlock'):
        super().__init__('AssemblyFor')
        self.pre = pre
        self.condition = condition
        self.post = post
        self.body = body

class AssemblyIf(BaseASTNode):
    def __init__(self, condition: 'AssemblyExpression', body: 'AssemblyBlock'):
        super().__init__('AssemblyIf')
        self.condition = condition
        self.body = body

class AssemblyLiteral(BaseASTNode):
    pass  # Placeholder class for AssemblyLiteral

class AssemblyMemberAccess(BaseASTNode):
    def __init__(self, expression: 'Identifier', memberName: 'Identifier'):
        super().__init__('AssemblyMemberAccess')
        self.expression = expression
        self.memberName = memberName

class NewExpression(BaseASTNode):
    def __init__(self, typeName: 'TypeName'):
        super().__init__('NewExpression')
        self.typeName = typeName

class TupleExpression(BaseASTNode):
    def __init__(self, components: List[Union[BaseASTNode, None]], isArray: bool):
        super().__init__('TupleExpression')
        self.components = components
        self.isArray = isArray

class NameValueExpression(BaseASTNode):
    def __init__(self, expression: 'Expression', arguments: 'NameValueList'):
        super().__init__('NameValueExpression')
        self.expression = expression
        self.arguments = arguments

class NumberLiteral(BaseASTNode):
    def __init__(self, number: str, subdenomination: Optional[str] = None):
        super().__init__('NumberLiteral')
        self.number = number
        self.subdenomination = subdenomination

class BooleanLiteral(BaseASTNode):
    def __init__(self, value: bool):
        super().__init__('BooleanLiteral')
        self.value = value

class HexLiteral(BaseASTNode):
    def __init__(self, value: str, parts: List[str]):
        super().__init__('HexLiteral')
        self.value = value
        self.parts = parts

class StringLiteral(BaseASTNode):
    def __init__(self, value: str, parts: List[str], isUnicode: List[bool]):
        super().__init__('StringLiteral')
        self.value = value
        self.parts = parts
        self.isUnicode = isUnicode

class Identifier(BaseASTNode):
    def __init__(self, name: str):
        super().__init__('Identifier')
        self.name = name

binaryOpValues = [
    '+', '-', '*', '/', '**', '%', '<<', '>>', '&&', '||', ',,', '&', ',', '^', '<', '>', '<=', '>=', '==', '!=', '=',
    ',=', '^=', '&=', '<<=', '>>=', '+=', '-=', '*=', '/=', '%=', '|', '|=',
]
BinOp = (
    '+', '-', '*', '/', '**', '%', '<<', '>>', '&&', '||', ',,', '&', ',', '^', '<', '>', '<=', '>=', '==', '!=', '=',
    ',=', '^=', '&=', '<<=', '>>=', '+=', '-=', '*=', '/=', '%=', '|', '|=',
)

unaryOpValues = ['-', '+', '++', '--', '~', 'after', 'delete', '!']
UnaryOp = ('-', '+', '++', '--', '~', 'after', 'delete', '!')

class BinaryOperation(BaseASTNode):
    def __init__(self, left: 'Expression', right: 'Expression', operator: BinOp):
        super().__init__('BinaryOperation')
        self.left = left
        self.right = right
        self.operator = operator

class UnaryOperation(BaseASTNode):
    def __init__(self, operator: UnaryOp, subExpression: 'Expression', isPrefix: bool):
        super().__init__('UnaryOperation')
        self.operator = operator
        self.subExpression = subExpression
        self.isPrefix = isPrefix

class Conditional(BaseASTNode):
    def __init__(self, condition: 'Expression', trueExpression: 'Expression', falseExpression: 'Expression'):
        super().__init__('Conditional')
        self.condition = condition
        self.trueExpression = trueExpression
        self.falseExpression = falseExpression

class IndexAccess(BaseASTNode):
    def __init__(self, base: 'Expression', index: 'Expression'):
        super().__init__('IndexAccess')
        self.base = base
        self.index = index

class IndexRangeAccess(BaseASTNode):
    def __init__(self, base: 'Expression', indexStart: Optional['Expression'] = None, indexEnd: Optional['Expression'] = None):
        super().__init__('IndexRangeAccess')
        self.base = base
        self.indexStart = indexStart
        self.indexEnd = indexEnd

class MemberAccess(BaseASTNode):
    def __init__(self, expression: 'Expression', memberName: str):
        super().__init__('MemberAccess')
        self.expression = expression
        self.memberName = memberName

class HexNumber(BaseASTNode):
    def __init__(self, value: str):
        super().__init__('HexNumber')
        self.value = value

class DecimalNumber(BaseASTNode):
    def __init__(self, value: str):
        super().__init__('DecimalNumber')
        self.value = value

class NameValueList(BaseASTNode):
    def __init__(self, names: List[str], identifiers: List['Identifier'], arguments: List['Expression']):
        super().__init__('NameValueList')
        self.names = names
        self.identifiers = identifiers
        self.arguments = arguments

from typing import TypeVar, Dict, Callable

# Define a dictionary mapping AST node types to their corresponding types
ASTNodeTypeString = str  # Replace with actual string union of node types
U = TypeVar('U', bound="ASTNode")
ASTMap = Dict[ASTNodeTypeString, U]

# Define a dictionary type for visitor functions
ASTVisitorEnter = Dict[ASTNodeTypeString, Callable[[U, Optional["ASTNode"]], None]]
ASTVisitorExit = Dict[ASTNodeTypeString, Callable[[U, Optional["ASTNode"]], None]]

# Combine visitor dictionaries into a single visitor object
class ASTVisitor:
    def __init__(self, enter: ASTVisitorEnter = {}, exit: ASTVisitorExit = {}):
        self.enter = enter
        self.exit = exit

# Create a function to check type consistency
def checkTypes():
    ast_node_type: str = ""
    ast_node_type_string: ASTNodeTypeString = ""
    ast_visitor_enter_key: str = ""
    
    assign_ast_node_type: str = ast_node_type_string
    assign_ast_node_type = ast_visitor_enter_key
    
    assign_ast_node_type_string: ASTNodeTypeString = ast_node_type
    assign_ast_node_type_string = ast_visitor_enter_key
    
    assign_ast_visitor_enter_key: str = ast_node_type
    assign_ast_visitor_enter_key = ast_node_type_string
    
    ast_node_type_exit: str = ""
    ast_node_type_string_exit: ASTNodeTypeString = ""
    ast_visitor_enter_key_exit: str = ""
    ast_visitor_exit_key: str = ""
    
    let_ast_node_type_exit: str = ast_node_type_string_exit
    let_ast_node_type_exit = ast_visitor_enter_key_exit
    let_ast_node_type_exit = ast_visitor_exit_key
    
    assign_ast_node_type_string_exit: ASTNodeTypeString = ast_node_type_exit
    assign_ast_node_type_string_exit = ast_visitor_enter_key_exit
    assign_ast_node_type_string_exit = ast_visitor_exit_key
    
    assign_ast_visitor_enter_key_exit: str = ast_node_type_exit
    assign_ast_visitor_enter_key_exit = ast_node_type_string_exit
    assign_ast_visitor_enter_key_exit = ast_visitor_exit_key
    
    assign_ast_visitor_exit_key: str = ast_node_type_exit
    assign_ast_visitor_exit_key = ast_node_type_string_exit
    assign_ast_visitor_exit_key = ast_visitor_enter_key_exit

# Call the type checking function
checkTypes()

from typing import List, Optional, Union

class ASTNode:
    pass

class AssemblyItem(ASTNode):
    pass

class AssemblyExpression(AssemblyItem):
    pass

class Expression(ASTNode):
    pass

class PrimaryExpression(Expression):
    pass

class SimpleStatement:
    pass

# class TypeName:
#     pass

# class Statement:
#     pass

# class SourceUnit(ASTNode):
#     pass

# class PragmaDirective(ASTNode):
#     pass

# class ImportDirective(ASTNode):
#     pass

# class ContractDefinition(ASTNode):
#     pass

# class InheritanceSpecifier(ASTNode):
#     pass

# class StateVariableDeclaration(ASTNode):
#     pass

# class UsingForDeclaration(ASTNode):
#     pass

# class StructDefinition(ASTNode):
#     pass

# class ModifierDefinition(ASTNode):
#     pass

# class ModifierInvocation(ASTNode):
#     pass

# class FunctionDefinition(ASTNode):
#     pass

# class EventDefinition(ASTNode):
#     pass

# class CustomErrorDefinition(ASTNode):
#     pass

# class EnumValue(ASTNode):
#     pass

# class EnumDefinition(ASTNode):
#     pass

# class VariableDeclaration(ASTNode):
#     pass

# class TypeName(ASTNode):
#     pass

# class UserDefinedTypeName(ASTNode):
#     pass

# class Mapping(ASTNode):
#     pass

# class FunctionTypeName(ASTNode):
#     pass

# class Block(ASTNode):
#     pass

class Statement(ASTNode):
    pass

# class ElementaryTypeName(ASTNode):
#     pass

# class AssemblyBlock(ASTNode):
#     pass

# class AssemblyCall(ASTNode):
#     pass

# class AssemblyLocalDefinition(ASTNode):
#     pass

# class AssemblyAssignment(ASTNode):
#     pass

# class AssemblyStackAssignment(ASTNode):
#     pass

# class LabelDefinition(ASTNode):
#     pass

# class AssemblySwitch(ASTNode):
#     pass

# class AssemblyCase(ASTNode):
#     pass

# class AssemblyFunctionDefinition(ASTNode):
#     pass

# class AssemblyFor(ASTNode):
#     pass

# class AssemblyIf(ASTNode):
#     pass

# class AssemblyLiteral(ASTNode):
#     pass

# class TupleExpression(ASTNode):
#     pass

# class BinaryOperation(ASTNode):
#     pass

# class Conditional(ASTNode):
#     pass

# class IndexAccess(ASTNode):
#     pass

# class IndexRangeAccess(ASTNode):
#     pass

# class NameValueList(ASTNode):
#     pass

# class AssemblyMemberAccess(ASTNode):
#     pass

# class CatchClause(ASTNode):
#     pass

# class FileLevelConstant(ASTNode):
#     pass

# class TypeDefinition(ASTNode):
#     pass

# class BooleanLiteral(PrimaryExpression):
#     pass

# class HexLiteral(PrimaryExpression):
#     pass

# class StringLiteral(PrimaryExpression):
#     pass

# class NumberLiteral(PrimaryExpression):
#     pass

# class Identifier(PrimaryExpression):
#     pass

# class TupleExpression(PrimaryExpression):
#     pass

# class TypeName(PrimaryExpression):
#     pass

# class TypeName(TypeName):
#     pass
