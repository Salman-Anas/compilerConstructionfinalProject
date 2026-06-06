# CS471L Mini Compiler Project
# Module: Recursive Descent Parser with AST + Call-Tree Generation

class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.type = node_type
        self.value = value
        self.children = children or []

    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'children': [child.to_dict() for child in self.children]
        }


class CallNode:
    """Node of the recursive-descent CALL TREE (the parse tree drawn in Image 1):
    non-terminals look like  program()  /  expression()  and terminals look like
    match('program') / match('id'). This is rendered as a top-down flow graph."""
    def __init__(self, label, kind='proc'):
        self.label = label
        self.kind = kind          # 'proc' (non-terminal) or 'match' (terminal leaf)
        self.children = []

    def to_dict(self):
        return {
            'label': self.label,
            'kind': self.kind,
            'children': [c.to_dict() for c in self.children]
        }


class RDParser:
    def __init__(self, lexer, sym_table, error_handler):
        self.lexer = lexer
        self.sym_table = sym_table
        self.error_handler = error_handler
        self.current_token = self.lexer.get_next_token()
        self.ast = None

        # --- call-tree state ---
        self.call_root = None
        self._stack = []

    # ---------- call-tree helpers ----------
    def _enter(self, label):
        node = CallNode(label, 'proc')
        if self._stack:
            self._stack[-1].children.append(node)
        else:
            self.call_root = node
        self._stack.append(node)
        return node

    def _leave(self):
        if self._stack:
            self._stack.pop()

    def _leaf(self, label, kind='match'):
        node = CallNode(label, kind)
        if self._stack:
            self._stack[-1].children.append(node)
        else:
            self.call_root = node

    # ---------- lexer/token helpers ----------
    def advance(self):
        self.current_token = self.lexer.get_next_token()

    def match(self, expected_tag, expected_val=None):
        tag, val, line, col = self.current_token
        print(f"[MATCH] Expected: {expected_val or expected_tag}, Found: {val}")

        if tag == expected_tag and (expected_val is None or val == expected_val):
            print(f"\u2713 Matched '{val}'")
            self._leaf(f"match('{val}')", 'match')
            self.advance()
        else:
            self.error_handler.report(line, col, f"Expected {expected_val or expected_tag}, found '{val}'")
            self._leaf(f"\u2717 expected {expected_val or expected_tag}", 'error')
            self.panic_mode_recovery()

    def panic_mode_recovery(self):
        print("-> Entering panic mode recovery...")
        while self.current_token[0] != 'EOF':
            if self.current_token[1] in {';', 'end', 'begin'}:
                break
            self.advance()

    # ---------- entry ----------
    def parse(self):
        print("\n--- Starting Recursive Descent Parse ---")
        self.ast = self.parse_program()

        if self.current_token[0] != 'EOF':
            self.error_handler.report(
                self.current_token[2],
                self.current_token[3],
                "Unexpected tokens at end of file"
            )
        print("--- Recursive Descent Parse Complete ---")
        return self.ast

    # ---------- grammar procedures ----------
    def parse_program(self):
        self._enter("program()")
        try:
            print("RD -> parse_program()")
            node = ASTNode('PROGRAM')

            self.match('KEYWORD', 'program')
            tag, name, line, col = self.current_token
            node.children.append(ASTNode('PROGRAM_NAME', name))

            self.match('ID')
            self.sym_table.insert(name, 'program', None, line)

            self.match('PUNCT', ';')
            self.match('KEYWORD', 'begin')

            self.sym_table.enter_scope()

            stmt_list = self.parse_stmt_list()
            node.children.append(stmt_list)

            self.match('KEYWORD', 'end')
            self.match('PUNCT', '.')

            self.sym_table.dump()
            self.sym_table.exit_scope()

            return node
        finally:
            self._leave()

    def parse_stmt_list(self):
        self._enter("stmt_list()")
        try:
            node = ASTNode('STATEMENT_LIST')
            stmt = self.parse_assignment()
            if stmt:
                node.children.append(stmt)

            stmt_prime = self.parse_stmt_list_prime()
            node.children.extend(stmt_prime.children)

            return node
        finally:
            self._leave()

    def parse_stmt_list_prime(self):
        self._enter("stmt_list'()")
        try:
            node = ASTNode('STATEMENT_LIST')

            if self.current_token[1] == ';':
                self.match('PUNCT', ';')
                stmt = self.parse_assignment()
                if stmt:
                    node.children.append(stmt)

                stmt_prime = self.parse_stmt_list_prime()
                node.children.extend(stmt_prime.children)

            return node
        finally:
            self._leave()

    def parse_assignment(self):
        self._enter("assignment()")
        try:
            print("RD -> parse_assignment()")
            tag, name, line, col = self.current_token

            if tag == 'ID':
                node = ASTNode('ASSIGNMENT')
                node.children.append(ASTNode('IDENTIFIER', name))

                if not self.sym_table.lookup(name):
                    self.sym_table.insert(name, 'variable', 'integer', line)

                self._leaf(f"match('{name}')", 'match')   # the identifier
                self.advance()
                self.match('ASSIGN', ':=')

                expr = self.parse_expression()
                node.children.append(expr)

                return node
            else:
                self.error_handler.report(line, col, "Expected Identifier in assignment")
                self._leaf("\u2717 expected identifier", 'error')
                self.panic_mode_recovery()
                return None
        finally:
            self._leave()

    def parse_expression(self):
        self._enter("expression()")
        try:
            node = ASTNode('EXPRESSION')
            term = self.parse_term()
            node.children.append(term)

            expr_prime = self.parse_expression_prime()
            if expr_prime.children:
                node = expr_prime
                node.children.insert(0, term)

            return node
        finally:
            self._leave()

    def parse_expression_prime(self):
        self._enter("expression'()")
        try:
            node = ASTNode('EXPRESSION')

            if self.current_token[1] == '+':
                self.match('PUNCT', '+')
                op_node = ASTNode('BINOP', '+')

                term = self.parse_term()
                op_node.children.append(term)

                expr_prime = self.parse_expression_prime()
                if expr_prime.children:
                    op_node.children.extend(expr_prime.children)

                node.children.append(op_node)

            return node
        finally:
            self._leave()

    def parse_term(self):
        self._enter("term()")
        try:
            print("RD -> parse_term()")
            node = ASTNode('TERM')

            factor = self.parse_factor()
            node.children.append(factor)

            term_prime = self.parse_term_prime()
            if term_prime.children:
                node = term_prime
                node.children.insert(0, factor)

            return node
        finally:
            self._leave()

    def parse_term_prime(self):
        self._enter("term'()")
        try:
            node = ASTNode('TERM')

            if self.current_token[1] == '*':
                self.match('PUNCT', '*')
                op_node = ASTNode('BINOP', '*')

                factor = self.parse_factor()
                op_node.children.append(factor)

                term_prime = self.parse_term_prime()
                if term_prime.children:
                    op_node.children.extend(term_prime.children)

                node.children.append(op_node)

            return node
        finally:
            self._leave()

    def parse_factor(self):
        self._enter("factor()")
        try:
            print("RD -> parse_factor()")
            tag, val, line, col = self.current_token

            if tag == 'ID':
                if not self.sym_table.lookup(val):
                    self.error_handler.report(line, col, f"Undeclared variable '{val}'")
                self._leaf(f"match('{val}')", 'match')
                self.advance()
                return ASTNode('IDENTIFIER', val)

            elif tag == 'NUM':
                self._leaf(f"match('{val}')", 'match')
                self.advance()
                return ASTNode('NUMBER', val)

            elif val == '(':
                self.match('PUNCT', '(')
                expr = self.parse_expression()
                self.match('PUNCT', ')')
                return expr

            else:
                self.error_handler.report(line, col, "Expected ID, NUM, or '('")
                self._leaf("\u2717 expected ID/NUM/(", 'error')
                self.panic_mode_recovery()
                return ASTNode('ERROR')
        finally:
            self._leave()