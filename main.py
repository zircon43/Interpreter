import sys
from lox.scanner import Scanner
from lox.parser import Parser
from lox.interpreter import Interpreter
from lox.resolver import Resolver
from lox.ast_printer import AstPrinter
from lox.exceptions import ParseError, LoxRuntimeError

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ["tokenize", "parse", "evaluate", "run"]:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    print("Logs from your program will appear here!", file=sys.stderr)

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    if command == "tokenize":
        for token in tokens:
            if token.type == "EOF":
                print("EOF  null")
            else:
                print(token)
        if scanner.has_error:
            exit(65)
    elif command == "parse":
        if scanner.has_error:
            exit(65)
        parser = Parser(tokens)
        expr = parser.parse()
        if parser.has_error:
            exit(65)
        printer = AstPrinter()
        if expr is not None:
            print(printer.print(expr))
    elif command == "evaluate":
        if scanner.has_error:
            exit(65)
        parser = Parser(tokens)
        expr = parser.parse()
        if parser.has_error:
            exit(65)
        
        if expr is not None:
            interpreter = Interpreter()
            try:
                result = interpreter.evaluate(expr)
                print(interpreter.stringify(result))
            except LoxRuntimeError as e:
                print(f"{e.message}\n[line {e.token.line}]", file=sys.stderr)
                exit(70)
    elif command == "run":
        if scanner.has_error:
            exit(65)
        parser = Parser(tokens)
        statements = parser.parse_statements()
        if parser.has_error:
            exit(65)
        
        if statements is not None:
            interpreter = Interpreter()
            resolver = Resolver(interpreter)
            resolver.resolve(statements)
            if resolver.has_error:
                exit(65)
            interpreter.interpret(statements)

if __name__ == "__main__":
    main()
