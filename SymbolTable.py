class SymbolTable:
    def __init__(self):
        # creates the class-level and subroutine-level symbol table.
        # Structure: {name:[type, kind, num]}
        self.classTable = {}
        self.subroutineTable = {}

    # reinitialize subroutine table as an empty dict. for example, switching
    # from subroutine foo to subroutine bar would count as a subroutine start.
    # However, a switch from subroutine Foo.bar to Bar.foo would be handled
    # by the initialization of a new symbol table because we're switching
    # classes.
    def startSubroutine(self):
        self.subroutineTable = {}

    # defines new identifier of a given name, type, kind, and index (varCount).
    # Example: define("happy", "FIELD", "game") would update class level symbol
    # table to {'happy': ['game', 'FIELD', 0]}. Another define call on 'happy'
    # would change its value. if we defined happy with a kind of "ARGUMENT", it
    # would be registered as a subroutine-level symbol table update.
    def define(self, name, kind, type):
        # if the kind is STATIC or FIELD, then it's a class level definition.
        if kind == "STATIC" or kind == "FIELD":
            self.classTable[name] = [type, kind, self.varCount(kind)]
        # otherwise, it must be a subroutine level definition.
        else:
            self.subroutineTable[name] = [type, kind, self.varCount(kind)]

    # finds the number of identifiers of the given kind. for example: state of
    # class-level table: {'happy': ['int', 'FIELD', 0]}. defining a new var
    # called "meat boot", with type int, kind FIELD. varCount will return 1,
    # then a new variable called "meat boot" is created with ["int", "FIELD", 1]
    def varCount(self, kind):
        # initialize the number of variables created with kind
        kindCount = 0

        # if kind is STATIC or FIELD, make the target the class table.
        if kind == "STATIC" or kind == "FIELD":
            target = self.classTable
        # otherwise, the target is the subroutine table.
        else:
            target = self.subroutineTable

        # use kindOf to access the name in target. You can't use in here, as it
        # doesn't check values or inside them if they're lists.
        for name in target:
            if self.kindOf(name) == kind.lower():
                kindCount += 1

        return kindCount

    # a helper function that says which table name is in. Used in kindOf,
    # typeOf, and indexOf. Example: you're finding name in two different tables,
    # and it's in the class table. You try finding it in the subroutine table
    # but don't find it. Then you notice that it's in the class table and
    # return the class table.
    # TODO consider adding code for calling subroutines when they're not vars.
    def findNameInTables(self, name):
        if name in self.subroutineTable:
            return self.subroutineTable
        return self.classTable

    # finds the kind of the given identifier. there are tests for kindOf,
    # typeOf, and indexOf in syntaxAnalyzer.py demonstrating their usage.
    def kindOf(self, name):
        table = self.findNameInTables(name)
        return table[name][1].lower()

    # finds the type of the given identifier. Test in main file.
    def typeOf(self, name):
        table = self.findNameInTables(name)
        return table[name][0]

    # finds the index of the given identifier. Test in main file.
    def indexOf(self, name):
        table = self.findNameInTables(name)
        return table[name][2]
