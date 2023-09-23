from typing import Any, List, Optional, Tuple, Union

from antlr4.tree.Tree import ErrorNode
from antlr4 import ParserRuleContext
from antlr4.tree.Tree import ParseTree

from .parser.SolidityParser import SolidityParser as SP
from .parser.SolidityVisitor import SolidityVisitor

from .ast_node_types import *


class SGPVisitorOptions:
    def __init__(
        self,
        tokens: bool = False,
        tolerant: bool = True,
        range: bool = True,
        loc: bool = True,
    ):
        """
        Contains options for the SGPVisitor

        Parameters
        ----------
        tokens : bool, optional, default False - #TODO: what is this for?
        tolerant : bool, optional, default True - suppress not critical [CST](https://en.wikipedia.org/wiki/Parse_tree) traversing errors
        range : bool, optional, default True - add range (start, end offset) information to AST nodes
        loc : bool, optional, default True - add line/column location information to AST nodes
        """
        self.range: bool = range
        self.loc: bool = loc
        self.tokens: bool = tokens  # TODO: what is this for?
        self.errors_tolerant: bool = tolerant


class SGPVisitor(SolidityVisitor):
    def __init__(self, options: SGPVisitorOptions):
        super().__init__()
        self._current_contract = None
        self._options = options

    def defaultResult(self):
        return {}

    def aggregateResult(self, aggregate, nextResult):
        return {"type": ""}

    def visitSourceUnit(self, ctx: SP.SourceUnitContext) -> SourceUnit:
        children = [child for child in ctx.children if not isinstance(child, ErrorNode)]

        node = SourceUnit(
            children=[self.visit(child) for child in children[:-1]]
        )

        return self._add_meta(node, ctx)

    def visitContractPart(self, ctx: SP.ContractPartContext):
        return self.visit(ctx.getChild(0))

    def visitContractDefinition(
        self, ctx: SP.ContractDefinitionContext
    ) -> ContractDefinition:
        name = self._toText(ctx.identifier())
        kind = self._toText(ctx.getChild(0))

        self._current_contract = name

        node = ContractDefinition(
            name=name,
            base_contracts=list(
                map(self.visitInheritanceSpecifier, ctx.inheritanceSpecifier())
            ),
            children=list(map(self.visit, ctx.contractPart())),
            kind=kind,
        )

        return self._add_meta(node, ctx)

    def visitStateVariableDeclaration(self, ctx: SP.StateVariableDeclarationContext):
        type = self.visitTypeName(ctx.typeName())
        iden = ctx.identifier()
        name = self._toText(iden)

        expression = None
        ctxExpression = ctx.expression()
        if ctxExpression:
            expression = self.visitExpression(ctxExpression)

        visibility = "default"
        if len(ctx.InternalKeyword()) > 0:
            visibility = "internal"
        elif len(ctx.PublicKeyword()) > 0:
            visibility = "public"
        elif len(ctx.PrivateKeyword()) > 0:
            visibility = "private"

        isDeclaredConst = False
        if len(ctx.ConstantKeyword()) > 0:
            isDeclaredConst = True

        override = None
        overrideSpecifier = ctx.overrideSpecifier()
        if len(overrideSpecifier) == 0:
            override = None
        else:
            override = [
                self.visitUserDefinedTypeName(x)
                for x in overrideSpecifier[0].userDefinedTypeName()
            ]

        isImmutable = False
        if len(ctx.ImmutableKeyword()) > 0:
            isImmutable = True

        decl = StateVariableDeclarationVariable(
            typeName=type,
            name=name,
            identifier=self.visitIdentifier(iden),
            expression=expression,
            visibility=visibility,
            isStateVar=True,
            isDeclaredConst=isDeclaredConst,
            isIndexed=False,
            isImmutable=isImmutable,
            override=override,
            storageLocation=None,
        )

        node = StateVariableDeclaration(
            variables=[self._add_meta(decl, ctx)], initial_value=expression
        )

        return self._add_meta(node, ctx)

    def visitVariableDeclaration(
        self, ctx: SP.VariableDeclarationContext
    ) -> VariableDeclaration:
        storageLocation = None
        ctxStorageLocation = ctx.storageLocation()
        if ctxStorageLocation:
            storageLocation = self._toText(ctxStorageLocation)

        identifierCtx = ctx.identifier()

        node = VariableDeclaration(
            typeName=self.visitTypeName(ctx.typeName()),
            name=self._toText(identifierCtx),
            identifier=self.visitIdentifier(identifierCtx),
            storageLocation=storageLocation,
            isStateVar=False,
            isIndexed=False,
            expression=None,
        )

        return self._add_meta(node, ctx)

    def visitVariableDeclarationStatement(
        self, ctx: SP.VariableDeclarationStatementContext
    ) -> VariableDeclarationStatement:
        variables = []
        ctxVariableDeclaration = ctx.variableDeclaration()
        ctxIdentifierList = ctx.identifierList()
        ctxVariableDeclarationList = ctx.variableDeclarationList()

        if ctxVariableDeclaration is not None:
            variables = [self.visitVariableDeclaration(ctxVariableDeclaration)]
        elif ctxIdentifierList is not None:
            variables = self.buildIdentifierList(ctxIdentifierList)
        elif ctxVariableDeclarationList:
            variables = self.buildVariableDeclarationList(ctxVariableDeclarationList)

        initialValue = None
        ctxExpression = ctx.expression()
        if ctxExpression:
            initialValue = self.visitExpression(ctxExpression)

        node = VariableDeclarationStatement(
            type="VariableDeclarationStatement",
            variables=variables,
            initialValue=initialValue,
        )

        return self._add_meta(node, ctx)

    def visitStatement(self, ctx: SP.StatementContext) -> Statement:
        return self.visit(ctx.getChild(0))  # Assuming the child type is Statement

    def visitSimpleStatement(
        self, ctx: SP.SimpleStatementContext
    ) -> SimpleStatement:
        return self.visit(ctx.getChild(0))  # Assuming the child type is SimpleStatement

    def visitEventDefinition(
        self, ctx: SP.EventDefinitionContext
    ) -> EventDefinition:
        parameters = [
            self._add_meta(
                VariableDeclaration(
                    type="VariableDeclaration",
                    typeName=self.visitTypeName(paramCtx.typeName()),
                    name=self._toText(paramCtx.identifier())
                    if paramCtx.identifier()
                    else None,
                    identifier=self.visitIdentifier(paramCtx.identifier())
                    if paramCtx.identifier()
                    else None,
                    isStateVar=False,
                    isIndexed=bool(paramCtx.IndexedKeyword() is not None),
                    storageLocation=None,
                    expression=None,
                ),
                paramCtx,
            )
            for paramCtx in ctx.eventParameterList().eventParameter()
        ]

        node = EventDefinition(
            type="EventDefinition",
            name=self._toText(ctx.identifier()),
            parameters=parameters,
            isAnonymous=bool(ctx.AnonymousKeyword() is not None),
        )

        return self._add_meta(node, ctx)

    def visitBlock(self, ctx: SP.BlockContext) -> Block:
        node = Block(statements=[self.visitStatement(x) for x in ctx.statement()])

        return self._add_meta(node, ctx)

    def visitParameter(self, ctx: SP.ParameterContext) -> VariableDeclaration:
        storageLocation = (
            self._toText(ctx.storageLocation()) if ctx.storageLocation() else None
        )
        name = self._toText(ctx.identifier()) if ctx.identifier() else None

        node = VariableDeclaration(
            typeName=self.visitTypeName(ctx.typeName()),
            name=name,
            identifier=self.visitIdentifier(ctx.identifier())
            if ctx.identifier()
            else None,
            storageLocation=storageLocation,
            isStateVar=False,
            isIndexed=False,
            expression=None,
        )

        return self._add_meta(node, ctx)

    def visitFunctionDefinition(
        self, ctx: SP.FunctionDefinitionContext
    ) -> FunctionDefinition:
        isConstructor = False
        isFallback = False
        isReceiveEther = False
        isVirtual = False
        name = None
        parameters = []
        returnParameters = None
        visibility = "default"

        block = None
        ctxBlock = ctx.block()
        if ctxBlock is not None:
            block = self.visitBlock(ctxBlock)

        modifiers = [
            self.visitModifierInvocation(mod)
            for mod in ctx.modifierList().modifierInvocation()
        ]

        stateMutability = None
        if ctx.modifierList().stateMutability():
            stateMutability = self._stateMutabilityToText(
                ctx.modifierList().stateMutability(0)
            )

        # see what type of function we"re dealing with
        ctxReturnParameters = ctx.returnParameters()
        func_desc_child = self._toText(ctx.functionDescriptor().getChild(0))
        if func_desc_child == "constructor":
            parameters = [self.visit(x) for x in ctx.parameterList().parameter()]
            # error out on incorrect function visibility
            if ctx.modifierList().InternalKeyword():
                visibility = "internal"
            elif ctx.modifierList().PublicKeyword():
                visibility = "public"
            else:
                visibility = "default"
            isConstructor = True
        elif func_desc_child == "fallback":
            parameters = [self.visit(x) for x in ctx.parameterList().parameter()]
            returnParameters = (
                self.visitReturnParameters(ctxReturnParameters)
                if ctxReturnParameters
                else None
            )
            visibility = "external"
            isFallback = True
        elif func_desc_child == "receive":
            visibility = "external"
            isReceiveEther = True
        elif func_desc_child == "function":
            identifier = ctx.functionDescriptor().identifier()
            name = self._toText(identifier) if identifier is not None else ""
            parameters = [self.visit(x) for x in ctx.parameterList().parameter()]
            returnParameters = (
                self.visitReturnParameters(ctxReturnParameters)
                if ctxReturnParameters
                else None
            )
            # parse function visibility
            if ctx.modifierList().ExternalKeyword():
                visibility = "external"
            elif ctx.modifierList().InternalKeyword():
                visibility = "internal"
            elif ctx.modifierList().PublicKeyword():
                visibility = "public"
            elif ctx.modifierList().PrivateKeyword():
                visibility = "private"
            isConstructor = name == self._current_contract
            isFallback = name == ""

        # check if function is virtual
        if ctx.modifierList().VirtualKeyword():
            isVirtual = True

        override = None
        overrideSpecifier = ctx.modifierList().overrideSpecifier()
        if overrideSpecifier:
            override = [
                self.visitUserDefinedTypeName(x)
                for x in overrideSpecifier[0].userDefinedTypeName()
            ]

        node = FunctionDefinition(
            name=name,
            parameters=parameters,
            returnParameters=returnParameters,
            body=block,
            visibility=visibility,
            modifiers=modifiers,
            override=override,
            isConstructor=isConstructor,
            isReceiveEther=isReceiveEther,
            isFallback=isFallback,
            isVirtual=isVirtual,
            stateMutability=stateMutability,
        )

        return self._add_meta(node, ctx)

    def visitEnumDefinition(self, ctx: SP.EnumDefinitionContext) -> EnumDefinition:
        node = EnumDefinition(
            name=self._toText(ctx.identifier()),
            members=[self.visitEnumValue(x) for x in ctx.enumValue()],
        )

        return self._add_meta(node, ctx)

    def visitEnumValue(self, ctx: SP.EnumValueContext) -> EnumValue:
        node = EnumValue(name=self._toText(ctx.identifier()))
        return self._add_meta(node, ctx)

    def visitElementaryTypeName(
        self, ctx: SP.ElementaryTypeNameContext
    ) -> ElementaryTypeName:
        node = ElementaryTypeName(name=self._toText(ctx), stateMutability=None)

        return self._add_meta(node, ctx)

    def visitIdentifier(self, ctx: SP.IdentifierContext) -> Identifier:
        node = Identifier(name=self._toText(ctx))
        return self._add_meta(node, ctx)

    def visitTypeName(
        self, ctx: SP.TypeNameContext
    ) -> Union[ArrayTypeName, ElementaryTypeName, UserDefinedTypeName]:
        if ctx.children and len(ctx.children) > 2:
            length = None
            if len(ctx.children) == 4:
                expression = ctx.expression()
                if expression is None:
                    raise Exception(
                        "Assertion error: a typeName with 4 children should have an expression"
                    )
                length = self.visitExpression(expression)

            ctxTypeName = ctx.typeName()

            node = ArrayTypeName(
                type="ArrayTypeName",
                baseTypeName=self.visitTypeName(ctxTypeName),
                length=length,
            )

            return self._add_meta(node, ctx)

        if ctx.children and len(ctx.children) == 2:
            node = ElementaryTypeName(
                type="ElementaryTypeName",
                name=self._toText(ctx.getChild(0)),
                stateMutability=self._toText(ctx.getChild(1)),
            )

            return self._add_meta(node, ctx)

        if ctx.elementaryTypeName() is not None:
            return self.visitElementaryTypeName(ctx.elementaryTypeName())
        if ctx.userDefinedTypeName() is not None:
            return self.visitUserDefinedTypeName(ctx.userDefinedTypeName())
        if ctx.mapping() is not None:
            return self.visitMapping(ctx.mapping())
        if ctx.functionTypeName() is not None:
            return self.visitFunctionTypeName(ctx.functionTypeName())

        raise Exception("Assertion error: unhandled type name case")

    def visitUserDefinedTypeName(
        self, ctx: SP.UserDefinedTypeNameContext
    ) -> UserDefinedTypeName:
        node = UserDefinedTypeName(
            type="UserDefinedTypeName", name_path=self._toText(ctx)
        )

        return self._add_meta(node, ctx)

    def visitUsingForDeclaration(
        self, ctx: SP.UsingForDeclarationContext
    ) -> UsingForDeclaration:
        typeName = None
        ctxTypeName = ctx.typeName()
        if ctxTypeName is not None:
            typeName = self.visitTypeName(ctxTypeName)

        isGlobal = ctx.GlobalKeyword() is not None

        usingForObjectCtx = ctx.usingForObject()

        userDefinedTypeNameCtx = usingForObjectCtx.userDefinedTypeName()

        if userDefinedTypeNameCtx is not None:
            # using Lib for ...
            node = UsingForDeclaration(
                type="UsingForDeclaration",
                isGlobal=isGlobal,
                typeName=typeName,
                libraryName=self._toText(userDefinedTypeNameCtx),
                functions=[],
                operators=[],
            )
        else:
            # using { } for ...
            usingForObjectDirectives = usingForObjectCtx.usingForObjectDirective()
            functions = [
                self._toText(x.userDefinedTypeName()) for x in usingForObjectDirectives
            ]
            operators = [
                self._toText(x.userDefinableOperators())
                if x.userDefinableOperators() is not None
                else None
                for x in usingForObjectDirectives
            ]

            node = UsingForDeclaration(
                type="UsingForDeclaration",
                isGlobal=isGlobal,
                typeName=typeName,
                libraryName=None,
                functions=functions,
                operators=operators,
            )

        return self._add_meta(node, ctx)

    def visitPragmaDirective(
        self, ctx: SP.PragmaDirectiveContext
    ) -> PragmaDirective:
        # this converts something like >= 0.5.0  <0.7.0
        # in >=0.5.0 <0.7.0
        versionContext = ctx.pragmaValue().version()

        value = self._toText(ctx.pragmaValue())
        if versionContext and versionContext.children is not None:
            value = " ".join([self._toText(x) for x in versionContext.children])

        node = PragmaDirective(
            name=self._toText(ctx.pragmaName()), value=value
        )

        return self._add_meta(node, ctx)

    def visitInheritanceSpecifier(
        self, ctx: SP.InheritanceSpecifierContext
    ) -> InheritanceSpecifier:
        exprList = ctx.expressionList()
        args = (
            [self.visitExpression(x) for x in exprList.expression()]
            if exprList is not None
            else []
        )

        node = InheritanceSpecifier(
            type="InheritanceSpecifier",
            base_name=self.visitUserDefinedTypeName(ctx.userDefinedTypeName()),
            arguments=args,
        )

        return self._add_meta(node, ctx)

    def visitModifierInvocation(
        self, ctx: SP.ModifierInvocationContext
    ) -> ModifierInvocation:
        exprList = ctx.expressionList()

        args = (
            [self.visit(x) for x in exprList.expression()]
            if exprList is not None
            else []
        )

        if not args and ctx.children and len(ctx.children) > 1:
            args = None

        node = ModifierInvocation(
            type="ModifierInvocation",
            name=self._toText(ctx.identifier()),
            arguments=args,
        )
        return self._add_meta(node, ctx)

    def visitFunctionTypeName(
        self, ctx: SP.FunctionTypeNameContext
    ) -> FunctionTypeName:
        parameterTypes = [
            self.visitFunctionTypeParameter(typeCtx)
            for typeCtx in ctx.functionTypeParameterList(0).functionTypeParameter()
        ]

        returnTypes = []
        if len(ctx.functionTypeParameterList()) > 1:
            returnTypes = [
                self.visitFunctionTypeParameter(typeCtx)
                for typeCtx in ctx.functionTypeParameterList(1).functionTypeParameter()
            ]

        visibility = "default"
        if ctx.InternalKeyword():
            visibility = "internal"
        elif ctx.ExternalKeyword():
            visibility = "external"

        stateMutability = (
            self._toText(ctx.stateMutability(0)) if ctx.stateMutability() else None
        )

        node = FunctionTypeName(
            type="FunctionTypeName",
            parameterTypes=parameterTypes,
            returnTypes=returnTypes,
            visibility=visibility,
            stateMutability=stateMutability,
        )

        return self._add_meta(node, ctx)

    def visitFunctionTypeParameter(
        self, ctx: SP.FunctionTypeParameterContext
    ) -> VariableDeclaration:
        storageLocation = (
            self._toText(ctx.storageLocation()) if ctx.storageLocation() else None
        )

        node = VariableDeclaration(
            type="VariableDeclaration",
            typeName=self.visitTypeName(ctx.typeName()),
            name=None,
            identifier=None,
            storageLocation=storageLocation,
            isStateVar=False,
            isIndexed=False,
            expression=None,
        )

        return self._add_meta(node, ctx)

    def visitThrowStatement(self, ctx: SP.ThrowStatementContext) -> ThrowStatement:
        node = ThrowStatement(type="ThrowStatement")

        return self._add_meta(node, ctx)

    def visitReturnStatement(
        self, ctx: SP.ReturnStatementContext
    ) -> ReturnStatement:
        expression = (
            self.visitExpression(ctx.expression()) if ctx.expression() else None
        )

        node = ReturnStatement(expression=expression)

        return self._add_meta(node, ctx)

    def visitEmitStatement(self, ctx: SP.EmitStatementContext) -> EmitStatement:
        node = EmitStatement(
            type="EmitStatement", eventCall=self.visitFunctionCall(ctx.functionCall())
        )

        return self._add_meta(node, ctx)

    def visitCustomErrorDefinition(
        self, ctx: SP.CustomErrorDefinitionContext
    ) -> CustomErrorDefinition:
        node = CustomErrorDefinition(
            type="CustomErrorDefinition",
            name=self._toText(ctx.identifier()),
            parameters=self.visitParameterList(ctx.parameterList()),
        )

        return self._add_meta(node, ctx)

    def visitTypeDefinition(self, ctx: SP.TypeDefinitionContext) -> TypeDefinition:
        node = TypeDefinition(
            type="TypeDefinition",
            name=self._toText(ctx.identifier()),
            definition=self.visitElementaryTypeName(ctx.elementaryTypeName()),
        )

        return self._add_meta(node, ctx)

    def visitRevertStatement(
        self, ctx: SP.RevertStatementContext
    ) -> RevertStatement:
        node = RevertStatement(
            type="RevertStatement",
            revertCall=self.visitFunctionCall(ctx.functionCall()),
        )

        return self._add_meta(node, ctx)

    def visitFunctionCall(self, ctx: SP.FunctionCallContext) -> FunctionCall:
        args = []
        names = []
        identifiers = []

        ctxArgs = ctx.functionCallArguments()
        ctxArgsExpressionList = ctxArgs.expressionList()
        ctxArgsNameValueList = ctxArgs.nameValueList()
        if ctxArgsExpressionList:
            args = [
                self.visitExpression(exprCtx)
                for exprCtx in ctxArgsExpressionList.expression()
            ]
        elif ctxArgsNameValueList:
            for nameValue in ctxArgsNameValueList.nameValue():
                args.append(self.visitExpression(nameValue.expression()))
                names.append(self._toText(nameValue.identifier()))
                identifiers.append(self.visitIdentifier(nameValue.identifier()))

        node = FunctionCall(
            type="FunctionCall",
            expression=self.visitExpression(ctx.expression()),
            arguments=args,
            names=names,
            identifiers=identifiers,
        )

        return self._add_meta(node, ctx)

    def visitStructDefinition(
        self, ctx: SP.StructDefinitionContext
    ) -> StructDefinition:
        node = StructDefinition(
            name=self._toText(ctx.identifier()),
            members=[
                self.visitVariableDeclaration(x) for x in ctx.variableDeclaration()
            ],
        )

        return self._add_meta(node, ctx)

    def visitWhileStatement(self, ctx: SP.WhileStatementContext) -> WhileStatement:
        node = WhileStatement(
            type="WhileStatement",
            condition=self.visitExpression(ctx.expression()),
            body=self.visitStatement(ctx.statement()),
        )

        return self._add_meta(node, ctx)

    def visitDoWhileStatement(
        self, ctx: SP.DoWhileStatementContext
    ) -> DoWhileStatement:
        node = DoWhileStatement(
            type="DoWhileStatement",
            condition=self.visitExpression(ctx.expression()),
            body=self.visitStatement(ctx.statement()),
        )

        return self._add_meta(node, ctx)

    def visitIfStatement(self, ctx: SP.IfStatementContext) -> IfStatement:
        trueBody = self.visitStatement(ctx.statement(0))

        falseBody = None
        if len(ctx.statement()) > 1:
            falseBody = self.visitStatement(ctx.statement(1))

        node = IfStatement(
            type="IfStatement",
            condition=self.visitExpression(ctx.expression()),
            trueBody=trueBody,
            falseBody=falseBody,
        )

        return self._add_meta(node, ctx)

    def visitTryStatement(self, ctx: SP.TryStatementContext) -> TryStatement:
        returnParameters = None
        ctxReturnParameters = ctx.returnParameters()
        if ctxReturnParameters is not None:
            returnParameters = self.visitReturnParameters(ctxReturnParameters)

        catchClauses = [self.visitCatchClause(exprCtx) for exprCtx in ctx.catchClause()]

        node = TryStatement(
            type="TryStatement",
            expression=self.visitExpression(ctx.expression()),
            returnParameters=returnParameters,
            body=self.visitBlock(ctx.block()),
            catchClauses=catchClauses,
        )

        return self._add_meta(node, ctx)

    def visitCatchClause(self, ctx: SP.CatchClauseContext) -> CatchClause:
        parameters = None
        if ctx.parameterList():
            parameters = self.visitParameterList(ctx.parameterList())

        if ctx.identifier() and self._toText(ctx.identifier()) not in [
            "Error",
            "Panic",
        ]:
            raise Exception("Expected 'Error' or 'Panic' identifier in catch clause")

        kind = self._toText(ctx.identifier()) if ctx.identifier() else None

        node = CatchClause(
            type="CatchClause",
            isReasonStringType=kind
            == "Error",  # deprecated, use the `kind` property instead,
            kind=kind,
            parameters=parameters,
            body=self.visitBlock(ctx.block()),
        )

        return self._add_meta(node, ctx)

    def visitExpressionStatement(
        self, ctx: SP.ExpressionStatementContext
    ) -> ExpressionStatement:
        if not ctx:
            return None
        node = ExpressionStatement(
            type="ExpressionStatement",
            expression=self.visitExpression(ctx.expression()),
        )

        return self._add_meta(node, ctx)

    def visitNumberLiteral(self, ctx: SP.NumberLiteralContext) -> NumberLiteral:
        number = self._toText(ctx.getChild(0))
        subdenomination = None

        if ctx.children and len(ctx.children) == 2:
            subdenomination = self._toText(ctx.getChild(1))

        node = NumberLiteral(
            number=number, subdenomination=subdenomination
        )

        return self._add_meta(node, ctx)

    def visitMappingKey(
        self, ctx: SP.MappingKeyContext
    ) -> Union[ElementaryTypeName, UserDefinedTypeName]:
        if ctx.elementaryTypeName():
            return self.visitElementaryTypeName(ctx.elementaryTypeName())
        elif ctx.userDefinedTypeName():
            return self.visitUserDefinedTypeName(ctx.userDefinedTypeName())
        else:
            raise Exception(
                "Expected MappingKey to have either elementaryTypeName or userDefinedTypeName"
            )

    def visitMapping(self, ctx: SP.MappingContext) -> Mapping:
        mappingKeyNameCtx = ctx.mappingKeyName()
        mappingValueNameCtx = ctx.mappingValueName()

        node = Mapping(
            type="Mapping",
            keyType=self.visitMappingKey(ctx.mappingKey()),
            keyName=self.visitIdentifier(mappingKeyNameCtx.identifier())
            if mappingKeyNameCtx
            else None,
            valueType=self.visitTypeName(ctx.typeName()),
            valueName=self.visitIdentifier(mappingValueNameCtx.identifier())
            if mappingValueNameCtx
            else None,
        )

        return self._add_meta(node, ctx)

    def visitModifierDefinition(
        self, ctx: SP.ModifierDefinitionContext
    ) -> ModifierDefinition:
        parameters = None
        if ctx.parameterList():
            parameters = self.visitParameterList(ctx.parameterList())

        isVirtual = len(ctx.VirtualKeyword()) > 0

        override = None
        overrideSpecifier = ctx.overrideSpecifier()
        if overrideSpecifier:
            override = [
                self.visitUserDefinedTypeName(x)
                for x in overrideSpecifier[0].userDefinedTypeName()
            ]

        body = None
        blockCtx = ctx.block()
        if blockCtx:
            body = self.visitBlock(blockCtx)

        node = ModifierDefinition(
            type="ModifierDefinition",
            name=self._toText(ctx.identifier()),
            parameters=parameters,
            body=body,
            isVirtual=isVirtual,
            override=override,
        )

        return self._add_meta(node, ctx)

    def visitUncheckedStatement(
        self, ctx: SP.UncheckedStatementContext
    ) -> UncheckedStatement:
        node = UncheckedStatement(
            type="UncheckedStatement", block=self.visitBlock(ctx.block())
        )

        return self._add_meta(node, ctx)

    def visitExpression(self, ctx: SP.ExpressionContext) -> Expression:
        op = None

        if len(ctx.children) == 1:
            # primary expression
            primaryExpressionCtx = ctx.getTypedRuleContext(SP.PrimaryExpressionContext, 0)
            if primaryExpressionCtx is None:
                raise Exception(
                    "Assertion error: primary expression should exist when children length is 1"
                )
            return self.visitPrimaryExpression(primaryExpressionCtx)
        elif len(ctx.children) == 2:
            op = self._toText(ctx.getChild(0))

            # new expression
            if op == "new":
                node = NewExpression(
                    type="NewExpression", typeName=self.visitTypeName(ctx.typeName())
                )
                return self._add_meta(node, ctx)

            # prefix operators
            if op in unaryOpValues:
                node = UnaryOperation(
                    type="UnaryOperation",
                    operator=op,
                    subExpression=self.visitExpression(
                        ctx.getRuleContext(0, SP.ExpressionContext)
                    ),
                    isPrefix=True,
                )
                return self._add_meta(node, ctx)

            op = self._toText(ctx.getChild(1))

            # postfix operators
            if op in ["++", "--"]:
                node = UnaryOperation(
                    type="UnaryOperation",
                    operator=op,
                    subExpression=self.visitExpression(
                        ctx.getRuleContext(0, SP.ExpressionContext)
                    ),
                    isPrefix=False,
                )
                return self._add_meta(node, ctx)
        elif len(ctx.children) == 3:
            # treat parenthesis as no-op
            if (
                self._toText(ctx.getChild(0)) == "("
                and self._toText(ctx.getChild(2)) == ")"
            ):
                node = TupleExpression(
                    type="TupleExpression",
                    components=[
                        self.visitExpression(
                            ctx.getRuleContext(0, SP.ExpressionContext)
                        )
                    ],
                    isArray=False,
                )
                return self._add_meta(node, ctx)

            op = self._toText(ctx.getChild(1))

            # member access
            if op == ".":
                node = MemberAccess(
                    type="MemberAccess",
                    expression=self.visitExpression(ctx.expression(0)),
                    memberName=self._toText(ctx.identifier()),
                )
                return self._add_meta(node, ctx)

            if op in binary_op_values:
                node = BinaryOperation(
                    type="BinaryOperation",
                    operator=op,
                    left=self.visitExpression(ctx.expression(0)),
                    right=self.visitExpression(ctx.expression(1)),
                )
                return self._add_meta(node, ctx)
        elif len(ctx.children) == 4:
            # function call
            if (
                self._toText(ctx.getChild(1)) == "("
                and self._toText(ctx.getChild(3)) == ")"
            ):
                args = []
                names = []
                identifiers = []

                ctxArgs = ctx.functionCallArguments()
                if ctxArgs.expressionList():
                    args = [
                        self.visitExpression(exprCtx)
                        for exprCtx in ctxArgs.expressionList().expression()
                    ]
                elif ctxArgs.nameValueList():
                    for nameValue in ctxArgs.nameValueList().nameValue():
                        args.append(self.visitExpression(nameValue.expression()))
                        names.append(self._toText(nameValue.identifier()))
                        identifiers.append(self.visitIdentifier(nameValue.identifier()))

                node = FunctionCall(
                    type="FunctionCall",
                    expression=self.visitExpression(ctx.expression(0)),
                    arguments=args,
                    names=names,
                    identifiers=identifiers,
                )

                return self._add_meta(node, ctx)

            # index access
            if (
                self._toText(ctx.getChild(1)) == "["
                and self._toText(ctx.getChild(3)) == "]"
            ):
                if ctx.getChild(2).text == ":":
                    node = IndexRangeAccess(
                        type="IndexRangeAccess",
                        base=self.visitExpression(ctx.expression(0)),
                    )
                    return self._add_meta(node, ctx)

                node = IndexAccess(
                    type="IndexAccess",
                    base=self.visitExpression(ctx.expression(0)),
                    index=self.visitExpression(ctx.expression(1)),
                )

                return self._add_meta(node, ctx)

            # expression with nameValueList
            if (
                self._toText(ctx.getChild(1)) == "{"
                and self._toText(ctx.getChild(3)) == "}"
            ):
                node = NameValueExpression(
                    type="NameValueExpression",
                    expression=self.visitExpression(ctx.expression(0)),
                    arguments=self.visitNameValueList(ctx.nameValueList()),
                )

                return self._add_meta(node, ctx)
        elif len(ctx.children) == 5:
            # ternary operator
            if (
                self._toText(ctx.getChild(1)) == "?"
                and self._toText(ctx.getChild(3)) == ":"
            ):
                node = Conditional(
                    type="Conditional",
                    condition=self.visitExpression(ctx.expression(0)),
                    trueExpression=self.visitExpression(ctx.expression(1)),
                    falseExpression=self.visitExpression(ctx.expression(2)),
                )

                return self._add_meta(node, ctx)

            # index range access
            if (
                self._toText(ctx.getChild(1)) == "["
                and self._toText(ctx.getChild(2)) == ":"
                and self._toText(ctx.getChild(4)) == "]"
            ):
                node = IndexRangeAccess(
                    type="IndexRangeAccess",
                    base=self.visitExpression(ctx.expression(0)),
                    indexEnd=self.visitExpression(ctx.expression(1)),
                )

                return self._add_meta(node, ctx)
            elif (
                self._toText(ctx.getChild(1)) == "["
                and self._toText(ctx.getChild(3)) == ":"
                and self._toText(ctx.getChild(4)) == "]"
            ):
                node = IndexRangeAccess(
                    type="IndexRangeAccess",
                    base=self.visitExpression(ctx.expression(0)),
                    indexStart=self.visitExpression(ctx.expression(1)),
                )

                return self._add_meta(node, ctx)
        elif len(ctx.children) == 6:
            # index range access
            if (
                self._toText(ctx.getChild(1)) == "["
                and self._toText(ctx.getChild(3)) == ":"
                and self._toText(ctx.getChild(5)) == "]"
            ):
                node = IndexRangeAccess(
                    type="IndexRangeAccess",
                    base=self.visitExpression(ctx.expression(0)),
                    indexStart=self.visitExpression(ctx.expression(1)),
                    indexEnd=self.visitExpression(ctx.expression(2)),
                )

                return self._add_meta(node, ctx)

        raise Exception("Unrecognized expression")

    def visitNameValueList(self, ctx: SP.NameValueListContext) -> NameValueList:
        names = []
        identifiers = []
        args = []

        for nameValue in ctx.nameValue():
            names.append(self._toText(nameValue.identifier()))
            identifiers.append(self.visitIdentifier(nameValue.identifier()))
            args.append(self.visitExpression(nameValue.expression()))

        node = NameValueList(
            type="NameValueList", names=names, identifiers=identifiers, arguments=args
        )

        return self._add_meta(node, ctx)

    def visitFileLevelConstant(
        self, ctx: SP.FileLevelConstantContext
    ) -> FileLevelConstant:
        type = self.visitTypeName(ctx.typeName())
        iden = ctx.identifier()
        name = self._toText(iden)

        expression = self.visitExpression(ctx.expression())

        node = FileLevelConstant(
            type="FileLevelConstant",
            type_name=type,
            name=name,
            initial_value=expression,
            isDeclaredConst=True,
            isImmutable=False,
        )

        return self._add_meta(node, ctx)

    def visitForStatement(self, ctx: SP.ForStatementContext) -> ForStatement:
        conditionExpression = self.visitExpressionStatement(ctx.expressionStatement())
        if conditionExpression:
            conditionExpression = conditionExpression.expression
        node = ForStatement(
            type="ForStatement",
            initExpression=self.visitSimpleStatement(ctx.simpleStatement())
            if ctx.simpleStatement()
            else None,
            conditionExpression=conditionExpression,
            loopExpression=ExpressionStatement(
                type="ExpressionStatement",
                expression=self.visitExpression(ctx.expression())
                if ctx.expression()
                else None,
            ),
            body=self.visitStatement(ctx.statement()),
        )

        return self._add_meta(node, ctx)

    def visitHexLiteral(self, ctx: SP.HexLiteralContext) -> HexLiteral:
        parts = [self._toText(x)[4:-1] for x in ctx.HexLiteralFragment()]
        node = HexLiteral(type="HexLiteral", value="".join(parts), parts=parts)

        return self._add_meta(node, ctx)

    def visit_primary_expression(self, ctx) -> Union[PrimaryExpression, Any]:
        if ctx.BooleanLiteral():
            node = {
                "type": "BooleanLiteral",
                "value": self._to_text(ctx.BooleanLiteral()) == "true",
            }

            return self._add_meta(node, ctx)

        if ctx.hexLiteral():
            return self.visit_hex_literal(ctx.hexLiteral())

        if ctx.stringLiteral():
            fragments = ctx.stringLiteral().StringLiteralFragment()
            fragments_info = []

            for string_literal_fragment_ctx in fragments:
                text = self._to_text(string_literal_fragment_ctx)

                is_unicode = text[:7] == "unicode"
                if is_unicode:
                    text = text[7:]

                single_quotes = text[0] == """"""
                text_without_quotes = text[1:-1]
                if single_quotes:
                    value = text_without_quotes.replace(r"\\" ", " "")
                else:
                    value = text_without_quotes.replace(r"\\" ", " "")

                fragments_info.append({"value": value, "is_unicode": is_unicode})

            parts = [x["value"] for x in fragments_info]

            node = {
                "type": "StringLiteral",
                "value": "".join(parts),
                "parts": parts,
                "isUnicode": [x["is_unicode"] for x in fragments_info],
            }

            return self._add_meta(node, ctx)

        if ctx.numberLiteral():
            return self.visit_number_literal(ctx.numberLiteral())

        if ctx.TypeKeyword():
            node = {
                "type": "Identifier",
                "name": "type",
            }

            return self._add_meta(node, ctx)

        if ctx.typeName():
            return self.visit_type_name(ctx.typeName())

        return self.visit(ctx.getChild(0))

    def visitTupleExpression(
        self, ctx: SP.TupleExpressionContext
    ) -> TupleExpression:
        children = ctx.children[1:-1]  # remove parentheses
        components = [
            self.visit(expr) if expr is not None else None
            for expr in self._mapCommasToNulls(children)
        ]

        node = TupleExpression(
            type="TupleExpression",
            components=components,
            isArray=self._toText(ctx.getChild(0)) == "[",
        )

        return self._add_meta(node, ctx)

    def buildIdentifierList(
        self, ctx: SP.IdentifierListContext
    ) -> List[Optional[VariableDeclaration]]:
        children = ctx.children[1:-1]  # remove parentheses
        identifiers = ctx.identifier()
        i = 0
        return [
            self.buildVariableDeclaration(iden) if iden is not None else None
            for iden in self._mapCommasToNulls(children)
        ]

    def buildVariableDeclarationList(
        self, ctx: SP.VariableDeclarationListContext
    ) -> List[Optional[VariableDeclaration]]:
        variableDeclarations = ctx.variableDeclaration()
        i = 0
        return [
            self.buildVariableDeclaration(decl) if decl is not None else None
            for decl in self._mapCommasToNulls(ctx.children or [])
        ]

    def buildVariableDeclaration(
        self, ctx: SP.VariableDeclarationContext
    ) -> VariableDeclaration:
        storageLocation = (
            self._toText(ctx.storageLocation()) if ctx.storageLocation() else None
        )
        identifierCtx = ctx.identifier()
        result = VariableDeclaration(
            type="VariableDeclaration",
            name=self._toText(identifierCtx),
            identifier=self.visitIdentifier(identifierCtx),
            typeName=self.visitTypeName(ctx.typeName()),
            storageLocation=storageLocation,
            isStateVar=False,
            isIndexed=False,
            expression=None,
        )

        return self._add_meta(result, ctx)

    def visitImportDirective(
        self, ctx: SP.ImportDirectiveContext
    ) -> ImportDirective:
        pathString = self._toText(ctx.importPath())
        unitAlias = None
        unitAliasIdentifier = None
        symbolAliases = None
        symbolAliasesIdentifiers = None

        if len(ctx.importDeclaration()) > 0:
            symbolAliases = [
                [self._toText(decl.identifier(0)), self._toText(decl.identifier(1))]
                if len(decl.identifier()) > 1
                else [self._toText(decl.identifier(0)), None]
                for decl in ctx.importDeclaration()
            ]
            symbolAliasesIdentifiers = [
                [
                    self.visitIdentifier(decl.identifier(0)),
                    self.visitIdentifier(decl.identifier(1)),
                ]
                if len(decl.identifier()) > 1
                else [self.visitIdentifier(decl.identifier(0)), None]
                for decl in ctx.importDeclaration()
            ]
        else:
            identifierCtxList = ctx.identifier()
            if len(identifierCtxList) == 0:
                pass
            elif len(identifierCtxList) == 1:
                aliasIdentifierCtx = ctx.identifier(0)
                unitAlias = self._toText(aliasIdentifierCtx)
                unitAliasIdentifier = self.visitIdentifier(aliasIdentifierCtx)
            elif len(identifierCtxList) == 2:
                aliasIdentifierCtx = ctx.identifier(1)
                unitAlias = self._toText(aliasIdentifierCtx)
                unitAliasIdentifier = self.visitIdentifier(aliasIdentifierCtx)
            else:
                raise AssertionError("an import should have one or two identifiers")

        path = pathString[1:-1]

        pathLiteral = StringLiteral(
            type="StringLiteral",
            value=path,
            parts=[path],
            isUnicode=[
                False
            ],  # paths in imports don"t seem to support unicode literals
        )

        node = ImportDirective(
            type="ImportDirective",
            path=path,
            path_literal=self._add_meta(pathLiteral, ctx.importPath()),
            unit_alias=unitAlias,
            unit_alias_identifier=unitAliasIdentifier,
            symbol_aliases=symbolAliases,
            symbol_aliases_identifiers=symbolAliasesIdentifiers,
        )

        return self._add_meta(node, ctx)

    def buildEventParameterList(
        self, ctx: SP.EventParameterListContext
    ) -> List[VariableDeclaration]:
        return [
            VariableDeclaration(
                type="VariableDeclaration",
                typeName=self.visit(paramCtx.typeName()),
                name=self._toText(paramCtx.identifier())
                if paramCtx.identifier()
                else None,
                isStateVar=False,
                isIndexed=bool(paramCtx.IndexedKeyword()),
            )
            for paramCtx in ctx.eventParameter()
        ]

    def visitReturnParameters(
        self, ctx: SP.ReturnParametersContext
    ) -> List[VariableDeclaration]:
        return self.visitParameterList(ctx.parameterList())

    def visitParameterList(
        self, ctx: SP.ParameterListContext
    ) -> List[VariableDeclaration]:
        return [self.visitParameter(paramCtx) for paramCtx in ctx.parameter()]

    def visitInlineAssemblyStatement(
        self, ctx: SP.InlineAssemblyStatementContext
    ) -> InlineAssemblyStatement:
        language = None
        if ctx.StringLiteralFragment():
            language = self._toText(ctx.StringLiteralFragment())
            language = language[1:-1]

        flags = []
        flag = ctx.inlineAssemblyStatementFlag()
        if flag is not None:
            flagString = self._toText(flag.stringLiteral())
            flags.append(flagString[1:-1])

        node = InlineAssemblyStatement(
            type="InlineAssemblyStatement",
            language=language,
            flags=flags,
            body=self.visitAssemblyBlock(ctx.assemblyBlock()),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyBlock(self, ctx: SP.AssemblyBlockContext) -> AssemblyBlock:
        operations = [self.visitAssemblyItem(item) for item in ctx.assemblyItem()]

        node = AssemblyBlock(
            type="AssemblyBlock",
            operations=operations,
        )

        return self._add_meta(node, ctx)

    def visitAssemblyItem(
        self, ctx: SP.AssemblyItemContext
    ) -> Union[
        HexLiteral, StringLiteral, Break, Continue, AssemblyItem
    ]:
        text = None

        if ctx.hexLiteral():
            return self.visitHexLiteral(ctx.hexLiteral())

        if ctx.stringLiteral():
            text = self._toText(ctx.stringLiteral())
            value = text[1:-1]
            node = StringLiteral(
                type="StringLiteral",
                value=value,
                parts=[value],
                isUnicode=[
                    False
                ],  # assembly doesn"t seem to support unicode literals right now
            )

            return self._add_meta(node, ctx)

        if ctx.BreakKeyword():
            node = Break(
                type="Break",
            )

            return self._add_meta(node, ctx)

        if ctx.ContinueKeyword():
            node = Continue(
                type="Continue",
            )

            return self._add_meta(node, ctx)

        return self.visit(ctx.getChild(0))

    def visitAssemblyExpression(
        self, ctx: SP.AssemblyExpressionContext
    ) -> AssemblyExpression:
        return self.visit(ctx.getChild(0))

    def visitAssemblyCall(self, ctx: SP.AssemblyCallContext) -> AssemblyCall:
        functionName = self._toText(ctx.getChild(0))
        args = [
            self.visitAssemblyExpression(assemblyExpr)
            for assemblyExpr in ctx.assemblyExpression()
        ]

        node = AssemblyCall(
            type="AssemblyCall",
            functionName=functionName,
            arguments=args,
        )

        return self._add_meta(node, ctx)

    def visitAssemblyLiteral(
        self, ctx: SP.AssemblyLiteralContext
    ) -> Union[
        StringLiteral,
        BooleanLiteral,
        DecimalNumber,
        HexNumber,
        HexLiteral,
    ]:
        text = None

        if ctx.stringLiteral():
            text = self._toText(ctx)
            value = text[1:-1]
            node = StringLiteral(
                type="StringLiteral",
                value=value,
                parts=[value],
                isUnicode=[
                    False
                ],  # assembly doesn"t seem to support unicode literals right now
            )

            return self._add_meta(node, ctx)

        if ctx.BooleanLiteral():
            node = BooleanLiteral(
                type="BooleanLiteral",
                value=self._toText(ctx.BooleanLiteral()) == "true",
            )

            return self._add_meta(node, ctx)

        if ctx.DecimalNumber():
            node = DecimalNumber(
                type="DecimalNumber",
                value=self._toText(ctx),
            )

            return self._add_meta(node, ctx)

        if ctx.HexNumber():
            node = HexNumber(
                type="HexNumber",
                value=self._toText(ctx),
            )

            return self._add_meta(node, ctx)

        if ctx.hexLiteral():
            return self.visitHexLiteral(ctx.hexLiteral())

        raise ValueError("Should never reach here")

    def visitAssemblySwitch(self, ctx: SP.AssemblySwitchContext) -> AssemblySwitch:
        node = AssemblySwitch(
            type="AssemblySwitch",
            expression=self.visitAssemblyExpression(ctx.assemblyExpression()),
            cases=[self.visitAssemblyCase(c) for c in ctx.assemblyCase()],
        )

        return self._add_meta(node, ctx)

    def visitAssemblyCase(self, ctx: SP.AssemblyCaseContext) -> AssemblyCase:
        value = None
        if self._toText(ctx.getChild(0)) == "case":
            value = self.visitAssemblyLiteral(ctx.assemblyLiteral())

        node = AssemblyCase(
            type="AssemblyCase",
            block=self.visitAssemblyBlock(ctx.assemblyBlock()),
            value=value,
            default=(value is None),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyLocalDefinition(
        self, ctx: SP.AssemblyLocalDefinitionContext
    ) -> AssemblyLocalDefinition:
        ctxAssemblyIdentifierOrList = ctx.assemblyIdentifierOrList()
        if ctxAssemblyIdentifierOrList.identifier():
            names = [self.visitIdentifier(ctxAssemblyIdentifierOrList.identifier())]
        elif ctxAssemblyIdentifierOrList.assemblyMember():
            names = [
                self.visitAssemblyMember(ctxAssemblyIdentifierOrList.assemblyMember())
            ]
        else:
            names = [
                self.visitIdentifier(x)
                for x in ctxAssemblyIdentifierOrList.assemblyIdentifierList().identifier()
            ]

        expression = None
        if ctx.assemblyExpression() is not None:
            expression = self.visitAssemblyExpression(ctx.assemblyExpression())

        node = AssemblyLocalDefinition(
            type="AssemblyLocalDefinition",
            names=names,
            expression=expression,
        )

        return self._add_meta(node, ctx)

    def visitAssemblyFunctionDefinition(
        self, ctx: SP.AssemblyFunctionDefinitionContext
    ):
        ctxAssemblyIdentifierList = ctx.assemblyIdentifierList()
        args = (
            [self.visitIdentifier(x) for x in ctxAssemblyIdentifierList.identifier()]
            if ctxAssemblyIdentifierList
            else []
        )

        ctxAssemblyFunctionReturns = ctx.assemblyFunctionReturns()
        returnArgs = (
            [
                self.visitIdentifier(x)
                for x in ctxAssemblyFunctionReturns.assemblyIdentifierList().identifier()
            ]
            if ctxAssemblyFunctionReturns
            else []
        )

        node = AssemblyFunctionDefinition(
            type="AssemblyFunctionDefinition",
            name=self._toText(ctx.identifier()),
            arguments=args,
            returnArguments=returnArgs,
            body=self.visitAssemblyBlock(ctx.assemblyBlock()),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyAssignment(self, ctx: SP.AssemblyAssignmentContext):
        ctxAssemblyIdentifierOrList = ctx.assemblyIdentifierOrList()
        if ctxAssemblyIdentifierOrList.identifier():
            names = [self.visitIdentifier(ctxAssemblyIdentifierOrList.identifier())]
        elif ctxAssemblyIdentifierOrList.assemblyMember():
            names = [
                self.visitAssemblyMember(ctxAssemblyIdentifierOrList.assemblyMember())
            ]
        else:
            names = [
                self.visitIdentifier(x)
                for x in ctxAssemblyIdentifierOrList.assemblyIdentifierList().identifier()
            ]

        node = AssemblyAssignment(
            type="AssemblyAssignment",
            names=names,
            expression=self.visitAssemblyExpression(ctx.assemblyExpression()),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyMember(
        self, ctx: SP.AssemblyMemberContext
    ) -> AssemblyMemberAccess:
        accessed, member = ctx.identifier()
        node = AssemblyMemberAccess(
            type="AssemblyMemberAccess",
            expression=self.visitIdentifier(accessed),
            memberName=self.visitIdentifier(member),
        )

        return self._add_meta(node, ctx)

    def visitLabelDefinition(self, ctx: SP.LabelDefinitionContext):
        node = LabelDefinition(
            type="LabelDefinition",
            name=self._toText(ctx.identifier()),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyStackAssignment(self, ctx: SP.AssemblyStackAssignmentContext):
        node = AssemblyStackAssignment(
            type="AssemblyStackAssignment",
            name=self._toText(ctx.identifier()),
            expression=self.visitAssemblyExpression(ctx.assemblyExpression()),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyFor(self, ctx: SP.AssemblyForContext):
        node = AssemblyFor(
            type="AssemblyFor",
            pre=self.visit(ctx.getChild(1)),
            condition=self.visit(ctx.getChild(2)),
            post=self.visit(ctx.getChild(3)),
            body=self.visit(ctx.getChild(4)),
        )

        return self._add_meta(node, ctx)

    def visitAssemblyIf(self, ctx: SP.AssemblyIfContext):
        node = AssemblyIf(
            type="AssemblyIf",
            condition=self.visitAssemblyExpression(ctx.assemblyExpression()),
            body=self.visitAssemblyBlock(ctx.assemblyBlock()),
        )

        return self._add_meta(node, ctx)

    def visitContinueStatement(
        self, ctx: SP.ContinueStatementContext
    ) -> ContinueStatement:
        node = ContinueStatement(
            type="ContinueStatement",
        )

        return self._add_meta(node, ctx)

    def visitBreakStatement(self, ctx: SP.BreakStatementContext) -> BreakStatement:
        node = BreakStatement(
            type="BreakStatement",
        )

        return self._add_meta(node, ctx)

    def _toText(self, ctx: ParserRuleContext or ParseTree) -> str:
        text = ctx.getText()
        if text is None:
            raise ValueError("Assertion error: text should never be undefined")

        return text

    def _stateMutabilityToText(
        self, ctx: SP.StateMutabilityContext
    ) -> FunctionDefinition:
        if ctx.PureKeyword() is not None:
            return "pure"
        if ctx.ConstantKeyword() is not None:
            return "constant"
        if ctx.PayableKeyword() is not None:
            return "payable"
        if ctx.ViewKeyword() is not None:
            return "view"

        raise ValueError("Assertion error: non-exhaustive stateMutability check")

    def _loc(self, ctx) -> Location:
        start_line = ctx.start.line
        start_column = ctx.start.column
        end_line = ctx.stop.line if ctx.stop else start_line
        end_column = ctx.stop.column if ctx.stop else start_column

        source_location = Location(
            start=(start_line, start_column), end=(end_line, end_column)
        )

        return source_location

    def _range(self, ctx) -> Tuple[int, int]:
        return Range(ctx.start.start, ctx.stop.stop)

    def _add_meta(
        self, node: Union[BaseASTNode, NameValueList], ctx
    ) -> Union[BaseASTNode, NameValueList]:
        # node_with_meta = {"type": node.type}

        if self._options.loc:
            node.add_loc(self._loc(ctx))

        if self._options.range:
            node.add_range(self._range(ctx))

        return node

    def _map_commas_to_nulls(
        self, children: List[Optional[ParseTree]]
    ) -> List[Optional[ParseTree]]:
        if len(children) == 0:
            return []

        values = []
        comma = True

        for el in children:
            if comma:
                if self._to_text(el) == ",":
                    values.append(None)
                else:
                    values.append(el)
                    comma = False
            else:
                if self._to_text(el) != ",":
                    raise ValueError("expected comma")
                comma = True

        if comma:
            values.append(None)

        return values
