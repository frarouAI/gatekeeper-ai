import ast
import math
import random
import datetime
import typing
import itertools
import functools
import re
import collections
import operator
import copy
import json
import time
import statistics
import string

# Allowed standard library modules for sandbox
ALLOWED_MODULES = {
    'math': math,
    'random': random,
    'datetime': datetime,
    'typing': typing,
    'itertools': itertools,
    'functools': functools,
    're': re,
    'collections': collections,
    'operator': operator,
    'copy': copy,
    'json': json,
    'time': time,
    'statistics': statistics,
    'string': string
}


def safe_import(name, *args, **kwargs):
    """Restricted import that only allows whitelisted modules."""
    if name in ALLOWED_MODULES:
        return ALLOWED_MODULES[name]
    raise ImportError(f"Import of '{name}' is not allowed")


def detect_module_references(code: str) -> set:
    """Detect standard library module references in code using AST."""
    try:
        tree = ast.parse(code)
        modules = set()
        
        for node in ast.walk(tree):
            # Detect import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ALLOWED_MODULES:
                        modules.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module in ALLOWED_MODULES:
                    modules.add(node.module)
            # Detect patterns like: math.sqrt()
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    if node.value.id in ALLOWED_MODULES:
                        modules.add(node.value.id)
        
        return modules
    except SyntaxError:
        return set()


def execute_code(code: str, timeout: int = 5) -> dict:
    """
    Safely execute Python code in a restricted sandbox.
    
    Args:
        code: Python code to execute
        timeout: Max execution time in seconds
        
    Returns:
        dict with keys: success, output, error
    """
    # Build sandbox environment
    sandbox = {
        '__builtins__': {
            '__import__': safe_import,
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'pow': pow,
            'isinstance': isinstance,
            'type': type,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'AttributeError': AttributeError,
        }
    }
    
    # Pre-inject detected modules (optimization)
    referenced_modules = detect_module_references(code)
    for module_name in referenced_modules:
        sandbox[module_name] = ALLOWED_MODULES[module_name]
    
    try:
        # Execute code in sandbox
        exec(code, sandbox)
        return {
            "success": True,
            "output": "Code executed successfully",
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error": f"{type(e).__name__}: {str(e)}"
        }


if __name__ == "__main__":
    print("Test 1: Using import math")
    test_code1 = """
import math

def calculate_hypotenuse(a, b):
    return math.sqrt(a**2 + b**2)

result = calculate_hypotenuse(3, 4)
print(f"Hypotenuse: {result}")
"""
    result1 = execute_code(test_code1)
    print(json.dumps(result1, indent=2))
    
    print("\nTest 2: Direct math.sqrt usage")
    test_code2 = """
result = math.sqrt(16)
print(f"Square root of 16: {result}")
"""
    result2 = execute_code(test_code2)
    print(json.dumps(result2, indent=2))
    
    print("\nTest 3: Blocked import")
    test_code3 = """
import os
print(os.getcwd())
"""
    result3 = execute_code(test_code3)
    print(json.dumps(result3, indent=2))
