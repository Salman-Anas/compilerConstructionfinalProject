# CS471L Mini Compiler Project
# Module: LL(1) Predictive Parser

class LL1Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens 
        self.pos = 0
        self.error_handler = error_handler
        self.stack = ['$', 'S'] 
        
        # Fully mapped LL(1) Table based on D1 FIRST/FOLLOW sets
        self.table = {
            'S':  {'program': ['program', 'id', ';', 'begin', 'L', 'end', '.']},
            'L':  {'id': ['A', "L'"]},
            "L'": {';': [';', 'A', "L'"], 'end': ['epsilon']},
            'A':  {'id': ['id', ':=', 'E']},
            'E':  {'id': ['T', "E'"], 'num': ['T', "E'"], '(': ['T', "E'"]},
            "E'": {'+': ['+', 'T', "E'"], ';': ['epsilon'], 'end': ['epsilon'], ')': ['epsilon']},
            'T':  {'id': ['F', "T'"], 'num': ['F', "T'"], '(': ['F', "T'"]},
            "T'": {'*': ['*', 'F', "T'"], '+': ['epsilon'], ';': ['epsilon'], 'end': ['epsilon'], ')': ['epsilon']},
            'F':  {'id': ['id'], 'num': ['num'], '(': ['(', 'E', ')']}
        }

    def parse(self):
        print("\n--- Starting LL(1) Parse ---")
        self.tokens.append(('EOF', '$', -1, -1)) 
        
        while len(self.stack) > 0:
            top = self.stack[-1]
            current_tag, current_val, line, col = self.tokens[self.pos]
            
            lookahead = current_val if current_tag in ('KEYWORD', 'PUNCT', 'ASSIGN', 'EOF') else current_tag.lower()

            if top == lookahead or (top == '$' and current_tag == 'EOF'):
                self.stack.pop()
                self.pos += 1
            elif top in self.table: 
                if lookahead in self.table[top]:
                    production = self.table[top][lookahead]
                    self.stack.pop()
                    if production != ['epsilon']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                else:
                    self.error_handler.report(line, col, f"LL(1) Syntax Error: Unexpected '{lookahead}'")
                    break 
            else:
                self.error_handler.report(line, col, f"LL(1) Syntax Error: Expected '{top}'")
                break