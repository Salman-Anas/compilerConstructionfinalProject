# CS471L Mini Compiler Project
# Module: Symbol Table Manager

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
        self.current_level = 0
        # Persistent log of EVERY symbol that was ever inserted.
        # This is what the UI reads, so symbols are not lost when a scope is popped.
        self.records = []

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
        entry = {'kind': kind, 'type': type_, 'scope': self.current_level, 'line': line}
        self.scopes[self.current_level][name] = entry
        # keep a permanent copy for display
        self.records.append({
            'name': name, 'kind': kind, 'type': type_,
            'scope': self.current_level, 'line': line
        })
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def dump(self):
        print("\n--- Symbol Table Dump ---")
        if not self.records:
            print("(empty)")
            return
        max_level = max(r['scope'] for r in self.records)
        for lvl in range(max_level + 1):
            entries = {r['name']: {k: v for k, v in r.items() if k != 'name'}
                       for r in self.records if r['scope'] == lvl}
            print(f"Scope Level {lvl}: {entries}")