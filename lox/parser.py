import sys
from .expr import *
from .stmt import *
from .exceptions import ParseError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.has_error = False

    def parse_statements(self):
        statements = []
        try:
            while not self.is_at_end():
                statements.append(self.declaration())
            return statements
        except ParseError:
            return None

    def declaration(self):
        if self.match("CLASS"):
            return self.class_declaration()
        if self.match("FUN"):
            return self.function("function")
        if self.match("VAR"):
            return self.var_declaration()
        return self.statement()

    def class_declaration(self):
        name = self.consume("IDENTIFIER", "Expect class name.")
        superclass = None
        if self.match("LESS"):
            self.consume("IDENTIFIER", "Expect superclass name.")
            superclass = Variable(self.previous())
        self.consume("LEFT_BRACE", "Expect '{' before class body.")
        methods = []
        while not self.check("RIGHT_BRACE") and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume("RIGHT_BRACE", "Expect '}' after class body.")
        return Class(name, superclass, methods)

    def function(self, kind):
        name = self.consume("IDENTIFIER", f"Expect {kind} name.")
        self.consume("LEFT_PAREN", f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check("RIGHT_PAREN"):
            parameters.append(self.consume("IDENTIFIER", "Expect parameter name."))
            while self.match("COMMA"):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume("IDENTIFIER", "Expect parameter name."))
        self.consume("RIGHT_PAREN", "Expect ')' after parameters.")
        self.consume("LEFT_BRACE", f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

    def var_declaration(self):
        name = self.consume("IDENTIFIER", "Expect variable name.")
        initializer = None
        if self.match("EQUAL"):
            initializer = self.expression()
        self.consume("SEMICOLON", "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self):
        if self.match("FOR"): return self.for_statement()
        if self.match("IF"): return self.if_statement()
        if self.match("PRINT"): return self.print_statement()
        if self.match("RETURN"): return self.return_statement()
        if self.match("WHILE"): return self.while_statement()
        if self.match("LEFT_BRACE"): return Block(self.block())
        return self.expression_statement()

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check("SEMICOLON"):
            value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after return value.")
        return Return(keyword, value)

    def for_statement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'for'.")
        
        initializer = None
        if self.match("SEMICOLON"):
            initializer = None
        elif self.match("VAR"):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
            
        condition = None
        if not self.check("SEMICOLON"):
            condition = self.expression()
        self.consume("SEMICOLON", "Expect ';' after loop condition.")
        
        increment = None
        if not self.check("RIGHT_PAREN"):
            increment = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after for clauses.")
        
        body = self.statement()
        
        if increment is not None:
            body = Block([body, Expression(increment)])
            
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        
        if initializer is not None:
            body = Block([initializer, body])
            
        return body

    def while_statement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def if_statement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def block(self):
        statements = []
        while not self.check("RIGHT_BRACE") and not self.is_at_end():
            statements.append(self.declaration())
        self.consume("RIGHT_BRACE", "Expect '}' after block.")
        return statements

    def print_statement(self):
        value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        expr = self.expression()
        self.consume("SEMICOLON", "Expect ';' after expression.")
        return Expression(expr)

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None

    def error(self, token, message):
        if token.type == "EOF":
            print(f"[line {token.line}] Error at end: {message}", file=sys.stderr)
        else:
            print(f"[line {token.line}] Error at '{token.lexeme}': {message}", file=sys.stderr)
        self.has_error = True
        return ParseError()

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_expr()

        if self.match("EQUAL"):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)

            self.error(equals, "Invalid assignment target.")
        return expr

    def or_expr(self):
        expr = self.and_expr()
        while self.match("OR"):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr, operator, right)
        return expr

    def and_expr(self):
        expr = self.equality()
        while self.match("AND"):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match("MINUS", "PLUS"):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match("SLASH", "STAR"):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match("BANG", "MINUS"):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match("LEFT_PAREN"):
                expr = self.finish_call(expr)
            elif self.match("DOT"):
                name = self.consume("IDENTIFIER", "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check("RIGHT_PAREN"):
            arguments.append(self.expression())
            while self.match("COMMA"):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
        paren = self.consume("RIGHT_PAREN", "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self):
        if self.match("FALSE"): return Literal(False)
        if self.match("TRUE"): return Literal(True)
        if self.match("NIL"): return Literal(None)
        if self.match("THIS"): return This(self.previous())
        if self.match("SUPER"):
            keyword = self.previous()
            self.consume("DOT", "Expect '.' after 'super'.")
            method = self.consume("IDENTIFIER", "Expect superclass method name.")
            return Super(keyword, method)
        
        if self.match("NUMBER") or self.match("STRING"):
            return Literal(self.previous().literal)
            
        if self.match("IDENTIFIER"):
            return Variable(self.previous())
            
        if self.match("LEFT_PAREN"):
            expr = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, type):
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == "EOF"

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
