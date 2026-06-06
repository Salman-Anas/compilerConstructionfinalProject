# web/app.py
# Compiler backend: AST + RD call-tree + LL(1) steps/table + LR automaton/steps

import sys
import os
import io
import copy
from contextlib import redirect_stdout
from flask import Flask, request, jsonify, render_template

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..', 'src'))

if src_dir not in sys.path:
    sys.path.append(src_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from error_handler import ErrorHandler
    from symbol_table import SymbolTable
    from lexer import Lexer
    from parser_rd import RDParser
    from parser_ll1 import LL1Parser
    from parser_lr import LRParser
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
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
    try:
        data = request.json or {}
        source_code = data.get('code', '')

        error_sys = ErrorHandler()
        sym_table = SymbolTable()

        # 1. Lexical Analysis
        lexer = Lexer(source_code, error_sys)
        all_tokens = []
        while True:
            tok = lexer.get_next_token()
            all_tokens.append(tok)
            if tok[0] == 'EOF':
                break

        # 2. Recursive Descent: AST + call tree
        ast_data = None
        rd_tree = None
        rd_output = io.StringIO()
        with redirect_stdout(rd_output):
            try:
                lexer_rd = Lexer(source_code, error_sys)
                rd_parser = RDParser(lexer_rd, sym_table, error_sys)
                ast = rd_parser.parse()
                if ast:
                    ast_data = ast.to_dict()
                if rd_parser.call_root:
                    rd_tree = rd_parser.call_root.to_dict()
            except Exception as e:
                print(f"RD Parser Error: {e}")

        # 3. LL(1) Parser -> structured steps + parse table
        ll1_steps = []
        ll1_table = {}
        ll1_output = io.StringIO()
        with redirect_stdout(ll1_output):
            try:
                ll1_tokens = copy.deepcopy(all_tokens)
                ll1 = LL1Parser(ll1_tokens, error_sys)
                ll1.parse()
                ll1_steps = ll1.steps_history
                ll1_table = ll1.table
            except Exception as e:
                print(f"LL(1) Error: {e}")

        # 4. Expression extraction for LR
        expr_tokens = []
        capture = False
        for tok in all_tokens:
            if tok[1] == ':=':
                expr_tokens = []
                capture = True
            elif capture and (tok[1] in {';', '.'} or str(tok[0]).lower() in {'end', 'eof'}):
                capture = False
            elif capture:
                if tok[0] in ('ID', 'NUM') or tok[1] in ('+', '*', '(', ')'):
                    expr_tokens.append(tok)

        if expr_tokens:
            if expr_tokens[-1][0] != 'EOF':
                expr_tokens.append(('EOF', '$', expr_tokens[-1][2], expr_tokens[-1][3]))
        else:
            expr_tokens = [('EOF', '$', 1, 1)]

        # 5. LR Parser -> structured steps + static automaton
        lr_steps = []
        lr_output = io.StringIO()
        with redirect_stdout(lr_output):
            try:
                lr = LRParser(expr_tokens, error_sys)
                lr.parse()
                lr_steps = lr.trace_steps
            except Exception as e:
                print(f"LR Error: {e}")

        lr_automaton = LRParser.automaton()

        # Symbol table dump (text) for the log
        sym_output = io.StringIO()
        with redirect_stdout(sym_output):
            sym_table.dump()
            error_sys.summarize()

        # Tokens for frontend
        token_list = []
        for t in all_tokens:
            if t[0] != 'EOF':
                token_list.append({'tag': t[0], 'value': t[1], 'line': t[2], 'col': t[3]})

        response_data = {
            'tokens': token_list,
            'symbol_table': sym_table.records,   # FIX: persistent records (all symbols)
            'errors': error_sys.errors,
            'ast': ast_data,
            'rd_tree': rd_tree,
            'rd_trace': rd_output.getvalue(),
            'll1_steps': ll1_steps,
            'll1_table': ll1_table,
            'll1_trace': ll1_output.getvalue(),
            'lr_steps': lr_steps,
            'lr_automaton': lr_automaton,
            'lr_trace': lr_output.getvalue(),
            'symbol_trace': sym_output.getvalue()
        }
        return jsonify(response_data)

    except Exception as e:
        import traceback
        return jsonify({
            'tokens': [], 'symbol_table': [], 'errors': [f"Compiler Error: {str(e)}"],
            'ast': None, 'rd_tree': None, 'rd_trace': traceback.format_exc(),
            'll1_steps': [], 'll1_table': {}, 'll1_trace': '',
            'lr_steps': [], 'lr_automaton': {'states': [], 'edges': []}, 'lr_trace': '',
            'symbol_trace': ''
        })


if __name__ == '__main__':
    app.run(debug=True, port=5000)