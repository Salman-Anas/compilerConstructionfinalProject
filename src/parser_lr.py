# src/parser_lr.py
# CS471L Mini Compiler Project
# Module: LR Parser (SLR(1) Expression Evaluator)

class LRParser:
    # Canonical LR(0) item sets for the expression grammar:
    #   0: S' -> E   1: E -> E + T   2: E -> T
    #   3: T -> T * F  4: T -> F      5: F -> ( E )   6: F -> id
    # Used to draw the SLR automaton diagram in the UI.
    ITEM_SETS = {
        0:  ["S' \u2192 \u2022E", "E \u2192 \u2022E + T", "E \u2192 \u2022T",
             "T \u2192 \u2022T * F", "T \u2192 \u2022F", "F \u2192 \u2022( E )", "F \u2192 \u2022id"],
        1:  ["S' \u2192 E\u2022", "E \u2192 E\u2022 + T"],
        2:  ["E \u2192 T\u2022", "T \u2192 T\u2022 * F"],
        3:  ["T \u2192 F\u2022"],
        4:  ["F \u2192 (\u2022E )", "E \u2192 \u2022E + T", "E \u2192 \u2022T",
             "T \u2192 \u2022T * F", "T \u2192 \u2022F", "F \u2192 \u2022( E )", "F \u2192 \u2022id"],
        5:  ["F \u2192 id\u2022"],
        6:  ["E \u2192 E +\u2022T", "T \u2192 \u2022T * F", "T \u2192 \u2022F",
             "F \u2192 \u2022( E )", "F \u2192 \u2022id"],
        7:  ["T \u2192 T *\u2022F", "F \u2192 \u2022( E )", "F \u2192 \u2022id"],
        8:  ["F \u2192 ( E\u2022)", "E \u2192 E\u2022 + T"],
        9:  ["F \u2192 ( E )\u2022"],
        10: ["E \u2192 E + T\u2022", "T \u2192 T\u2022 * F"],
        11: ["T \u2192 T * F\u2022"],
    }

    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.pos = 0
        self.error_handler = error_handler
        self.state_stack = [0]
        self.symbol_stack = []
        self.trace_steps = []   # structured shift/reduce trace for the UI

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

    @classmethod
    def automaton(cls):
        """Export states (with their LR(0) items) and labelled transitions so the
        frontend can render the SLR automaton diagram."""
        inst = cls([], None)
        # merge shift + goto transitions, combining labels that share from/to
        merged = {}
        for state, row in inst.action.items():
            for sym, act in row.items():
                if isinstance(act, str) and act.startswith('s'):
                    key = (state, int(act[1:]))
                    merged.setdefault(key, set()).add(sym)
        for state, row in inst.goto.items():
            for sym, tgt in row.items():
                merged.setdefault((state, tgt), set()).add(sym)

        edges = [{'from': f, 'to': t, 'label': ', '.join(sorted(labels))}
                 for (f, t), labels in merged.items()]
        states = [{'id': k, 'items': v} for k, v in sorted(cls.ITEM_SETS.items())]
        return {'states': states, 'edges': edges}

    def parse(self):
        return self.parse_expression(self.tokens)

    def parse_expression(self, tokens=None):
        """Bottom-Up Shift-Reduce parser over an isolated math expression."""
        if tokens is not None:
            self.tokens = tokens
        print("\n--- Starting LR Bottom-Up Parse ---")
        pos = 0
        success = True

        while True:
            if pos >= len(self.tokens):
                current_tag, current_val, line, col = 'EOF', '$', -1, -1
            else:
                current_tag, current_val, line, col = self.tokens[pos]

            current_state = self.state_stack[-1]
            lookahead = current_val if current_tag in ('PUNCT', 'EOF') else current_tag.lower()

            remaining = ' '.join(str(t[1]) for t in self.tokens[pos:]) or '$'

            if lookahead not in self.action.get(current_state, {}):
                desc = f"Syntax Error: unexpected '{current_val}' at state {current_state}"
                self._record(remaining, desc, 'error')
                self.error_handler.report(line, col, f"LR {desc}")
                success = False
                break

            act = self.action[current_state][lookahead]

            if act == 'acc':
                self._record(remaining, "ACCEPT \u2713", 'accept')
                print(f"[{current_state}] Lookahead '{lookahead}': ACCEPT SUCCESS!")
                break

            elif act.startswith('s'):
                next_state = int(act[1:])
                self._record(remaining, f"Shift '{lookahead}' \u2192 state {next_state}", 'shift')
                self.symbol_stack.append(lookahead)
                self.state_stack.append(next_state)
                print(f"[{current_state}] Shift lookahead '{lookahead}' -> State {next_state}")
                pos += 1

            elif act.startswith('r'):
                rule_num = int(act[1:])
                lhs, pop_count = self.rules[rule_num]
                prod = self._rule_text(rule_num)
                self._record(remaining, f"Reduce r{rule_num}: {prod}", 'reduce')
                print(f"[{current_state}] Reduce by rule #{rule_num} ({lhs} -> length {pop_count})")

                for _ in range(pop_count):
                    if self.symbol_stack:
                        self.symbol_stack.pop()
                    if self.state_stack:
                        self.state_stack.pop()

                top_state = self.state_stack[-1]
                if lhs in self.goto.get(top_state, {}):
                    next_state = self.goto[top_state][lhs]
                    self.symbol_stack.append(lhs)
                    self.state_stack.append(next_state)
                    print(f"      Goto State {next_state} via Non-Terminal '{lhs}'")
                else:
                    desc = f"Goto error: no transition for '{lhs}' from state {top_state}"
                    self._record(remaining, desc, 'error')
                    self.error_handler.report(line, col, f"LR {desc}")
                    success = False
                    break

        return success

    def _rule_text(self, rule_num):
        texts = {
            1: "E \u2192 E + T", 2: "E \u2192 T", 3: "T \u2192 T * F",
            4: "T \u2192 F", 5: "F \u2192 ( E )", 6: "F \u2192 id"
        }
        return texts.get(rule_num, "?")

    def _record(self, remaining_input, action, kind):
        self.trace_steps.append({
            'state_stack': ' '.join(str(s) for s in self.state_stack),
            'symbol_stack': ' '.join(self.symbol_stack) if self.symbol_stack else '\u03b5',
            'input': remaining_input,
            'action': action,
            'type': kind
        })