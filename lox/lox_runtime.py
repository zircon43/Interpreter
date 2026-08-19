import time
from .environment import Environment
from .exceptions import ReturnException, LoxRuntimeError

class LoxCallable:
    def arity(self):
        pass
    def call(self, interpreter, arguments):
        pass

class Clock(LoxCallable):
    def arity(self):
        return 0
    def call(self, interpreter, arguments):
        return float(int(time.time()))
    def __str__(self):
        return "<native fn>"

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
            
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return e.value
            
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def __str__(self):
        return self.name

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance"
