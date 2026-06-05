# CS471L Mini Compiler Project
# Module: LL(1) Predictive Parser

class LL1Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.pos = 0
        self.error_handler = error_handler
        self.stack = ['$', 'S']

        # LL(1) parsing table
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

        # IMPORTANT: avoid double EOF append bug
        if self.tokens[-1][0] != 'EOF':
            self.tokens.append(('EOF', '$', -1, -1))

        step = 0

        while len(self.stack) > 0:
            step += 1

            top = self.stack[-1]
            current_tag, current_val, line, col = self.tokens[self.pos]

            lookahead = current_val if current_tag in (
                'KEYWORD', 'PUNCT', 'ASSIGN', 'EOF'
            ) else current_tag.lower()

            print(f"[LL1 Step {step}] Stack: {self.stack}")
            print(f"[LL1 Step {step}] Input: {self.tokens[self.pos:]}")
            print(f"[LL1 Step {step}] Top: {top}, Lookahead: {lookahead}")

            # MATCH CASE
            if top == lookahead or (top == '$' and current_tag == 'EOF'):
                print(f"[LL1] MATCH: {top}")
                self.stack.pop()
                self.pos += 1
                continue

            # NON-TERMINAL CASE
            if top in self.table:
                if lookahead in self.table[top]:
                    production = self.table[top][lookahead]

                    print(f"[LL1] APPLY: {top} → {production}")

                    self.stack.pop()

                    if production != ['epsilon']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                else:
                    self.error_handler.report(
                        line, col,
                        f"LL(1) Syntax Error: Unexpected '{lookahead}'"
                    )
                    print("[LL1] ERROR: No rule found")
                    break
            else:
                self.error_handler.report(
                    line, col,
                    f"LL(1) Syntax Error: Expected '{top}'"
                )
                print("[LL1] ERROR: Invalid stack symbol")
                break

        print("--- LL(1) Parse Complete ---")