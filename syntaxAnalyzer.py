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


# compilationEngine.compileClass()
# compilationEngine.testCompile()
symbolTable = SymbolTable()
symbolTable.define("good", "int", "ARGUMENT")
symbolTable.define("game", "int", "FIELD")
symbolTable.define("beep", "int", "ARGUMENT")

print("class table pre-reset:", symbolTable.classTable)
print("subroutine table pre-reset:", symbolTable.subroutineTable)
print(symbolTable.typeOf("beep"), symbolTable.kindOf("beep"), symbolTable.indexOf("beep"))
print(symbolTable.typeOf("game"), symbolTable.kindOf("game"), symbolTable.indexOf("game"))
print(symbolTable.typeOf("good"), symbolTable.kindOf("good"), symbolTable.indexOf("good"))

symbolTable.startSubroutine()
print("class table post-reset:", symbolTable.classTable)
print("subroutine table post-reset:", symbolTable.subroutineTable)
