import sys
import os

# Add the project root to Python's module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ollama
import logging
import re
from models.static_analyzer import detect_edge_cases

# Configure logging
LOG_FILE = "logs/test_automation.log"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Path to store test failure logs for AI self-learning
FAILURE_LOG = "results/test_failures.log"
os.makedirs("results", exist_ok=True)

def extract_function_details(code_snippet):
    """Extracts function name and docstring from a given code snippet."""
    function_name = "Unknown Function"
    docstring = ""

    try:
        function_name_match = re.search(r"def (\w+)\(", code_snippet)
        docstring_match = re.search(r'"""(.*?)"""', code_snippet, re.DOTALL)

        function_name = function_name_match.group(1) if function_name_match else function_name
        docstring = docstring_match.group(1).strip() if docstring_match else docstring
    except Exception as e:
        logging.error(f"Error extracting function details: {e}")

    return function_name, docstring

def get_past_failures():
    """Reads past test failure logs to improve AI-generated test cases."""
    if os.path.exists(FAILURE_LOG):
        with open(FAILURE_LOG, "r") as f:
            return f.read().strip()
    return ""

def generate_test_case(code_snippet, test_type="unit"):
    """Uses Ollama's LLM to generate test cases dynamically."""
    function_name, docstring = extract_function_details(code_snippet)
    static_issues = detect_edge_cases(code_snippet)
    failure_context = get_past_failures()

    prompt = f"""
    You are an expert software tester. Given the following Python function, generate a {test_type} test case using pytest.

    Function Name: {function_name}
    Function Docstring: {docstring if docstring else "No documentation provided"}

    Function Code:
    ```python
    {code_snippet}
    ```

    Based on static analysis, consider these potential issues:
    {', '.join(static_issues) if static_issues else "No major issues detected."}

    Ensure the test case covers:
    - Edge cases (like invalid inputs)
    - Exception handling
    - Performance tests if applicable
    """

    if failure_context:
        prompt += f"\nAlso, improve the test cases based on these past test failures:\n{failure_context}"

    try:
        response = ollama.chat(model="qwen2.5-coder", messages=[{"role": "user", "content": prompt}])
        test_code = clean_generated_code(response["message"]["content"])
        logging.info(f"Generated Test Case for {function_name}:\n{test_code}")
        return test_code
    except Exception as e:
        logging.error(f"Error generating test case: {e}")
        return ""

def clean_generated_code(code):
    """Removes surrounding triple backticks and 'python' specifier if present."""
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()

def save_test_case(test_code, file_path="tests/ai_generated_tests.py"):
    """Saves the cleaned test case into a file for execution."""
    cleaned_code = clean_generated_code(test_code)
    with open(file_path, "w") as f:
        f.write(cleaned_code)
    logging.info(f"Test case saved to {file_path}")

# Example: Generate a test for a sample function
if __name__ == "__main__":
    sample_function = """
    def divide(a, b):
        \"\"\" This function divides two numbers. If b is zero, it raises an exception. \"\"\"
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    """
    
    test_case = generate_test_case(sample_function)
    save_test_case(test_case)
    print("Test case generated and saved.")
