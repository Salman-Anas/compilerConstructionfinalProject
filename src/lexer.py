# CS471L Mini Compiler Project
# Module: Lexical Analyzer
import re

class Lexer:
    def __init__(self, source_code, error_handler):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.error_handler = error_handler
        
        self.keywords = {'program', 'begin', 'end'}
        self.token_exprs = [
            (r'[ \t]+', None),                
            (r'\n', 'NEWLINE'),               
            (r'\{[^}]*\}', None),             
            (r':=', 'ASSIGN'),                
            (r'[;.\+\*\(\)]', 'PUNCT'),       
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'ID'),
            (r'\d+', 'NUM')                   
        ]

    def get_next_token(self):
        if self.pos >= len(self.source):
            return ('EOF', 'EOF', self.line, self.col)

        sub_str = self.source[self.pos:]
        
        for pattern, tag in self.token_exprs:
            match = re.match(pattern, sub_str)
            if match:
                val = match.group(0)
                old_col = self.col
                
                self.pos += len(val)
                if tag == 'NEWLINE':
                    self.line += 1
                    self.col = 1
                    return self.get_next_token() 
                else:
                    self.col += len(val)

                if tag is None:
                    return self.get_next_token() 
                
                if tag == 'ID' and val.lower() in self.keywords:
                    tag = 'KEYWORD'
                
                return (tag, val, self.line, old_col)

        self.error_handler.report(self.line, self.col, f"Unrecognized character: {sub_str[0]}")
        self.pos += 1
        self.col += 1
        return self.get_next_token()