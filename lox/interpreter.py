import sys
from .expr import *
from .stmt import *
from .environment import Environment
from .lox_runtime import Clock, LoxCallable, LoxFunction, LoxClass, LoxInstance
from .exceptions import LoxRuntimeError, ReturnException

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.globals.define("clock", Clock())
        self.locals = {}

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def look_up_variable(self, name, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            print(f"{e.message}\n[line {e.token.line}]", file=sys.stderr)
            exit(70)

    def execute(self, stmt):
        if isinstance(stmt, Print):
            value = self.evaluate(stmt.expression)
            print(self.stringify(value))
        elif isinstance(stmt, Expression):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, Var):
            value = None
            if stmt.initializer is not None:
                value = self.evaluate(stmt.initializer)
            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, Block):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, If):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                self.execute(stmt.else_branch)
        elif isinstance(stmt, While):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        elif isinstance(stmt, Class):
            superclass = None
            if stmt.superclass is not None:
                superclass = self.evaluate(stmt.superclass)
                if not isinstance(superclass, LoxClass):
                    raise LoxRuntimeError(stmt.superclass.name, "Superclass must be a class.")
            self.environment.define(stmt.name.lexeme, None)
            if stmt.superclass is not None:
                self.environment = Environment(self.environment)
                self.environment.define("super", superclass)
            methods = {}
            for method in stmt.methods:
                is_init = method.name.lexeme == "init"
                function = LoxFunction(method, self.environment, is_init)
                methods[method.name.lexeme] = function
            klass = LoxClass(stmt.name.lexeme, superclass, methods)
            if superclass is not None:
                self.environment = self.environment.enclosing
            self.environment.assign(stmt.name, klass)
        elif isinstance(stmt, Function):
            function = LoxFunction(stmt, self.environment)
            self.environment.define(stmt.name.lexeme, function)
        elif isinstance(stmt, Return):
            value = None
            if stmt.value is not None:
                value = self.evaluate(stmt.value)
            raise ReturnException(value)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            return self.look_up_variable(expr.name, expr)
        elif isinstance(expr, Assign):
            value = self.evaluate(expr.value)
            distance = self.locals.get(expr)
            if distance is not None:
                self.environment.assign_at(distance, expr.name, value)
            else:
                self.globals.assign(expr.name, value)
            return value
        elif isinstance(expr, Get):
            obj = self.evaluate(expr.object)
            if isinstance(obj, LoxInstance):
                return obj.get(expr.name)
            raise LoxRuntimeError(expr.name, "Only instances have properties.")
        elif isinstance(expr, Set):
            obj = self.evaluate(expr.object)
            if isinstance(obj, LoxInstance):
                value = self.evaluate(expr.value)
                obj.set(expr.name, value)
                return value
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        elif isinstance(expr, This):
            return self.look_up_variable(expr.keyword, expr)
        elif isinstance(expr, Super):
            distance = self.locals.get(expr)
            superclass = self.environment.get_at(distance, "super")
            obj = self.environment.get_at(distance - 1, "this")
            method = superclass.find_method(expr.method.lexeme)
            if method is None:
                raise LoxRuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")
            return method.bind(obj)
        elif isinstance(expr, Logical):
            left = self.evaluate(expr.left)
            if expr.operator.type == "OR":
                if self.is_truthy(left): return left
            else:
                if not self.is_truthy(left): return left
            return self.evaluate(expr.right)
        elif isinstance(expr, Call):
            callee = self.evaluate(expr.callee)
            arguments = [self.evaluate(arg) for arg in expr.arguments]
            
            if not isinstance(callee, LoxCallable):
                raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
                
            if len(arguments) != callee.arity():
                raise LoxRuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
                
            return callee.call(self, arguments)
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, Unary):
            right = self.evaluate(expr.right)
            if expr.operator.type == "MINUS":
                self.check_number_operand(expr.operator, right)
                return -float(right)
            elif expr.operator.type == "BANG":
                return not self.is_truthy(right)
        elif isinstance(expr, Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            
            op_type = expr.operator.type
            if op_type == "MINUS":
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            elif op_type == "SLASH":
                self.check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            elif op_type == "STAR":
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            elif op_type == "PLUS":
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            elif op_type == "GREATER":
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            elif op_type == "GREATER_EQUAL":
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            elif op_type == "LESS":
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            elif op_type == "LESS_EQUAL":
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            elif op_type == "BANG_EQUAL":
                return not self.is_equal(left, right)
            elif op_type == "EQUAL_EQUAL":
                return self.is_equal(left, right)
        return None

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")
        
    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")
        
    def is_equal(self, a, b):
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    def is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def stringify(self, value):
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return str(value)
        return str(value)
