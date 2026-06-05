# CS471L Mini Compiler Project - Group [Insert Group #]

**Language Subset:** Pascal

## Project Overview
This is a custom mini compiler built for a subset of the Pascal language. It integrates six distinct modules:
1. Lexical Analyzer (Double buffering, error tracking)
2. Recursive Descent Parser
3. Non-Recursive Predictive LL(1) Parser
4. LR Parser (Expression Sub-routine)
5. Symbol Table Manager (Hash-based with nested scope tracking)
6. Error Handler (Panic-mode recovery)

## Directory Structure
* `src/`: Contains `compiler.py` (all integrated modules).
* `docs/`: Contains the project report, BNF grammar, and parsing tables.
* `test/`: Contains sample `.pas` programs.
* `output/`: Contains the generated outputs and symbol table dumps.

## How to Run

### Prerequisites
* Python 3.x installed.
* Ensure you are in the root directory containing the `Makefile`.

### Using Make (Recommended)
To run the compiler on the default test file and display the output:
```bash
make run