

class Expr:
    pass

class Get(Expr):
    def __init__(self, object, name):
        self.object = object
        self.name = name

class Set(Expr):
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value

class This(Expr):
    def __init__(self, keyword):
        self.keyword = keyword

class Super(Expr):
    def __init__(self, keyword, method):
        self.keyword = keyword
        self.method = method

class Call(Expr):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Variable(Expr):
    def __init__(self, name):
        self.name = name

class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

