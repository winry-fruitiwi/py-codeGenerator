"""
The main file, where I make JackTokenizers and CompilationEngines!

Files I've tested with the current version of code:
    10/Square/Main.jack
    10/Square/Square.jack
    10/Square/SquareGame.jack

"""

from compilationEngine import *
from TokenType import *
from SymbolTable import *
from VMWriter import *

# the root of all files I'll need to test here.
file_root = "10/Square/"

# compilationEngine = CompilationEngine(file_root + "Square.jack")


def mainLoop(ce):
    outputXML = open("test.xml", "w")
    outputXML.write("<tokens>\n")

    # while there are still more tokens, print out the tokenizer's current character
    # and advance the current letter.
    while ce.tokenizer.hasMoreTokens():
        # get the current token of the tokenizer.
        current_token = ce.tokenizer.current_token

        # use a match-case statement to check for possible lexical elements for the
        # compilation engine to compile
        match current_token:
            case "while":
                print(current_token)
                ce.compileWhileStatement()
                continue

        # advance the current character.
        ce.tokenizer.advance()

        # get the token type of the tokenizer.
        token_type = ce.tokenizer.tokenType()

        # there are several value that token_type can take on. I used match-case
        # statements here. Depending on the value that token_type takes on, I'll
        # add a tag describing it appropriately.
        match token_type:
            case TokenType.STRING_CONST:
                outputXML.write(
                    f"<stringConstant> {ce.tokenizer.stringVal()} </stringConstant>\n")

            case TokenType.INT_CONST:
                outputXML.write(
                    f"<integerConstant> {ce.tokenizer.intVal()} </integerConstant>\n")

            case TokenType.SYMBOL:
                outputXML.write(
                    f"<symbol> {ce.tokenizer.symbol()} </symbol>\n")

            case TokenType.KEYWORD:
                outputXML.write(
                    f"<keyword> {ce.tokenizer.keyword()} </keyword>\n")

            case TokenType.IDENTIFIER:
                outputXML.write(
                    f"<identifier> {ce.tokenizer.identifier()} </identifier>\n")

        print("\n")

    outputXML.write("</tokens>")


def symbolTableTest():
    sT = SymbolTable()
    sT.define("have", "ARGUMENT", "int")
    sT.define("some", "FIELD", "int")
    sT.define("good", "FIELD", "int")
    sT.define("game", "ARGUMENT", "int")

    print("class table pre-reset:", sT.classTable)
    print("subroutine table pre-reset:", sT.subroutineTable)
    print(sT.typeOf("have"), sT.kindOf("have"),
          sT.indexOf("have"))
    print(sT.typeOf("some"), sT.kindOf("some"),
          sT.indexOf("some"))
    print(sT.typeOf("good"), sT.kindOf("good"),
          sT.indexOf("good"))
    print(sT.typeOf("game"), sT.kindOf("game"),
          sT.indexOf("game"))

    sT.startSubroutine()
    print("class table post-reset:", sT.classTable)
    print("subroutine table post-reset:", sT.subroutineTable)


# compilationEngine.compileClass()
# compilationEngine.testCompile()
VMWriter = VMWriter()
VMWriter.writePush("argument", 2)
VMWriter.writePop("this", 0)
VMWriter.writeArithmetic("add")
VMWriter.writeLabel("L1")
VMWriter.writeGoto("L3")
VMWriter.writeIf("L2")
VMWriter.writeCall("Keyboard.keyPressed", 0)
