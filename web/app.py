# web/app.py
# Author: M. Salman Anas (2023-CS-06)
# Completely insulated multi-module execution pipeline

import sys
import os
import io
import copy
import traceback
from contextlib import redirect_stdout
from flask import Flask, request, jsonify, render_template

# Ensure absolute paths are stitched across systems cleanly to prevent module load drops
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
    # Local fallback layout handler for alternative workspace environments
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

        # Global system module initialization instances
        error_sys = ErrorHandler()
        sym_table = SymbolTable()
        
        # 1. Base Token Generation Loop (Used exclusively to display values in the frontend grid view)
        lexer_grid = Lexer(source_code, error_sys)
        grid_tokens = []
        while True:
            tok = lexer_grid.get_next_token()
            grid_tokens.append(tok)
            if tok[0] == 'EOF': 
                break

        # 2. Re-tokenize to build a clean sequence array for the parsers (eliminating pointer side-effects)
        lexer_raw = Lexer(source_code, error_sys)
        raw_token_list = []
        while True:
            t = lexer_raw.get_next_token()
            raw_token_list.append(t)
            if t[0] == 'EOF': 
                break

        # 3. Mathematical Expression Isolation Phase for the LR Engine
        # Exactly mirrors the mathematical filtering tracking logic of your src/main.py script
        expr_tokens = []
        capture = False
        for tok in raw_token_list:
            if tok[1] == ':=':
                expr_tokens = [] 
                capture = True
            elif capture and (tok[1] in {';', '.'} or str(tok[0]).lower() in {'end', 'eof'}):
                capture = False
            elif capture:
                # Retain only terminal classifications mapped inside your SLR(1) ACTION table keys
                if tok[0] in ('ID', 'NUM') or tok[1] in ('+', '*', '(', ')'):
                    expr_tokens.append(tok)

        # Inject explicit end-of-file terminal lookahead sequence ($) matching parser_lr.py requirements
        if expr_tokens:
            last_line, last_col = expr_tokens[-1][2], expr_tokens[-1][3]
            if expr_tokens[-1][0] == 'EOF':
                expr_tokens.pop()
            expr_tokens.append(('EOF', '$', last_line, last_col))
        else:
            expr_tokens = [('EOF', '$', 1, 1)]

        # 4. Intercept and Redirect Output Streams for Frontend Logging Consoles
        rd_buf = io.StringIO()
        ll1_buf = io.StringIO()
        lr_buf = io.StringIO()

        # ---------------- RD PARSER ----------------
        with redirect_stdout(rd_buf):
            print("\n--- Starting Recursive Descent Parse ---")
            try:
                lexer_rd = Lexer(source_code, error_sys)
                rd_parser = RDParser(lexer_rd, sym_table, error_sys)
                rd_parser.parse()
            except Exception as e:
                print(f"RD ERROR: {e}")

        # ---------------- LL1 PARSER ----------------
        with redirect_stdout(ll1_buf):
            print("\n--- Starting LL(1) Parse ---")
            try:
                ll1_tokens_clean = copy.deepcopy(raw_token_list)
                ll1 = LL1Parser(ll1_tokens_clean, error_sys)
                ll1.parse()
            except Exception as e:
                print(f"LL1 ERROR: {e}")

        # ---------------- LR PARSER ----------------
        with redirect_stdout(lr_buf):
            print("\n--- Starting LR Bottom-Up Parse ---")
            try:
                lr = LRParser(expr_tokens, error_sys)
                lr.parse()
            except Exception as e:
                print(f"LR ERROR: {e}")
            
            # --- MODULE A: RECURSIVE DESCENT PARSER ---
            print("\n=========================================")
            print("1. RECURSIVE DESCENT PARSER TRACE LOGS")
            print("=========================================")
            try:
                # Instantiate a completely fresh, unused lexer instance
                lexer_rd = Lexer(source_code, error_sys) 
                rd_parser = RDParser(lexer_rd, sym_table, error_sys)
                rd_parser.parse()
            except Exception as rd_err:
                print(f"[RD Module System Failure]: {str(rd_err)}")

            # --- MODULE B: LL(1) PREDICTIVE PARSER ---
            print("\n=========================================")
            print("2. LL(1) PREDICTIVE PARSER TRACE LOGS")
            print("=========================================")
            try:
                # Deep-copy the token array to prevent the parser's internal .append() from corrupting other modules
                ll1_tokens_clean = copy.deepcopy(raw_token_list)
                ll1 = LL1Parser(ll1_tokens_clean, error_sys)
                ll1.parse()
            except Exception as ll1_err:
                print(f"[LL(1) Module System Failure]: {str(ll1_err)}")

            # --- MODULE C: LR BOTTOM-UP EXPRESSION PARSER ---
            print("\n=========================================")
            print("3. LR BOTTOM-UP EXPRESSION PARSER TRACE LOGS")
            print("=========================================")
            try:
                # Initialize using your mathematical expression fragments
                lr = LRParser(expr_tokens, error_sys)
                
                # Check your class for the correct interface entry hook
                if hasattr(lr, 'parse'):
                    lr.parse()
                elif hasattr(lr, 'parse_expression'):
                    lr.parse_expression(expr_tokens)
                else:
                    print("[LR Integration Error]: No matching executable parser routine tracked.")
            except Exception as lr_err:
                print(f"[LR Module System Failure]: {str(lr_err)}")

            # --- MODULE D: SYSTEM MEMORY AND DIAGNOSTIC CLOSURE SUMMARY ---
            print("\n=========================================")
            print("4. COMPILER MEMORY & DIAGNOSTIC SUMMARY")
            print("=========================================")
            try:
                sym_table.dump()
            except Exception as sym_err:
                print(f"[Symbol Table Serialization Failure]: {str(sym_err)}")
                
            error_sys.summarize()

        # terminal_output = f.getvalue()
        # terminal_output = f.getvalue()

        print("============== TERMINAL OUTPUT ==============")
        # print(terminal_output)
        print("============================================")
        # Build response map matching your interactive frontend dashboard requirements
        # Provides BOTH a combined log and split keys to satisfy any custom UI variations
        response_data = {
    'tokens': [{'tag': t[0], 'value': t[1], 'line': t[2], 'col': t[3]} for t in grid_tokens],
    'symbol_table': sym_table.scopes,
    'errors': error_sys.errors,

    'rd_trace': rd_buf.getvalue(),
    'll1_trace': ll1_buf.getvalue(),
    'lr_trace': lr_buf.getvalue()
}
        return jsonify(response_data)

    except Exception as general_backend_crash:
        # Safety mesh fallback: Ensures unhandled syntax bugs do not drop raw server HTML pages
        emergency_log = f"Fatal Core Pipeline Crash Intercepted:\n{str(general_backend_crash)}\n{traceback.format_exc()}"
        print(emergency_log)
        return jsonify({
            'tokens': [],
            'symbol_table': [{}],
            'errors': [f"Fatal Application Server Crash: {str(general_backend_crash)}"],
            'terminal_log': emergency_log,
            'rd_trace': emergency_log,
            'll1_trace': emergency_log,
            'lr_trace': emergency_log
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)