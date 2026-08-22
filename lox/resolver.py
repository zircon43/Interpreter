import sys
from .expr import *
from .stmt import *

class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.has_error = False
        self.current_function = "NONE"
        self.current_class = "NONE"

    def resolve(self, statements):
        for stmt in statements:
            self.resolve_stmt(stmt)

    def resolve_stmt(self, stmt):
        if isinstance(stmt, Block):
            self.begin_scope()
            self.resolve(stmt.statements)
            self.end_scope()
        elif isinstance(stmt, Class):
            enclosing_class = self.current_class
            self.current_class = "CLASS"
            self.declare(stmt.name)
            self.define(stmt.name)
            if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
                self.error(stmt.superclass.name, "A class can't inherit from itself.")
            if stmt.superclass is not None:
                self.current_class = "SUBCLASS"
                self.resolve_expr(stmt.superclass)
            if stmt.superclass is not None:
                self.begin_scope()
                self.scopes[-1]["super"] = True
            self.begin_scope()
            self.scopes[-1]["this"] = True
            for method in stmt.methods:
                declaration = "METHOD"
                if method.name.lexeme == "init":
                    declaration = "INITIALIZER"
                self.resolve_function(method, declaration)
            self.end_scope()
            if stmt.superclass is not None:
                self.end_scope()
            self.current_class = enclosing_class
        elif isinstance(stmt, Var):
            self.declare(stmt.name)
            if stmt.initializer is not None:
                self.resolve_expr(stmt.initializer)
            self.define(stmt.name)
        elif isinstance(stmt, Function):
            self.declare(stmt.name)
            self.define(stmt.name)
            self.resolve_function(stmt, "FUNCTION")
        elif isinstance(stmt, Expression):
            self.resolve_expr(stmt.expression)
        elif isinstance(stmt, If):
            self.resolve_expr(stmt.condition)
            self.resolve_stmt(stmt.then_branch)
            if stmt.else_branch is not None:
                self.resolve_stmt(stmt.else_branch)
        elif isinstance(stmt, Print):
            self.resolve_expr(stmt.expression)
        elif isinstance(stmt, Return):
            if self.current_function == "NONE":
                self.error(stmt.keyword, "Can't return from top-level code.")
            if stmt.value is not None:
                if self.current_function == "INITIALIZER":
                    self.error(stmt.keyword, "Can't return a value from an initializer.")
                self.resolve_expr(stmt.value)
        elif isinstance(stmt, While):
            self.resolve_expr(stmt.condition)
            self.resolve_stmt(stmt.body)

    def resolve_expr(self, expr):
        if isinstance(expr, Variable):
            if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
                self.error(expr.name, "Can't read local variable in its own initializer.")
            self.resolve_local(expr, expr.name)
        elif isinstance(expr, Assign):
            self.resolve_expr(expr.value)
            self.resolve_local(expr, expr.name)
        elif isinstance(expr, Binary):
            self.resolve_expr(expr.left)
            self.resolve_expr(expr.right)
        elif isinstance(expr, Call):
            self.resolve_expr(expr.callee)
            for arg in expr.arguments:
                self.resolve_expr(arg)
        elif isinstance(expr, Get):
            self.resolve_expr(expr.object)
        elif isinstance(expr, Set):
            self.resolve_expr(expr.value)
            self.resolve_expr(expr.object)
        elif isinstance(expr, This):
            if self.current_class == "NONE":
                self.error(expr.keyword, "Can't use 'this' outside of a class.")
                return
            self.resolve_local(expr, expr.keyword)
        elif isinstance(expr, Super):
            if self.current_class == "NONE":
                self.error(expr.keyword, "Can't use 'super' outside of a class.")
            elif self.current_class != "SUBCLASS":
                self.error(expr.keyword, "Can't use 'super' in a class with no superclass.")
            self.resolve_local(expr, expr.keyword)
        elif isinstance(expr, Grouping):
            self.resolve_expr(expr.expression)
        elif isinstance(expr, Logical):
            self.resolve_expr(expr.left)
            self.resolve_expr(expr.right)
        elif isinstance(expr, Unary):
            self.resolve_expr(expr.right)

    def resolve_function(self, function, type):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.error(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def error(self, token, message):
        print(f"[line {token.line}] Error at '{token.lexeme}': {message}", file=sys.stderr)
        self.has_error = True
