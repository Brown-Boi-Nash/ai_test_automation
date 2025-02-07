import ast

def detect_edge_cases(code_snippet):
    """Analyzes a Python function and detects possible edge cases."""
    try:
        tree = ast.parse(code_snippet)
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name

                if any(isinstance(child, ast.BinOp) and isinstance(child.op, ast.Div) for child in ast.walk(node)):
                    issues.append(f"Function '{function_name}' performs division, check for divide by zero errors.")

                if not any(isinstance(child, ast.Try) for child in ast.walk(node)):
                    issues.append(f"Function '{function_name}' has no exception handling.")

        return issues

    except Exception as e:
        return [f"Error analyzing function: {str(e)}"]

# Example usage
if __name__ == "__main__":
    sample_function = """
    def divide(a, b):
        return a / b
    """
    detected_issues = detect_edge_cases(sample_function)
    for issue in detected_issues:
        print("🔍 Static Analysis Issue:", issue)
