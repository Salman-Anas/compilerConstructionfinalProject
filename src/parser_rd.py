# CS471L Mini Compiler Project
# Module: Recursive Descent Parser

class RDParser:
    def __init__(self, lexer, sym_table, error_handler):
        self.lexer = lexer
        self.sym_table = sym_table
        self.error_handler = error_handler
        self.current_token = self.lexer.get_next_token()

    def advance(self):
        self.current_token = self.lexer.get_next_token()

    def match(self, expected_tag, expected_val=None):
        tag, val, line, col = self.current_token

        print(
            f"[MATCH] Expected: {expected_val or expected_tag}, "
            f"Found: {val}"
        )

        if tag == expected_tag and (expected_val is None or val == expected_val):
            print(f"✓ Matched '{val}'")
            self.advance()
        else:
            self.error_handler.report(
                line,
                col,
                f"Expected {expected_val or expected_tag}, found '{val}'"
            )
            self.panic_mode_recovery()

    def panic_mode_recovery(self):
        print("-> Entering panic mode recovery...")
        while self.current_token[0] != 'EOF':
            if self.current_token[1] in {';', 'end', 'begin'}:
                break
            self.advance()

    def parse(self):
        print("\n--- Starting Recursive Descent Parse ---")

        self.parse_program()

        if self.current_token[0] != 'EOF':
            self.error_handler.report(
                self.current_token[2],
                self.current_token[3],
                "Unexpected tokens at end of file"
            )

        print("--- Recursive Descent Parse Complete ---")
    def parse_program(self):
        print("RD -> parse_program()")

        self.match('KEYWORD', 'program')

        tag, name, line, col = self.current_token

        self.match('ID')
        self.sym_table.insert(name, 'program', None, line)

        self.match('PUNCT', ';')
        self.match('KEYWORD', 'begin')

        self.sym_table.enter_scope()

        self.parse_stmt_list()

        self.match('KEYWORD', 'end')
        self.match('PUNCT', '.')

        self.sym_table.dump()
        self.sym_table.exit_scope()

    def parse_stmt_list(self):
        self.parse_assignment()
        self.parse_stmt_list_prime()

    def parse_stmt_list_prime(self):
        if self.current_token[1] == ';':
            self.match('PUNCT', ';')
            self.parse_assignment()
            self.parse_stmt_list_prime()

    def parse_assignment(self):
        print("RD -> parse_assignment()")

        tag, name, line, col = self.current_token

        if tag == 'ID':

            if not self.sym_table.lookup(name):
                self.sym_table.insert(
                    name,
                    'variable',
                    'integer',
                    line
                )

            self.advance()

            self.match('ASSIGN', ':=')

            self.parse_expression()

        else:
            self.error_handler.report(
                line,
                col,
                "Expected Identifier in assignment"
            )
            self.panic_mode_recovery()

    def parse_expression(self):
        self.parse_term()
        self.parse_expression_prime()

    def parse_expression_prime(self):
        if self.current_token[1] == '+':
            self.match('PUNCT', '+')
            self.parse_term()
            self.parse_expression_prime()

    def parse_term(self):
        print("RD -> parse_term()")

        self.parse_factor()
        self.parse_term_prime()

    def parse_term_prime(self):
        if self.current_token[1] == '*':
            self.match('PUNCT', '*')
            self.parse_factor()
            self.parse_term_prime()

    def parse_factor(self):
        print("RD -> parse_factor()")

        tag, val, line, col = self.current_token

        if tag == 'ID':

            if not self.sym_table.lookup(val):
                self.error_handler.report(
                    line,
                    col,
                    f"Undeclared variable '{val}'"
                )

            self.advance()

        elif tag == 'NUM':
            self.advance()

        elif val == '(':

            self.match('PUNCT', '(')

            self.parse_expression()

            self.match('PUNCT', ')')

        else:

            self.error_handler.report(
                line,
                col,
                "Expected ID, NUM, or '('"
            )

            self.panic_mode_recovery()