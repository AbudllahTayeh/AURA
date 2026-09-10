import ast
import operator

from langchain_core.tools import tool

# Map AST node types to Python's built-in mathematical operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_evaluate(node):
    """Recursively evaluates the mathematical AST nodes."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Only numbers are allowed, got: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        return OPERATORS[type(node.op)](
            safe_evaluate(node.left), safe_evaluate(node.right)
        )
    elif isinstance(node, ast.UnaryOp):
        return OPERATORS[type(node.op)](safe_evaluate(node.operand))
    else:
        raise TypeError(f"Unsupported mathematical operation: {type(node)}")


@tool
def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression safely.
    Use this tool to calculate trade-offs, percentages, costs, and comparisons.
    Example input: '(25.5 * 300) / 0.5'
    """
    try:
        # Parse the string into an AST evaluation node
        tree = ast.parse(expression.strip(), mode="eval").body
        result = safe_evaluate(tree)
        return str(round(result, 4))
    except KeyError:
        return "Error: Unsupported operator in expression."
    except Exception as e:
        return f"Error evaluating mathematical expression: {str(e)}"
