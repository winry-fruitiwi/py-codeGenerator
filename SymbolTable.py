class SymbolTable:
    def __init__(self):
        # creates the class-level and subroutine-level symbol table.
        # Structure: {name:[type, kind, num]}
        self.classTable = {}
        self.subroutineTable = {}

    # reinitialize subroutine table as an empty dict
    def startSubroutine(self):
        self.subroutineTable = {}

    # defines new identifier of a given name, type, kind, and index (varCount).
    def define(self, name, type, kind):
        if kind == "STATIC" or "FIELD":
            self.classTable[name] = [type, kind, self.varCount(kind)]
        else:
            self.subroutineTable[name] = [type, kind, self.varCount(kind)]

    # finds the number of identifiers of the given kind
    def varCount(self, kind):
        kindCount = 0

        if kind == "STATIC" or "FIELD":
            target = self.classTable
        else:
            target = self.subroutineTable

        for name in target:
            if self.kindOf(name) == kind:
                kindCount += 1

        return kindCount

    # finds the kind of the given identifier
    def kindOf(self, name):
        pass

    # finds the type of the given identifier
    def typeOf(self, name):
        pass

    # finds the index of the given identifier
    def indexOf(self, name):
        pass
