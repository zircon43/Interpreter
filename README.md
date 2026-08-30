# Python Lox Interpreter

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Status](https://img.shields.io/badge/status-complete-success.svg)

A full-featured, tree-walk interpreter for the [Lox programming language](https://craftinginterpreters.com/the-lox-language.html), implemented entirely in Python from scratch.

This project was built to explore programming language theory, compiler design, and the practical challenges of parsing and interpreting code. It translates raw source code into a fully functioning dynamic language runtime without relying on external parsing or lexing libraries.

## ✨ Features

- **Lexical Analysis:** Custom scanner for robust tokenization of Lox source code.
- **Recursive Descent Parsing:** Translates tokens into an Abstract Syntax Tree (AST).
- **Expression Evaluation:** Full support for arithmetic, logical operations, and equality comparisons.
- **Control Flow:** Implementation of `if`/`else` branching, and `while`/`for` loops.
- **Functions & Closures:** First-class functions with persistent lexical environments (closures).
- **Static Scoping:** A semantic resolution pass that binds variables to their exact declaration scopes prior to runtime, effectively bypassing dynamic scoping bugs.
- **Object-Oriented Programming:** Classes, instances, `init()` constructors, methods, and `this` binding.
- **Inheritance:** Single inheritance using the `<` operator, along with `super` keyword resolution for subclassing.

## 🏗️ Architecture

The interpreter pipeline executes in the following modular stages:
1. **Scanner (`lox/scanner.py`)**: Reads raw text and groups characters into structural `Token`s.
2. **Parser (`lox/parser.py`)**: Uses recursive descent to convert tokens into a hierarchical Abstract Syntax Tree (AST).
3. **Resolver (`lox/resolver.py`)**: Performs a static semantic pass over the AST to compute variable scope resolution.
4. **Interpreter (`lox/interpreter.py`)**: Evaluates the AST using the post-resolved environments and dynamic runtime entities.

## 🚀 Usage

You can run the interpreter from the command line using the `main.py` entrypoint.

### Execute a Script
Run a Lox script directly:
```bash
python main.py run path/to/script.lox
```

### Advanced Commands
The CLI also exposes intermediate compiler stages for debugging and educational purposes:

- **Tokenize**: Output the lexical tokens.
  ```bash
  python main.py tokenize script.lox
  ```
- **Parse**: Output the stringified Abstract Syntax Tree.
  ```bash
  python main.py parse script.lox
  ```
- **Evaluate**: Evaluate a single expression.
  ```bash
  python main.py evaluate script.lox
  ```

## 📝 Example Lox Code

```javascript
// Classes and Inheritance
class Doughnut {
  cook() {
    print "Fry until golden brown.";
  }
}

class BostonCream < Doughnut {
  cook() {
    super.cook();
    print "Pipe full of custard and coat with chocolate.";
  }
}

var pastry = BostonCream();
pastry.cook();

// Functions and Closures
fun makeCounter() {
  var i = 0;
  fun count() {
    i = i + 1;
    print i;
  }
  return count;
}

var counter = makeCounter();
counter(); // 1
counter(); // 2
```

## 🛠️ Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-lox.git
   cd python-lox
   ```
2. The interpreter relies exclusively on Python standard libraries. No external dependencies or virtual environments are required!
