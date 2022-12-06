class VMWriter:
    def __init__(self):
        # opens a write-only VM file
        self.out = open("Main.vm", "w")

    # a wrapper for self.out.write(string + "\n")
    def write(self, string):
        self.out.write(string + "\n")

    # writes a push statement
    def writePush(self, segment, index):
        self.write("push " + segment + " " + str(index))

    # writes a pop statement
    def writePop(self, segment, index):
        self.write("pop " + segment + " " + str(index))

    # writes command to the output file.
    def writeArithmetic(self, command):
        self.write(command)

    # writes a label
    def writeLabel(self, label):
        self.write("label " + label)

    # writes a goto label statement
    def writeGoto(self, label):
        self.write("goto " + label)

    # writes an if-goto label statement
    def writeIf(self, label):
        self.write("if-goto " + label)

    # writes a function call statement
    def writeCall(self, function, args):
        self.write("call " + function + " " + str(args))

    # writes a function declaration
    def writeFunction(self, function, args):
        self.write("function " + function + " " + str(args))

    # writes a return statement, which is just return
    def writeReturn(self):
        self.write("return")

    # closes the write-only output
    def close(self):
        self.out.close()
