class VMWriter:
    def __init__(self):
        # opens a write-only VM file
        self.out = open("output.vm", "w")

    # writes a push statement
    def writePush(self, segment, index):
        self.out.write("push " + segment + " " + str(index) + "\n")

    # writes a pop statement
    def writePop(self, segment, index):
        pass

    # writes command to the output file.
    def writeArithmetic(self, command):
        pass

    # writes a label
    def writeLabel(self, label):
        pass

    # writes a goto label statement
    def writeGoto(self, label):
        pass

    # writes an if-goto label statement
    def writeIf(self, label):
        pass

    # writes a function call statement
    def writeCall(self, function, args):
        pass

    # writes a function declaration
    def writeFunction(self, function, args):
        pass

    # writes a return statement, which is just return
    def writeReturn(self):
        pass

    # closes the write-only output
    def close(self):
        pass
