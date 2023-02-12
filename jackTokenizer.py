from TokenType import *


class JackTokenizer:
    def __init__(self, path):
        # open the input file.
        self.current_token = None
        self.input_file = open(path).readlines()

        # a list of all the symbols in the jack language.
        self.symbols = [
            '{',
            '}',
            '(',
            ')',
            '[',
            ']',
            '.',
            ',',
            ';',
            '+',
            '-',
            '*',
            '/',
            '&',
            '|',
            '<',
            '>',
            '=',
            '~'
        ]

        # a list of all the keywords in the jack language.
        self.keywords = [
            'class',
            'constructor',
            'function',
            'class',
            'method',
            'field',
            'static',
            'method',
            'var',
            'int',
            'char',
            'boolean',
            'void',
            'true',
            'false',
            'null',
            'this',
            'let',
            'do',
            'if',
            'else',
            'while',
            'return'
        ]

        # a list from 0-9.
        self.digits = [
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9'
        ]

        # a list of the file's lines that will be stripped of whitespace, new
        # lines, full line comments, and inline comments.
        self.stripped_lines = []

        # a flag for when I've found a multi-line comment.
        in_multiline_comment = False

        for line in self.input_file:
            # strip the whitespace, then newlines and whitespace before the
            # newlines.
            stripped_line = line.strip("\t").strip(" ").strip("\n").strip(" ").strip("\t")

            if not in_multiline_comment:
                try:
                    # if the stripped line is an empty space, don't append it to
                    # the list of stripped lines.
                    if stripped_line == "":
                        continue

                    # if the stripped line starts with a //, it's a comment, so we
                    # don't append it to the list of stripped lines.
                    if stripped_line[0:2] == "//":
                        continue

                    try:
                        if stripped_line[0:3] == "/**":
                            in_multiline_comment = True

                        if stripped_line.index("*/"):
                            in_multiline_comment = False

                        continue
                    except ValueError:
                        if in_multiline_comment:
                            continue

                    # this is why there's a try-except block. index() returns a
                    # ValueError if the substring doesn't exist. in this block,
                    # I'm checking if there is a //, which signals the beginning
                    # of a comment no matter where it is.
                    if stripped_line.index("//"):
                        # if there is an index, then take a slice from 0 to the
                        # index.
                        stripped_line = stripped_line[0:stripped_line.index("//")]

                        # most inline comments will have whitespace between them
                        # and the code that they're explaining. We need to strip
                        # that.

                    # do the same for multiline comments.
                    stripped_line = stripped_line.strip(" ")
                    if stripped_line.index("/**"):

                        stripped_line = stripped_line[
                                        0:stripped_line.index("/**")]

                        stripped_line = stripped_line.strip(" ")

                        in_multiline_comment = True
                    if stripped_line[0:2] == "*/":
                        in_multiline_comment = False
                        continue
                    try:
                        if stripped_line.index("*/"):
                            stripped_line = stripped_line[
                                            stripped_line.index("*/"):]
                            stripped_line = stripped_line.strip(" ")
                            in_multiline_comment = False
                    except ValueError:
                        pass


                    # finally, if the stripped line is now just an empty line,
                    # signaling that this was a full-line comment, then we don't
                    # have to append the line to self.stripped_lines anymore.
                    if stripped_line == "":
                        continue

                # if there is no //, then a ValueError will be raised and the
                # except block will fire.
                except ValueError:
                    pass

                if stripped_line[-1] != '"':
                    self.stripped_lines.append(stripped_line + " ")
                else:
                    self.stripped_lines.append(stripped_line)

            else:
                if stripped_line[0:2] == "*/":
                    in_multiline_comment = False
                    continue
                try:
                    if stripped_line.index("*/"):
                        stripped_line = stripped_line[
                                        stripped_line.index("*/")+1:-2]

                        stripped_line = stripped_line.strip(" ")

                        in_multiline_comment = False

                        if stripped_line[-1] != '"':
                            self.stripped_lines.append(stripped_line + " ")
                        else:
                            self.stripped_lines.append(stripped_line)
                except ValueError:
                    pass
                except IndexError:
                    pass

        # the two indices below handle where I am in my list of stripped lines.
        self.current_line_index = 0
        self.current_char_index = 0

        # the current character
        self.current_char = None

        # the current line
        self.currentLine = None

    # detects if the tokenizer has more tokens
    def hasMoreTokens(self):
        # return if the current character index is the same as
        # the maximum character index for this line. then do the same for the
        # line index. after finding the result, reverse it.
        return not (self.current_char_index == len(
            self.stripped_lines[self.current_line_index]) - 1
                    and self.current_line_index == len(self.stripped_lines) - 1)

    # advances the current token to the next token
    def advance(self):
        # the current line
        curr_line = self.stripped_lines[self.current_line_index]

        # if the current character is None, make it the first character in
        # stripped_lines
        if self.current_char is None:
            self.current_token = ""
            self.current_char_index = 0
            self.current_line_index = 0
            self.current_char = self.stripped_lines[0][0]
            self.currentLine = self.stripped_lines[0]
            return

        # if I'm done finding all the delimiters, advance to the next line
        if (self.current_char_index >= len(curr_line) - 1
                and self.current_line_index < len(self.stripped_lines) - 1):
            self.current_line_index += 1
            self.current_char_index = 0
            self.current_char = self.stripped_lines[self.current_line_index][
                self.current_char_index]
            self.current_token = ""

            print("new line:", self.stripped_lines[self.current_line_index])
            self.currentLine = self.stripped_lines[self.current_line_index]
            return

        # if the current character is a symbol, immediately make it the next token
        if self.current_char in self.symbols:
            self.current_token = self.current_char
            self.current_char_index += 1
        # if the current character is a double quote, make the current token
        # a string from the current character index to the next double quote
        elif self.current_char == '"':
            next_quote_index = curr_line.index('"', self.current_char_index + 1)
            self.current_token = curr_line[self.current_char_index:next_quote_index + 1]

            self.current_char_index = next_quote_index + 1
            # print(self.current_char_index)
        else:
            # for each character in the current line, starting from the current
            # character index, check if the character at curr_line[char_index]
            # is a delimiter. if it is, make current_char_index the char_index.
            for char_index in range(self.current_char_index + 1, len(curr_line)):
                char = curr_line[char_index]

                # if we find a quote, we treat it as a delimiter.
                if char == '\"':
                    self.current_token = curr_line[self.current_char_index:char_index]

                    # to advance the current character index, we can make it
                    # the character index with the delim we just found
                    self.current_char_index = char_index
                    break

                # if we find a delimiter, make the current token a substring of the
                # current line from the current character index to char_index
                if self.isDelimiter(char) or char_index == len(curr_line) - 1:
                    self.current_token = curr_line[
                                         self.current_char_index:char_index]

                    self.current_char_index = char_index
                    break



        self.current_char = curr_line[self.current_char_index]
        print(self.current_char_index, ":", self.current_token)

    # checks the type of the current token
    def tokenType(self):
        # if we haven't initialized the current token or it's the start of the
        # line, do nothing.
        if self.current_token == "":
            return "Not a token."

        # same as the above, except we add a newline in syntaxAnalyzer.py.
        if self.current_token == " ":
            return "delimiter"

        self.current_token = self.current_token.strip(" ")

        # if the first character in the current token is a digit, then we know
        # it must be an integer constant because nothing else can start with a
        # digit.
        if self.current_token[0] in self.digits:
            return TokenType.INT_CONST

        # if the first character in the current token is a quote, then it's a
        # string constant, and we should print "STRING_CONST".
        elif self.current_token[0] == '"':
            return TokenType.STRING_CONST

        # if the current token is a keyword, then print KEYWORD.
        elif self.current_token in self.keywords:
            return TokenType.KEYWORD

        # if the current token is a symbol, then print SYMBOL.
        elif self.current_token in self.symbols:
            return TokenType.SYMBOL

        # finally, if none of the above are true, then current_token must be an
        # IDENTIFIER, so we print "IDENTIFIER".
        else:
            return TokenType.IDENTIFIER

    # returns current token if it's a keyword
    def keyword(self):
        return self.current_token

    # returns current token if it's a symbol
    def symbol(self):
        if self.current_token == "<":
            return "&lt;"

        if self.current_token == ">":
            return "&gt;"

        if self.current_token == "&":
            return "&amp;"

        return self.current_token

    # returns current token if it's an identifier
    def identifier(self):
        return self.current_token

    # returns current token if it's a integer constant
    def intVal(self):
        return self.current_token

    # returns current token if it's a string constant. Does not handle quotes.
    def stringVal(self):
        return self.current_token.strip('"')

    # returns if current character is a symbol.
    def isSymbol(self, char):
        return char in self.symbols

    # returns if current character is a symbol, whitespace, or newline.
    def isDelimiter(self, char):
        return (self.isSymbol(char) or
                char == "\n" or
                char == " "
                )
