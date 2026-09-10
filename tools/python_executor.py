import io
import sys

from langchain_core.tools import tool


@tool
def python_executor(code: str) -> str:
    """
    Executes Python code for complex data analysis, filtering, or string manipulation.
    The code MUST output its final result using the print() function.

    Example input:
    import json
    data = [1, 2, 3, 4]
    print(sum(data) / len(data))
    """
    # Redirect standard output to capture the agent's print() statements
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    # Restrict execution scope to prevent accidental global overrides
    safe_globals = {"__builtins__": __builtins__}
    safe_locals = {}

    try:
        # Execute the code snippet
        exec(code, safe_globals, safe_locals)
        output = redirected_output.getvalue().strip()

        if not output:
            return "Code executed successfully, but nothing was printed. Use print() to output results."
        return output

    except Exception as e:
        return f"Execution Error: {type(e).__name__} - {str(e)}"

    finally:
        # Guarantee stdout is restored even if the agent writes broken code
        sys.stdout = old_stdout
