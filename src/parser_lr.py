# src/parser_lr.py
# CS471L Mini Compiler Project
# Module: LR Parser (SLR(1) Expression Evaluator)

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
        
        # Full SLR(1) Action Table matching assignment mathematical criteria
        self.action = {
            0: {'id': 's5', 'num': 's5', '(': 's4'},
            1: {'+': 's6', '$': 'acc'},
            2: {'+': 'r2', '*': 's7', ')': 'r2', '$': 'r2'},
            3: {'+': 'r4', '*': 'r4', ')': 'r4', '$': 'r4'},
            4: {'id': 's5', 'num': 's5', '(': 's4'},
            5: {'+': 'r6', '*': 'r6', ')': 'r6', '$': 'r6'},
            6: {'id': 's5', 'num': 's5', '(': 's4'},
            7: {'id': 's5', 'num': 's5', '(': 's4'},
            8: {'+': 's6', ')': 's9'},
            9: {'+': 'r5', '*': 'r5', ')': 'r5', '$': 'r5'},
            10: {'+': 'r1', '*': 's7', ')': 'r1', '$': 'r1'},
            11: {'+': 'r3', '*': 'r3', ')': 'r3', '$': 'r3'}
        }
        
        # SLR(1) Goto Table definitions
        self.goto = {
            0: {'E': 1, 'T': 2, 'F': 3},
            4: {'E': 8, 'T': 2, 'F': 3},
            6: {'T': 10, 'F': 3},
            7: {'F': 11}
        }

    def parse(self):
        """
        Main entry point for Bottom-Up Expression Parser.
        Executes the Shift-Reduce automated routine over isolated mathematical math fragments.
        """
        print("\n--- Starting LR Bottom-Up Parse ---")
        pos = 0
        success = True
        
        while True:
            if pos >= len(self.tokens):
                # Fallback to absolute boundary lookahead strings if stream terminates early
                current_tag, current_val, line, col = 'EOF', '$', -1, -1
            else:
                current_tag, current_val, line, col = self.tokens[pos]
            
            current_state = self.state_stack[-1]
            
            # Normalize lexeme values to match action table keys
            lookahead = current_val if current_tag in ('PUNCT', 'EOF') else current_tag.lower()
            
            # Error checking layer against SLR action grid indices
            if lookahead not in self.action.get(current_state, {}):
                self.error_handler.report(line, col, f"LR Syntax Error: Unexpected token '{current_val}' at state {current_state}")
                success = False
                break
                
            act = self.action[current_state][lookahead]
            
            if act == 'acc':
                print(f"[{current_state}] Lookahead '{lookahead}': ACCEPT SUCCESS!")
                break
                
            elif act.startswith('s'):
                # --- SHIFT OPERATION ---
                next_state = int(act[1:])
                self.symbol_stack.append(lookahead)
                self.state_stack.append(next_state)
                print(f"[{current_state}] Shift lookahead '{lookahead}' -> State {next_state}")
                pos += 1
                
            elif act.startswith('r'):
                # --- REDUCE OPERATION ---
                rule_num = int(act[1:])
                lhs, pop_count = self.rules[rule_num]
                
                print(f"[{current_state}] Reduce by rule #{rule_num} ({lhs} -> length {pop_count})")
                
                # Pop matched handles off our tracking stack structures
                for _ in range(pop_count):
                    if self.symbol_stack: self.symbol_stack.pop()
                    if self.state_stack: self.state_stack.pop()
                    
                top_state = self.state_stack[-1]
                
                if lhs in self.goto.get(top_state, {}):
                    next_state = self.goto[top_state][lhs]
                    self.symbol_stack.append(lhs)
                    self.state_stack.append(next_state)
                    print(f"      Goto State {next_state} via Non-Terminal '{lhs}'")
                else:
                    self.error_handler.report(line, col, f"LR Goto Table Error: Missing transition for '{lhs}' from State {top_state}")
                    success = False
                    break
        
        return success