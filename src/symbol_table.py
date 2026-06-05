# CS471L Mini Compiler Project
# Module: Symbol Table Manager

class SymbolTable:
    def __init__(self):
        self.scopes = [{}] 
        self.current_level = 0

    def enter_scope(self):
        self.scopes.append({})
        self.current_level += 1

    def exit_scope(self):
        if self.current_level > 0:
            self.scopes.pop()
            self.current_level -= 1

    def insert(self, name, kind, type_, line):
        if name in self.scopes[self.current_level]:
            return False 
        self.scopes[self.current_level][name] = {
            'kind': kind, 'type': type_, 'scope': self.current_level, 'line': line
        }
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def dump(self):
        print("\n--- Symbol Table Dump ---")
        for i, scope in enumerate(self.scopes):
            print(f"Scope Level {i}: {scope}")