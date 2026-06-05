# CS471L Mini Compiler Project
# Module: Error Handler

class ErrorHandler:
    def __init__(self):
        self.errors = []

    def report(self, line, col, message):
        error_msg = f"Error at Line {line}, Col {col}: {message}"
        print(error_msg)
        self.errors.append(error_msg)

    def summarize(self):
        print("\n--- Compilation Summary ---")
        if not self.errors:
            print("0 Errors found. Compilation successful!")
        else:
            print(f"{len(self.errors)} Errors detected.")