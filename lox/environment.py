from .exceptions import LoxRuntimeError

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, token):
        if token.lexeme in self.values:
            return self.values[token.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(token)
        raise LoxRuntimeError(token, f"Undefined variable '{token.lexeme}'.")

    def assign(self, token, value):
        if token.lexeme in self.values:
            self.values[token.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(token, value)
            return
        raise LoxRuntimeError(token, f"Undefined variable '{token.lexeme}'.")

    def get_at(self, distance, name):
        return self.ancestor(distance).values.get(name)

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment
