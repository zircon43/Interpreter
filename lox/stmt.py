from .expr import Expr

class Stmt:
    pass

class Class(Stmt):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

class Function(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements

class Expression(Stmt):
    def __init__(self, expression):
        self.expression = expression

class Print(Stmt):
    def __init__(self, expression):
        self.expression = expression

class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

