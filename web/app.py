# web/app.py
# Author: M. Salman Anas (2023-CS-06)

import sys
import os
import io
from contextlib import redirect_stdout
from flask import Flask, request, jsonify, render_template

# Add the src directory to the path so we can import your compiler modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from error_handler import ErrorHandler
from symbol_table import SymbolTable
from lexer import Lexer
from parser_rd import RDParser
from parser_ll1 import LL1Parser
from parser_lr import LRParser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    source_code = data.get('code', '')

    # Initialize Compiler Modules
    error_sys = ErrorHandler()
    sym_table = SymbolTable()
    
    # 1. Lexical Analysis (Capture all tokens)
    lexer = Lexer(source_code, error_sys)
    all_tokens = []
    while True:
        tok = lexer.get_next_token()
        all_tokens.append(tok)
        if tok[0] == 'EOF': break

    # Capture standard output for the parsers to send to the frontend UI
    f = io.StringIO()
    with redirect_stdout(f):
        # 2. Recursive Descent
        lexer_rd = Lexer(source_code, error_sys) 
        rd_parser = RDParser(lexer_rd, sym_table, error_sys)
        rd_parser.parse()

        # 3. LL(1) Parse
        ll1 = LL1Parser(all_tokens.copy(), error_sys)
        ll1.parse()

        # 4. LR Parse (Expressions Only)
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

        # 5. Finalize
        sym_table.dump()
        error_sys.summarize()

    terminal_output = f.getvalue()

    # Package the internal state for the modern UI
    response_data = {
        'tokens': [{'tag': t[0], 'value': t[1], 'line': t[2], 'col': t[3]} for t in all_tokens],
        'symbol_table': sym_table.scopes,
        'errors': error_sys.errors,
        'terminal_log': terminal_output
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)