# CS471L Mini Compiler Project - Entry Point

import sys
from error_handler import ErrorHandler
from symbol_table import SymbolTable
from lexer import Lexer
from parser_rd import RDParser
from parser_ll1 import LL1Parser
from parser_lr import LRParser

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <source_file.pas>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'")
        sys.exit(1)

    print(f"Compiling '{filename}'...")
    error_sys = ErrorHandler()
    sym_table = SymbolTable()
    
    # Run Lexer 
    lexer = Lexer(source_code, error_sys)
    all_tokens = []
    while True:
        tok = lexer.get_next_token()
        all_tokens.append(tok)
        if tok[0] == 'EOF': break

    # 1. Recursive Descent 
    lexer = Lexer(source_code, error_sys) 
    rd_parser = RDParser(lexer, sym_table, error_sys)
    rd_parser.parse()

    # 2. LL(1) Parse
    ll1 = LL1Parser(all_tokens.copy(), error_sys)
    ll1.parse()
    
    # 3. LR Parse (Expressions)
    # We must isolate just the math tokens to feed into the LR expression engine.
    # We will grab the final mathematical expression in the file (after the last ':=')
    expr_tokens = []
    capture = False
    for tok in all_tokens:
        if tok[1] == ':=':
            expr_tokens = [] 
            capture = True
        elif capture and tok[1].lower() in {';', 'end', 'eof'}:
            capture = False
        elif capture:
            expr_tokens.append(tok)

    lr = LRParser(all_tokens.copy(), error_sys)
    if expr_tokens:
        lr.parse_expression(expr_tokens)
    else:
        print("\n--- Skipping LR Parse (No expression found to trace) ---")

    error_sys.summarize()
