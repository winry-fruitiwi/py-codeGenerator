# The main file, where I make JackTokenizers and CompilationEngines!

from compilationEngine import *
from TokenType import *
from symbolTable import *
from VMWriter import *
import os

# the root of all files I'll need to test here.
file_root = "11/ConvertToBin/"

# compilationEngine = CompilationEngine(file_root + "Main.jack")

# find the path and create a list of all the files.
path = "11/Pong/"
dir_list = os.listdir(path)
print(dir_list)

print()

# for every jack file in dir_list, compile it!
for file in dir_list:
    # split the file by . and check if the file extension is jack.
    splitFile = file.split(".")
    if splitFile[-1] != "jack":
        continue

    print("\n" + path + file)
    compilationEngine = CompilationEngine(path, file)
    compilationEngine.compileClass()


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
    # initialize symbol table
    sT = SymbolTable()

    # populate symbol table with values
    sT.define("have", "ARGUMENT", "int")
    sT.define("some", "FIELD", "int")
    sT.define("good", "FIELD", "int")
    sT.define("game", "ARGUMENT", "int")

    # print all variable names' name, type, kind, and index. name is hardcoded
    print("class table pre-reset:", sT.classTable)
    print("subroutine table pre-reset:", sT.subroutineTable)
    print("some:", sT.typeOf("have"), sT.kindOf("have"), sT.indexOf("have"))
    print("have:", sT.typeOf("some"), sT.kindOf("some"), sT.indexOf("some"))
    print("good:", sT.typeOf("good"), sT.kindOf("good"), sT.indexOf("good"))
    print("game:", sT.typeOf("game"), sT.kindOf("game"), sT.indexOf("game"))

    # start a new subroutine and make sure that only the subroutine table is
    # reset to default state of empty dictionary
    sT.startSubroutine()
    print("class table post-reset:", sT.classTable)
    print("subroutine table post-reset:", sT.subroutineTable)


def VMWriterTest():
    # initialize the VMWriter
    vm_writer = VMWriter("output.vm")

    # use VMWriter to write to output.vm. I just tested this random sequence of
    # statements without thinking about its effects, but it will be an infinite
    # loop!
    vm_writer.writeFunction("KB.keyPressed", 0)
    vm_writer.writePush("argument", 2)
    vm_writer.writePop("this", 0)
    vm_writer.writeArithmetic("add")
    vm_writer.writeLabel("L1")
    vm_writer.writeGoto("L1")
    vm_writer.writeIf("L2")
    vm_writer.writeCall("Keyboard.keyPressed", 0)
    vm_writer.writeReturn()

    # close the file
    vm_writer.close()


# compilationEngine.compileClass()
# compilationEngine.testCompile()
# print("subroutine table: ", compilationEngine.st.subroutineTable)
# print("class table0: ", compilationEngine.st.classTable)
