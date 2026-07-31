import sys
from .token import Token

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.has_error = False
        self.line_number = 1
        self.i = 0
        
        self.reserved_words = {
            "and": "AND",
            "class": "CLASS",
            "else": "ELSE",
            "false": "FALSE",
            "for": "FOR",
            "fun": "FUN",
            "if": "IF",
            "nil": "NIL",
            "or": "OR",
            "print": "PRINT",
            "return": "RETURN",
            "super": "SUPER",
            "this": "THIS",
            "true": "TRUE",
            "var": "VAR",
            "while": "WHILE"
        }

        self.single_char_tokens = {
            '(': 'LEFT_PAREN', ')': 'RIGHT_PAREN',
            '{': 'LEFT_BRACE', '}': 'RIGHT_BRACE',
            ',': 'COMMA', '.': 'DOT',
            '-': 'MINUS', '+': 'PLUS',
            ';': 'SEMICOLON', '*': 'STAR'
        }

    def scan_tokens(self):
        while self.i < len(self.source):
            char = self.source[self.i]
            
            if char in self.single_char_tokens:
                self.add_token(self.single_char_tokens[char], char, "null")
            elif char == '=':
                if self.match_next('='):
                    self.add_token("EQUAL_EQUAL", "==", "null")
                else:
                    self.add_token("EQUAL", "=", "null")
            elif char == '!':
                if self.match_next('='):
                    self.add_token("BANG_EQUAL", "!=", "null")
                else:
                    self.add_token("BANG", "!", "null")
            elif char == '<':
                if self.match_next('='):
                    self.add_token("LESS_EQUAL", "<=", "null")
                else:
                    self.add_token("LESS", "<", "null")
            elif char == '>':
                if self.match_next('='):
                    self.add_token("GREATER_EQUAL", ">=", "null")
                else:
                    self.add_token("GREATER", ">", "null")
            elif char == '/':
                if self.match_next('/'):
                    while self.i < len(self.source) and self.source[self.i] != '\n':
                        self.i += 1
                    continue
                else:
                    self.add_token("SLASH", "/", "null")
            elif char == '\n':
                self.line_number += 1
            elif char in [' ', '\r', '\t']:
                pass
            elif char == '"':
                start_i = self.i
                self.i += 1
                while self.i < len(self.source) and self.source[self.i] != '"':
                    if self.source[self.i] == '\n':
                        self.line_number += 1
                    self.i += 1
                    
                if self.i >= len(self.source):
                    print(f"[line {self.line_number}] Error: Unterminated string.", file=sys.stderr)
                    self.has_error = True
                    continue
                    
                value = self.source[start_i+1:self.i]
                self.add_token("STRING", f'"{value}"', value)
            elif char.isdigit():
                start_i = self.i
                while self.i < len(self.source) and self.source[self.i].isdigit():
                    self.i += 1
                if self.i < len(self.source) and self.source[self.i] == '.':
                    if self.i + 1 < len(self.source) and self.source[self.i+1].isdigit():
                        self.i += 1
                        while self.i < len(self.source) and self.source[self.i].isdigit():
                            self.i += 1
                
                value = self.source[start_i:self.i]
                literal = float(value)
                self.add_token("NUMBER", value, literal)
                continue
            elif char.isalpha() or char == '_':
                start_i = self.i
                while self.i < len(self.source) and (self.source[self.i].isalnum() or self.source[self.i] == '_'):
                    self.i += 1
                value = self.source[start_i:self.i]
                if value in self.reserved_words:
                    self.add_token(self.reserved_words[value], value, "null")
                else:
                    self.add_token("IDENTIFIER", value, "null")
                continue
            else:
                print(f"[line {self.line_number}] Error: Unexpected character: {char}", file=sys.stderr)
                self.has_error = True
                
            self.i += 1
            
        self.tokens.append(Token("EOF", "", "null", self.line_number))
        return self.tokens

    def match_next(self, expected):
        if self.i + 1 < len(self.source) and self.source[self.i+1] == expected:
            self.i += 1
            return True
        return False
        
    def add_token(self, type, lexeme, literal):
        self.tokens.append(Token(type, lexeme, literal, self.line_number))
