from .expr import Literal, Grouping, Unary, Binary

class AstPrinter:
    def print(self, expr):
        if isinstance(expr, Literal):
            if expr.value is None:
                return "nil"
            elif isinstance(expr.value, bool):
                return str(expr.value).lower()
            else:
                return str(expr.value)
        elif isinstance(expr, Grouping):
            return f"(group {self.print(expr.expression)})"
        elif isinstance(expr, Unary):
            return f"({expr.operator.lexeme} {self.print(expr.right)})"
        elif isinstance(expr, Binary):
            return f"({expr.operator.lexeme} {self.print(expr.left)} {self.print(expr.right)})"
        return ""
