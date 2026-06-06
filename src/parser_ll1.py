# src/parser_ll1.py
class LL1Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.pos = 0
        self.error_handler = error_handler
        self.stack = ['$', 'S']
        self.steps_history = []  # Structural visual trace arrays

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
        if self.tokens[-1][0] != 'EOF':
            self.tokens.append(('EOF', '$', -1, -1))

        step_num = 0
        while len(self.stack) > 0:
            step_num += 1
            top = self.stack[-1]
            current_tag, current_val, line, col = self.tokens[self.pos]
            lookahead = current_val if current_tag in ('KEYWORD', 'PUNCT', 'ASSIGN', 'EOF') else current_tag.lower()

            # Record a snapshot of current live structures for custom diagrams
            stack_snapshot = list(self.stack)
            input_snapshot = [t[1] for t in self.tokens[self.pos:]]

            action_desc = ""
            action_type = "match"

            if top == lookahead or (top == '$' and current_tag == 'EOF'):
                action_desc = f"Match '{top}'"
                self.stack.pop()
                self.pos += 1
                action_type = "match"
            elif top in self.table:
                if lookahead in self.table[top]:
                    production = self.table[top][lookahead]
                    action_desc = f"{top} \u2192 {' '.join(production)}"
                    self.stack.pop()
                    if production != ['epsilon']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                    action_type = "apply"
                else:
                    action_desc = f"Syntax Error: Unexpected '{lookahead}'"
                    action_type = "error"
                    self.error_handler.report(line, col, action_desc)
                    self._record(step_num, stack_snapshot, input_snapshot, action_desc, action_type)
                    break
            else:
                action_desc = f"Syntax Error: Expected '{top}'"
                action_type = "error"
                self.error_handler.report(line, col, action_desc)
                self._record(step_num, stack_snapshot, input_snapshot, action_desc, action_type)
                break

            self._record(step_num, stack_snapshot, input_snapshot, action_desc, action_type)

    def _record(self, step_num, stack_snapshot, input_snapshot, action_desc, action_type):
        self.steps_history.append({
            'step': step_num,
            'stack': ' '.join(stack_snapshot),
            'input': ' '.join(input_snapshot[:6]) + ("..." if len(input_snapshot) > 6 else ""),
            'action': action_desc,
            'type': action_type
        })