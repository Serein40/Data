"""
Functions for grading student code for a given question. Includes
the actual grader.check function and a way to tell if studentcode
calls a given function.
"""

import ast
from typing import List, Dict, Any
from grader_utils.assert_helpers import *
from grader_utils.grader_messages import (
    CUR_QUESTION_ERROR_PREFIX,
    MISSED_REQ_FUNC_FORMAT,
    MISSED_REQ_VAR_FORMAT,
    ASSERTION_FAILED_PREFIX,
)
from grader_utils.code_execution import execute_code


def check_student_code_against_requirements(
    student_code: str,
    required_functions: List[str],
    required_vars: List[str],
    assertions: str,
    current_question_warnings: List[str],
    current_question_errors: List[str],
    global_vars: Dict[str, Any],
) -> None:
    """Helper function for packages' grader check functions

    Executes student's code then checks that student code has:
    - used all required functions
    - defined all necessary variables
    - passes all test cases

    and then appends to the list of warnings and/or errors for the
    current question. Used to enforce consistency across all check
    functions in grader packages.
    """

    execute_code(
        student_code,
        global_vars,
        current_question_warnings,
        current_question_errors,
        CUR_QUESTION_ERROR_PREFIX,
    )

    for function_name in required_functions:
        if not _does_code_use(student_code, function_name):
            current_question_errors.append(MISSED_REQ_FUNC_FORMAT.format(function_name))

    for required_var in required_vars:
        if required_var not in global_vars:
            current_question_errors.append(MISSED_REQ_VAR_FORMAT.format(required_var))

    execute_code(
        assertions,
        global_vars,
        current_question_warnings,
        current_question_errors,
        ASSERTION_FAILED_PREFIX,
    )


def _does_code_use(code_snippet: str, name: str) -> bool:
    """Uses ast to tell if code contains a call to a specific function or operator.

    For a list of usable operator names, check
    https://docs.python.org/3/library/ast.html

    Parameters:
        code_snippet: A string containing Python code to be analyzed
        name: The name of the function or ast operator to look for in the code snippet
    """

    class CustomNodeVisitor(ast.NodeVisitor):
        """Extends ast's NoteVisitor to look for functions or operators"""

        def __init__(self):
            self.found = False

        def visit(self, node):
            """Traverse the abstract syntax tree to check for the function call or operator"""

            if isinstance(node, ast.Call):
                full_name = self.get_full_name(node.func)
                if full_name == name:
                    self.found = True
            elif (
                isinstance(node, ast.BinOp)
                or isinstance(node, ast.BoolOp)
                or isinstance(node, ast.UnaryOp)
            ):
                op_name = node.op.__class__.__name__
                if op_name == name:
                    self.found = True
            self.generic_visit(node)

        def get_full_name(self, node):
            """Recursively retrieves the full name of a function being called

            This inclues attribute accesses (e.g., "module.function").
            """

            if isinstance(node, ast.Attribute):
                return self.get_full_name(node.value) + "." + node.attr
            elif isinstance(node, ast.Name):
                return node.id
            return ""

    tree = ast.parse(code_snippet)
    visitor = CustomNodeVisitor()
    visitor.visit(tree)
    return visitor.found
