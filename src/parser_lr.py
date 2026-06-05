# CS471L Mini Compiler Project
# Module: LR Parser

class LRParser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.pos = 0
        self.error_handler = error_handler
        self.state_stack = [0]
        self.symbol_stack = []
        
        # 1:E->E+T, 2:E->T, 3:T->T*F, 4:T->F, 5:F->(E), 6:F->id
        self.rules = {
            1: ('E', 3), 2: ('E', 1), 3: ('T', 3), 
            4: ('T', 1), 5: ('F', 3), 6: ('F', 1)
        }
        
        # Full SLR(1) Action Table
        self.action = {
            0: {'id': 's5', 'num': 's5', '(': 's4'},
            1: {'+': 's6', '$': 'acc'},
            2: {'+': 'r2', '*': 's7', ')': 'r2', '$': 'r2'},
            3: {'+': 'r4', '*': 'r4', ')': 'r4', '$': 'r4'},
            4: {'id': 's5', 'num': 's5', '(': 's4'},
            5: {'+': 'r6', '*': 'r6', ')': 'r6', '$': 'r6'},
            6: {'id': 's5', 'num': 's5', '(': 's4'},
            7: {'id': 's5', 'num': 's5', '(': 's4'},
            8: {'+': 's6', ')': 's11'},
            9: {'+': 'r1', '*': 's7', ')': 'r1', '$': 'r1'},
            10: {'+': 'r3', '*': 'r3', ')': 'r3', '$': 'r3'},
            11: {'+': 'r5', '*': 'r5', ')': 'r5', '$': 'r5'}
        }
        
        # Full SLR(1) Goto Table
        self.goto = {
            0: {'E': 1, 'T': 2, 'F': 3},
            4: {'E': 8, 'T': 2, 'F': 3},
            6: {'T': 9, 'F': 3},
            7: {'F': 10}
        }

    def parse_expression(self, expression_tokens):
        print("\n--- Starting LR Parse (Expression Trace) ---")
        self.state_stack = [0]
        self.symbol_stack = []
        
        # Append end marker for LR parse
        tokens = expression_tokens + [('EOF', '$', -1, -1)]
        pos = 0
        
        while True:
            current_state = self.state_stack[-1]
            current_tag, current_val, line, col = tokens[pos]
            
            # Map token to table column
            lookahead = current_val if current_tag in ('PUNCT', 'EOF') else current_tag.lower()
            if lookahead not in self.action.get(current_state, {}):
                self.error_handler.report(line, col, f"LR Syntax Error at '{current_val}'")
                break
                
            act = self.action[current_state][lookahead]
            
            if act.startswith('s'):
                # SHIFT
                next_state = int(act[1:])
                self.symbol_stack.append(lookahead)
                self.state_stack.append(next_state)
                print(f"Shift to state {next_state}")
                pos += 1
                
            elif act.startswith('r'):
                # REDUCE
                rule_num = int(act[1:])
                lhs, pop_count = self.rules[rule_num]
                
                for _ in range(pop_count):
                    self.symbol_stack.pop()
                    self.state_stack.pop()
                    
                top_state = self.state_stack[-1]
                next_state = self.goto[top_state][lhs]
                
                self.symbol_stack.append(lhs)
                self.state_stack.append(next_state)
                print(f"Reduce by rule {rule_num} ({lhs} -> ...), Goto state {next_state}")
                
            elif act == 'acc':
                print("LR Parse Accepted!")
                break