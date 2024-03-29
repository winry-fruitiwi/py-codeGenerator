from jackTokenizer import *
from symbolTable import *
from VMWriter import *


class CompilationEngine:
    def __init__(self, path, file):
        self.path = path
        self.vmw = None
        self.currentClassName = None
        self.tokenizer = JackTokenizer(path + file)
        self.output = open("test.xml", "w")

        # signals to eat() if we need to skip advance()
        self.skip_advance = False

        # the number of indents before each line
        self.indents = 0

        # a symbol table instance
        self.st = SymbolTable()

        # the number of times I've created a label in an if statement
        self.numLabels = -1

        # the labels that currently need to be written
        self.labelsToBeWritten = []

        # the number of fields
        self.numFields = 0

        # the current line
        self.currentLine = self.tokenizer.stripped_lines[self.tokenizer.current_line_index]

    # compiles a complete class. This needs to be called immediately after
    # an instance is initialized.
    def compileClass(self):
        self.writeToOutput("<class>\n")
        self.indent()

        # eat class
        self.eat("class")

        # advance
        self.advance()
        self.skip_advance = True

        # create the current class name
        self.currentClassName = self.tokenizer.current_token

        # an instance of a VM writer
        self.vmw = VMWriter(self.path + self.currentClassName)

        # compile an identifier
        self.compileIdentifier(False)

        # eat {
        self.eat("{")

        # advance
        self.advance()
        self.skip_advance = True

        # compile class variable declarations
        while self.tokenizer.current_token in ["static", "field"]:
            self.compileClassVarDec()
            self.advance()
            self.skip_advance = True

        # compile a subroutine declaration.
        while self.tokenizer.current_token in ["constructor", "function",
                                               "method"]:
            print("subroutine table: ", self.st.subroutineTable)
            self.st.startSubroutine()

            self.compileSubRoutineDec()
            self.advance()
            self.skip_advance = True

        # eat }
        self.eat("}")

        self.dedent()
        self.writeToOutput("</class>\n")

    # compiles a static variable or a field declaration.
    def compileClassVarDec(self):
        self.writeToOutput("<classVarDec>\n")
        self.indent()

        # eat either static or field
        if not self.skip_advance:
            self.advance()
        self.skip_advance = True

        ifField = False
        numFields = 0

        if self.tokenizer.current_token == "static":
            self.eat("static")
            currentKind = "STATIC"
        else:
            self.eat("field")
            currentKind = "FIELD"
            ifField = True
            numFields = 1

        # advance
        self.advance()
        self.skip_advance = True

        # compile a type
        currentType = self.tokenizer.current_token
        self.compileType()

        # compile an identifier
        self.advance()
        self.skip_advance = True
        self.st.define(self.tokenizer.current_token, currentKind, currentType)
        self.compileIdentifier(False)

        # advance
        self.advance()
        self.skip_advance = True

        # while the next token is a comma, eat a comma and compile an identifier
        while self.tokenizer.current_token == ",":
            if ifField:
                numFields += 1

            # eat a comma
            self.eat(",")

            # advance and define a new variable. then, compile an identifier
            self.advance()
            self.skip_advance = True
            self.st.define(self.tokenizer.current_token, currentKind,
                           currentType)
            self.compileIdentifier(False)

            self.advance()
            self.skip_advance = True
        self.eat(";")

        self.dedent()
        self.writeToOutput("</classVarDec>\n")

        self.numFields += numFields

    # compiles the inside of a subroutine declaration
    def compileSubRoutineBody(self, functionName, ifConstructor, ifMethod):
        self.writeToOutput("<subroutineBody>\n")
        self.indent()

        # eat {
        self.eat("{")

        # advance
        self.advance()
        self.skip_advance = True

        # the total number of local variables found
        totalNumVars = 0

        # while the current token is var, compile varDec
        while self.tokenizer.current_token == "var":
            totalNumVars += self.compileVarDec()
            self.advance()
            self.skip_advance = True

        # write a function call
        self.vmw.writeFunction(
            self.currentClassName + "." + functionName, totalNumVars)

        # if ifConstructor is true, call Memory.alloc with 1 argument
        if ifConstructor:
            self.vmw.writePush("constant", self.numFields)
            self.vmw.writeCall("Memory.alloc", 1)
            self.vmw.writePop("pointer", 0)

        if ifMethod:
            self.vmw.writePush("argument", 0)
            self.vmw.writePop("pointer", 0)

        # compile statements
        self.compileStatements()

        # eat }
        self.eat("}")

        self.dedent()
        self.writeToOutput("</subroutineBody>\n")

    # compiles a complete method, function, or constructor.
    def compileSubRoutineDec(self):
        self.writeToOutput("<subroutineDec>\n")
        self.indent()

        # advance, then check for either constructor, function, or method
        if not self.skip_advance:
            self.advance()
        self.skip_advance = True

        ifConstructor = False
        ifMethod = False

        match self.tokenizer.current_token:
            case "constructor":
                ifConstructor = True
                self.eat("constructor")
            case "function":
                self.eat("function")
            case "method":
                self.eat("method")
                self.st.define(self.currentClassName, "argument", self.currentClassName)
                ifMethod = True

        # advance, then check for void or type
        self.advance()
        self.skip_advance = True

        if self.tokenizer.current_token == "void":
            self.eat("void")
        else:
            self.compileType()

        # advance, then write call statement with current name
        self.advance()
        self.skip_advance = True

        functionName = self.tokenizer.current_token

        # compile an identifier
        self.compileIdentifier(False)

        # eat (
        self.eat("(")

        # compile parameterList
        self.compileParameterList()

        # eat )
        self.eat(")")

        # compile subRoutineBody. for now, this can just be a compile statement
        # for statements in brackets.
        self.compileSubRoutineBody(functionName, ifConstructor, ifMethod)

        self.dedent()
        self.writeToOutput("</subroutineDec>\n")

    # compilers a parameter list. doesn't handle enclosing parentheses.
    def compileParameterList(self):
        self.writeToOutput("<parameterList>\n")
        self.indent()

        self.advance()
        self.skip_advance = True
        if (self.tokenizer.current_token in ["int", "char", "boolean"] or
                self.tokenizer.tokenType() == TokenType.IDENTIFIER):
            # compile type
            currentType = self.tokenizer.current_token
            self.compileType()

            # compile identifier
            self.advance()
            self.skip_advance = True
            self.st.define(self.tokenizer.current_token, "ARGUMENT",
                           currentType)
            self.compileIdentifier(False)

            # advance
            self.advance()
            self.skip_advance = True

            # while the token is a comma, eat it, compile type and identifier,
            # then advance.
            while self.tokenizer.current_token == ",":
                # eat a comma
                self.eat(",")

                # advance, then set currentType to the current token
                self.advance()
                self.skip_advance = True
                currentType = self.tokenizer.current_token

                # compile type
                self.compileType()

                # advance, then define a new variable with the current token
                # (name), "ARGUMENT" (kind), and currentType (type).
                self.advance()
                self.skip_advance = True
                self.st.define(self.tokenizer.current_token, "ARGUMENT",
                               currentType)

                # compile identifier
                self.compileIdentifier(False)

                # advance to prepare for the next iteration
                self.advance()
                self.skip_advance = True

        self.dedent()
        self.writeToOutput("</parameterList>\n")

    # compiles a variable declaration. grammar: var type varName(,varName)*;
    def compileVarDec(self):
        self.writeToOutput("<varDec>\n")
        self.indent()

        """
        <varDec>
            <keyword> var </keyword>
            <identifier> SquareGame </identifier>
            <identifier> game </identifier>
            <symbol> ; </symbol>
        </varDec>
            :return:
        """

        # eat var
        self.eat("var")

        # keeps track of the number of expressions I've encountered
        numExpressions = 1

        # advance
        self.advance()
        # print(self.tokenizer.current_token)
        currentType = self.tokenizer.current_token
        self.skip_advance = True

        # compile a type
        self.compileType()

        # compile an identifier
        self.advance()
        self.skip_advance = True
        self.st.define(self.tokenizer.current_token, "LOCAL", currentType)
        self.compileIdentifier(False)

        # advance
        self.advance()
        self.skip_advance = True

        # while the next token is a comma, eat a comma and compile an identifier
        while self.tokenizer.current_token == ",":
            numExpressions += 1
            self.eat(",")
            self.advance()
            self.skip_advance = True
            self.st.define(self.tokenizer.current_token, "LOCAL", currentType)
            self.compileIdentifier(False)

            self.advance()
            self.skip_advance = True
        self.eat(";")

        self.dedent()
        self.writeToOutput("</varDec>\n")

        return numExpressions

    # compiles a sequence of statements. doesn't handle enclosing {}s. grammar:
    # statement*
    def compileStatements(self):
        self.writeToOutput("<statements>\n")
        self.indent()

        # advance
        if not self.skip_advance:
            self.advance()
        self.skip_advance = True

        # while the current token is do, while, if, let, or return, call
        # compileStatement
        while self.tokenizer.current_token in ["while", "do", "if", "let",
                                               "return"]:
            self.compileStatement()

            if not self.skip_advance:
                self.advance()
            self.skip_advance = True

        self.dedent()
        self.writeToOutput("</statements>\n")

    # compiles a sequence of statements inside curly brackets
    def compileStatementsInBrackets(self):
        self.eat("{")
        self.compileStatements()
        self.eat("}")

    # helper functions!

    # compiles a type
    def compileType(self):
        # eat int, char, boolean, or an identifier
        match self.tokenizer.current_token:
            case "int":
                self.eat("int")
                return
            case "char":
                self.eat("char")
                return
            case "boolean":
                self.eat("boolean")
                return
        if self.tokenizer.tokenType() == TokenType.IDENTIFIER:
            self.compileIdentifier(False)

        pass

    # compiles a single statement. A helper function for compile_statements.
    # grammar: letStatement|ifStatement|whileStatement|doStatement|returnStatement
    def compileStatement(self):
        # match-case for do, while, return, let, and if statements
        # for each case, compile the respective statement.

        match self.tokenizer.current_token:
            case "do":
                self.compileDoStatement()
            case "if":
                self.compileIfStatement()
            case "while":
                self.compileWhileStatement()
            case "let":
                self.compileLetStatement()
            case "return":
                self.compileReturnStatement()

    # compiles a let statement. grammar: let varName([expression])?=expression;
    def compileLetStatement(self):
        """
        <letStatement>
          <keyword> let </keyword>
          <identifier> game </identifier>
          <symbol> = </symbol>
          <expression>
            <term>
              <identifier> game </identifier>
            </term>
          </expression>
          <symbol> ; </symbol>
        </letStatement>

        :return:
        """
        # add opening tag
        self.writeToOutput("<letStatement>\n")
        self.indent()

        # a flag for if I have to assign the expression's value to a list index
        listIndexFound = False

        # eat let
        self.eat("let")

        # advance and find the name of the current identifier
        self.advance()
        self.skip_advance = True
        name = self.tokenizer.current_token

        # self.vmw.writeComment(name)

        # compile an identifier
        self.compileIdentifier(False)

        # advance and check for a bracket. If there is one, eat [, compile
        # expression, and then eat ]. If not, continue.
        self.advance()
        self.skip_advance = True
        if self.tokenizer.current_token == "[":
            self.eat("[")
            self.compileExpression()
            self.eat("]")

            self.vmw.writePush(self.st.kindOf(name),
                               self.st.indexOf(name))
            self.vmw.writeArithmetic("add")

            listIndexFound = True

        # eat =
        self.eat("=")

        # compile expression
        self.compileExpression()

        # eat ;
        self.eat(";")

        self.dedent()
        self.writeToOutput("</letStatement>\n")

        if listIndexFound:
            self.vmw.writePop("temp", 0)
            self.vmw.writePop("pointer", 1)
            self.vmw.writePush("temp", 0)
            self.vmw.writePop("that", 0)

        else:
            # write a pop statement for the kind of the name
            self.vmw.writePop(self.st.kindOf(name), self.st.indexOf(name))

    # compiles an if statement. grammar: if (expression){statement} (else
    # {statements})?
    def compileIfStatement(self):
        """
        <ifStatement>
          <keyword> if </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <identifier> b </identifier>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
          </statements>
          <symbol> } </symbol>
          <keyword> else </keyword>
          <symbol> { </symbol>
          <statements>
          </statements>
          <symbol> } </symbol>
        </ifStatement>

        :return:
        """

        self.vmw.writeComment("if found")

        # write opening tag, eat if
        self.writeToOutput("<ifStatement>\n")
        self.indent()

        self.eat("if")

        self.numLabels += 1

        numLabels = self.numLabels

        # eat expression in parens, then goto beginning of if statement if
        # condition is true. Otherwise, goto the end.
        self.compileExprInParens()
        self.vmw.writeIf(f"IF_TRUE{numLabels}")
        self.vmw.writeGoto(f"IF_FALSE{numLabels}")
        self.vmw.writeLabel(f"IF_TRUE{numLabels}")
        self.labelsToBeWritten.append(numLabels)
        self.labelsToBeWritten.append(numLabels)

        # eat statement in brackets
        self.eat("{")
        self.compileStatements()
        self.eat("}")

        # advance the tokenizer, then check if the current token is else. if
        # it is, then eat else and {statements}.
        self.advance()
        self.skip_advance = True
        if self.tokenizer.current_token == "else":
            # after statements is done, goto the end of the if statement
            self.vmw.writeGoto(f"IF_END{self.labelsToBeWritten.pop()}")
            self.vmw.writeLabel(f"IF_FALSE{self.labelsToBeWritten.pop()}")
            self.labelsToBeWritten.append(numLabels)

            self.eat("else")
            self.compileStatementsInBrackets()
            self.vmw.writeLabel(f"IF_END{self.labelsToBeWritten.pop()}")

        else:
            self.vmw.writeLabel(f"IF_FALSE{self.labelsToBeWritten.pop()}")
            self.labelsToBeWritten.pop()


        # write ending tag to output
        self.dedent()
        self.writeToOutput("</ifStatement>\n")
        # print("after an if statement: ", self.tokenizer.current_token)

    # compiles a while statement. grammar: while (expression) {statements}
    def compileWhileStatement(self):
        """
        <whileStatement>
          <keyword> while </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <identifier> key </identifier>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
            <letStatement>
              <keyword> let </keyword>
              <identifier> key </identifier>
              <symbol> = </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
              </expression>
              <symbol> ; </symbol>
            </letStatement>
            <doStatement>
              <keyword> do </keyword>
              <identifier> moveSquare </identifier>
              <symbol> ( </symbol>
              <expressionList>
              </expressionList>
              <symbol> ) </symbol>
              <symbol> ; </symbol>
            </doStatement>
          </statements>
          <symbol> } </symbol>
        </whileStatement>

        :return:
        """
        self.numLabels += 1

        # while + write to output
        self.writeToOutput("<whileStatement>\n")
        self.indent()

        self.eat("while")

        # compile (expression)
        self.vmw.writeLabel("WHILE_EXP" + str(self.numLabels))
        self.compileExprInParens()
        self.vmw.writeArithmetic("not")
        self.vmw.writeIf("WHILE_END" + str(self.numLabels))

        # compile {statements}
        self.labelsToBeWritten.append(f"WHILE_END{str(self.numLabels)}")
        self.labelsToBeWritten.append(f"WHILE_EXP{str(self.numLabels)}")
        self.compileStatementsInBrackets()
        self.vmw.writeGoto(self.labelsToBeWritten.pop())
        self.vmw.writeLabel(self.labelsToBeWritten.pop())

        # write closing tag
        self.dedent()
        self.writeToOutput("</whileStatement>\n")

    # compiles a do statement. grammar: do subRoutineCall;
    def compileDoStatement(self):
        """
        <doStatement>
          <keyword> do </keyword>
          <identifier> moveSquare </identifier>
          <symbol> ( </symbol>
          <expressionList>
          </expressionList>
          <symbol> ) </symbol>
          <symbol> ; </symbol>
        </doStatement>

        :return:
        """

        # eat do
        self.writeToOutput("<doStatement>\n")
        self.indent()

        self.eat("do")

        # compile subRoutineCall
        self.compileSubRoutineCall()

        # eat ;
        self.eat(";")

        # ending tag
        self.dedent()
        self.writeToOutput("</doStatement>\n")

        # we know there was no value to be saved, so we should just dump the
        # current value on the stack.
        self.vmw.writePop("temp", "0")

    # compiles a return statement. grammar: return expression?;
    def compileReturnStatement(self):
        # eat return
        self.writeToOutput("<returnStatement>\n")
        self.indent()

        self.eat("return")

        # advance, set skip_advance to true
        self.advance()
        self.skip_advance = True

        # if the current token is a term, compile expression
        if (self.tokenizer.tokenType() == TokenType.IDENTIFIER or
                self.tokenizer.tokenType() == TokenType.STRING_CONST or
                self.tokenizer.tokenType() == TokenType.INT_CONST or
                self.tokenizer.current_token == "this"):
            self.compileExpression()

        # otherwise, then we know that there's no new value pushed onto the
        # stack, so we can write "push constant 0"
        else:
            self.vmw.writePush("constant", 0)

        # no matter what happened previously, eat ";"
        self.eat(";")

        # write return
        self.vmw.writeReturn()

        # write output tag
        self.dedent()
        self.writeToOutput("</returnStatement>\n")

    # compiles an expression. grammar: term (op term)*
    def compileExpression(self):
        self.writeToOutput("<expression>\n")
        self.indent()

        self.compileTerm()

        # advance
        if not self.skip_advance:
            self.advance()
        self.skip_advance = True
        # print(self.tokenizer.current_token)

        # if the current token is in the list [+, -, *, /, &, |, <, >, =], eat
        # a symbol and a term. keep track of the command and add it to the end
        # of the file later on
        currentCommands = []
        while self.tokenizer.current_token in ['+', '-', '*', '/', '&', '|',
                                               '<', '>', '=']:
            match self.tokenizer.current_token:
                case '+':
                    currentCommands.append("add")

                case '-':
                    currentCommands.append("sub")

                case '*':
                    currentCommands.append("mul")

                case '/':
                    currentCommands.append("div")

                case '&':
                    currentCommands.append("and")

                case '|':
                    currentCommands.append("or")

                case '<':
                    currentCommands.append("lt")

                case '>':
                    currentCommands.append("gt")

                case '=':
                    currentCommands.append("eq")

            # print("hello!")
            self.compileSymbol()
            self.compileTerm()
            if not self.skip_advance:
                self.advance()
            self.skip_advance = True

        currentCommands = currentCommands[::-1]

        for command in currentCommands:
            if command == "mul":
                self.vmw.writeCall("Math.multiply", 2)

            elif command == "div":
                self.vmw.writeCall("Math.divide", 2)

            else:
                self.vmw.writeArithmetic(command)

        self.dedent()
        self.writeToOutput("</expression>\n")

    # compiles an expression within parentheses.
    def compileExprInParens(self):
        self.eat("(")
        self.compileExpression()
        self.eat(")")

    # compiles a term.
    def compileTerm(self):
        self.writeToOutput("<term>\n")
        self.indent()

        # advance
        if not self.skip_advance:
            self.advance()
        self.skip_advance = True

        # a flag for when I get a token type compiled
        compiledToken = False

        match self.tokenizer.tokenType():
            # if current token is a string constant, compile it
            case TokenType.STRING_CONST:
                self.compileStrConst()
                compiledToken = True

            # if the current token is an integer constant, compile it and return.
            case TokenType.INT_CONST:
                self.compileIntConst()
                compiledToken = True

            # if the type is a keyword, compile a keyword.
            case TokenType.KEYWORD:
                if self.tokenizer.current_token == "true":
                    self.vmw.writePush("constant", 0)
                    self.vmw.writeArithmetic("not")

                if self.tokenizer.current_token == "false":
                    self.vmw.writePush("constant", 0)

                if self.tokenizer.current_token == "this":
                    self.vmw.writePush("pointer", 0)

                if self.tokenizer.current_token == "null":
                    self.vmw.writePush("constant", 0)

                self.compileKeyword()
                compiledToken = True

            # if current token is an identifier, eat it
            case TokenType.IDENTIFIER:
                # prepare for a potential subroutine call
                current_name = self.tokenizer.current_token

                # print("identifier", self.tokenizer.current_token, "found")
                self.compileIdentifier(False)

                self.advance()
                self.skip_advance = True

                match self.tokenizer.current_token:
                    # if the next token is (, eat (, compile exprList, eat )
                    case "(":
                        self.eat("(")
                        numArgs = self.compileExpressionList()
                        self.eat(")")

                        self.vmw.writeCall(
                            self.currentClassName + "." + current_name,
                            numArgs + 1)

                        # self.vmw.writeComment(current_name)

                    # if the next token is [, eat [, compile expr, eat ]
                    case "[":
                        self.eat("[")
                        self.compileExpression()
                        self.eat("]")

                        self.vmw.writePush(self.st.kindOf(current_name),
                                           self.st.indexOf(current_name))
                        self.vmw.writeArithmetic("add")
                        self.vmw.writePop("pointer", 1)
                        self.vmw.writePush("that", 0)

                    # if the next token is a period, eat period, identifier, (, exprList, )
                    case ".":
                        numArgs = 0
                        # this is a subroutine call, so add a period and the
                        # next token to current_name, then write call statement
                        # with numArgs from compileExpressionList
                        if self.st.inTable(current_name):
                            numArgs += 1
                            self.vmw.writePush("this", self.st.indexOf(current_name))
                            current_name = self.st.typeOf(current_name)

                        current_name += "."
                        self.eat(".")

                        self.advance()
                        self.skip_advance = True
                        current_name += self.tokenizer.current_token
                        self.compileIdentifier(False)
                        self.eat("(")
                        numArgs += self.compileExpressionList()
                        self.eat(")")

                        self.vmw.writeCall(current_name, numArgs)

                    case _:
                        identifierSegment = self.st.kindOf(current_name)
                        identifierIndex = self.st.indexOf(current_name)
                        self.vmw.writePush(identifierSegment, identifierIndex)

                compiledToken = True

        if not compiledToken:
            # if the current token is a unary operator, eat it and call term().
            if self.tokenizer.current_token == "-":
                self.eat("-")
                self.compileTerm()
                self.vmw.writeArithmetic("neg")

            elif self.tokenizer.current_token == "~":
                self.eat("~")
                self.compileTerm()
                self.vmw.writeArithmetic("not")

                # if the current token is (, eat (, compile expr, eat )
            elif self.tokenizer.current_token == "(":
                self.eat("(")
                self.compileExpression()
                self.eat(")")

        # print("done")

        self.dedent()
        self.writeToOutput("</term>\n")

    # compiles a massively simplified version of compile_term
    def compileSimpleTerm(self):
        self.writeToOutput("<term>\n")
        self.indent()

        if not self.skip_advance:
            self.advance()
            self.skip_advance = True
        if self.tokenizer.current_token == "this":
            self.eat("this")

        else:
            self.compileIdentifier(True)

        self.dedent()
        self.writeToOutput("</term>\n")

    # compiles a comma-separated list of expressions. can be empty.
    def compileExpressionList(self):
        self.writeToOutput("<expressionList>\n")
        self.indent()

        if not self.skip_advance:
            self.advance()
            self.skip_advance = True
        else:
            self.skip_advance = False

        # initialize a variable saying how many variables are in the expression
        numArgs = 0

        # if term's requirements are met:
        if self.tokenizer.current_token != ")":
            # compile an expression
            # print(self.tokenizer.current_token)
            self.compileExpression()

            # increment numArgs
            numArgs += 1

            # while commas are detected, eat a comma and then compile an
            # expression.
            if not self.skip_advance:
                self.advance()
            self.skip_advance = True
            while self.tokenizer.current_token == ",":
                numArgs += 1
                self.eat(",")
                self.compileExpression()
                if not self.skip_advance:
                    self.advance()
                self.skip_advance = True

        self.dedent()
        self.writeToOutput("</expressionList>\n")
        return numArgs

    # compiles an identifier. writePush is a boolean saying if we should write
    # a push statement inside compileIdentifier, as when we have to look ahead
    # before pushing onto the stack, we usually don't want to immediately push
    # an identifier onto the stack.
    def compileIdentifier(self, writePush):
        if not self.skip_advance:
            self.advance()
        else:
            self.skip_advance = False

        identifier = self.tokenizer.identifier()

        assert self.tokenizer.tokenType() == TokenType.IDENTIFIER

        try:
            identifierKind = self.st.kindOf(self.tokenizer.current_token)
            identifierType = self.st.typeOf(self.tokenizer.current_token)
            iKindAndType = identifierKind + identifierType
        except KeyError:
            iKindAndType = "identifier"

        self.writeToOutput(
            f"<{iKindAndType}> {self.tokenizer.identifier()} </{iKindAndType}>\n"
        )

        # self.vmw.writeComment(
        #     "Identifier name is " + self.tokenizer.identifier()
        # )

        if writePush:
            try:
                self.vmw.writePush(
                    self.st.kindOf(identifier), self.st.indexOf(identifier)
                )
            except KeyError:
                pass

    def compileStrConst(self):
        if not self.skip_advance:
            self.advance()
        else:
            self.skip_advance = False

        assert self.tokenizer.tokenType() == TokenType.STRING_CONST

        tokenizedString = self.tokenizer.stringVal()
        lenStr = len(tokenizedString)

        self.vmw.writePush("constant", lenStr)
        self.vmw.writeCall("String.new", 1)

        for char in tokenizedString:
            self.vmw.writePush("constant", ord(char))
            self.vmw.writeCall("String.appendChar", 2)

        self.writeToOutput(
            f"<stringConstant> {self.tokenizer.stringVal()} </stringConstant>\n")

    def compileIntConst(self):
        if not self.skip_advance:
            self.advance()
        else:
            self.skip_advance = False

        assert self.tokenizer.tokenType() == TokenType.INT_CONST

        self.vmw.writePush("constant", self.tokenizer.current_token)

        self.writeToOutput(
            f"<integerConstant> {self.tokenizer.intVal()} </integerConstant>\n")

    def compileKeyword(self):
        if not self.skip_advance:
            self.advance()
        else:
            self.skip_advance = False

        assert self.tokenizer.tokenType() == TokenType.KEYWORD

        self.writeToOutput(f"<keyword> {self.tokenizer.keyword()} </keyword>\n")

    def compileSymbol(self):
        if not self.skip_advance:
            self.advance()
        else:
            self.skip_advance = False

        assert self.tokenizer.tokenType() == TokenType.SYMBOL

        self.writeToOutput(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")

    # advances the tokenizer and checks if it's a delimiter or not a token.
    def advance(self):
        # advance the tokenizer.
        self.tokenizer.advance()

        # check if the tokenizer's and CE's current line is different.
        if self.tokenizer.currentLine != self.currentLine:
            self.vmw.writeComment(self.tokenizer.currentLine)
            self.currentLine = self.tokenizer.currentLine

        # get the token type of the tokenizer.
        token_type = self.tokenizer.tokenType()

        # if the token is the start of a line or a delimiter, advance again,
        # setting the token type again as well
        while token_type == "delimiter" or token_type == "Not a token.":
            self.tokenizer.advance()
            token_type = self.tokenizer.tokenType()
            # check if the tokenizer's and CE's current line is different.
            if self.tokenizer.currentLine != self.currentLine:
                self.vmw.writeComment(self.tokenizer.currentLine)
                self.currentLine = self.tokenizer.currentLine

    # asserts that the next token is its first argument. its second argument, a
    # boolean, determines whether to advance. We can sometimes not advance when
    # dealing with expressions.
    def eat(self, token):
        # advance the current character if second argument is true.
        if not self.skip_advance:
            self.advance()
        else:
            self.skip_advance = False

        token_type = self.tokenizer.tokenType()

        # there are several value that token_type can take on. I used match-case
        # statements here. Depending on the value that token_type takes on, I'll
        # add a tag describing it appropriately.
        match token_type:
            case TokenType.STRING_CONST:
                self.writeToOutput(
                    f"<stringConstant> {self.tokenizer.stringVal()} </stringConstant>\n")

            case TokenType.INT_CONST:
                self.writeToOutput(
                    f"<integerConstant> {self.tokenizer.intVal()} </integerConstant>\n")

            case TokenType.SYMBOL:
                self.writeToOutput(
                    f"<symbol> {self.tokenizer.symbol()} </symbol>\n")

            case TokenType.KEYWORD:
                self.writeToOutput(
                    f"<keyword> {self.tokenizer.keyword()} </keyword>\n")

            case TokenType.IDENTIFIER:
                self.writeToOutput(
                    f"<identifier> {self.tokenizer.identifier()} </identifier>\n")

        current_token = self.tokenizer.current_token
        assert token == current_token

    # a simple function that tests a single compile statement.
    def testCompile(self):
        self.compileTerm()

    # an unneeded subroutine call method for use in terms and do statements.
    def compileSubRoutineCall(self):
        # advance and make the name of the current subroutine
        if not self.skip_advance:
            self.advance()
        self.skip_advance = True

        currentSubName = self.tokenizer.current_token

        # keeps track of if we found the current token in the symbol table.
        subNameFoundInST = False

        # checks if the current subroutine call doesn't include className.
        classNameNotIncluded = False

        # if the subroutine name is in the table, that means it's a variable
        # name, and we can retrieve its properties.
        if self.st.inTable(currentSubName):
            typeOfSubName = self.st.typeOf(currentSubName)
            if self.st.kindOf(currentSubName) == "field":
                self.vmw.writePush("this", self.st.indexOf(currentSubName))

            else:
                self.vmw.writePush(self.st.kindOf(currentSubName),
                                   self.st.indexOf(currentSubName))
            currentSubName = typeOfSubName
            subNameFoundInST = True

        self.compileIdentifier(False)

        # if the next token is an open paren:
        self.advance()
        self.skip_advance = True

        if self.tokenizer.current_token == "(":
            self.vmw.writePush("pointer", 0)
            classNameNotIncluded = True

            # eat (
            self.eat("(")

            # compile an expression
            numArgs = self.compileExpressionList()

            # eat )
            self.eat(")")

        # otherwise, eat period, compile another identifier, eat (, eat an
        # expression list, and then eat ).
        else:
            # add . to currentSubName
            currentSubName += "."
            self.eat(".")

            # then add the subroutine name
            self.advance()
            self.skip_advance = True
            currentSubName += self.tokenizer.current_token
            self.compileIdentifier(False)
            self.eat("(")
            numArgs = self.compileExpressionList()
            self.eat(")")

        # if the class name is found in ST, numArgs += 1
        if subNameFoundInST:
            numArgs += 1

        # if the class name wasn't found, push pointer 0
        if classNameNotIncluded:
            self.vmw.writeCall(self.currentClassName + "." + currentSubName,
                               numArgs + 1)
        else:
            self.vmw.writeCall(currentSubName, numArgs)

    # increases self.indent
    def indent(self):
        self.indents += 1

    # decreases self.indent
    def dedent(self):
        self.indents -= 1

    # write to the output, taking into account number of indents
    def writeToOutput(self, string):
        self.output.write("  " * self.indents + string)
