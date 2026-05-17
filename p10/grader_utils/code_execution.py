"""
Helper functions for executing code. Includes functionality
for suppressing printed output and safely executing code without
modifying global variables or taking too long.
"""

import builtins
import threading
import sys
import os
from typing import List, Dict, Any
from contextlib import contextmanager
import matplotlib
import matplotlib.pyplot as plt

CODE_MAX_EXECUTION_TIME = 60  # in seconds


def timeout_handler() -> None:
    """Helper function for execute_code to trigger when code has taken too long"""

    raise RuntimeError(
        "Execution timed out in our grader system. Please modify your code so it runs faster."
    )


def execute_code(
    code: str,
    global_vars: Dict[str, Any],
    warnings_list: List[str],
    errors_list: List[str],
    error_prefix: str,
) -> None:
    """Execute the code and record any warnings or errors.

    Detects and warns about changes to pre-existing global and builtin
    variables when running student code. This helps prevent unintended
    side effects later in the notebook. Uses a timeout to prevent execution
    from lasting too long.

    Parameters:
        code: Python code to run that potentially contains errors
        global_vars: Dictionary mapping names of global variables to their values
        warnings_list: Records any detected warning messages
        errors_list: Records strings with error_msg and exception text if any occur
        error_prefix: Start of error message to display to the student. Example:
            if desired message is f"Test case failed: {e}", then prefix is "Test case failed: "
    """

    before_exec_globals = global_vars.copy()
    builtin_identifiers = dir(builtins)

    timer = threading.Timer(CODE_MAX_EXECUTION_TIME, timeout_handler)
    timer.start()

    try:
        exec(code, global_vars)
    except Exception as e:
        errors_list.append(f"{error_prefix}{e}")
    finally:
        timer.cancel()  # code finished before alarm went off, cancel the alarm

    after_exec_globals = global_vars.copy()

    variables_defined_by_exec = set(after_exec_globals) - set(before_exec_globals)
    for var_name in variables_defined_by_exec:
        if var_name in builtin_identifiers:
            warnings_list.append(
                f"Built-in function '{var_name}' was modified. You should never overwrite these."
            )


@contextmanager
def suppress_output():
    """Temporarily suppresses stdout, stderr, and MatplolLib output.

    Redirects stdout and stderr to os.devnull, effectively silencing
    any print statements or error messages within the context. Once
    the context is exited, the original stdout and stderr are restored.
    Also sets Matplotlib to a non-interactive backend to suppress plot
    displays and closes any lingering figures after execution.

    This is useful when running executing code in cells above the current
    grader.check call, since we don't want that output to show up
    when the user is expecting information related to the current question.

    Usage:
        with suppress_output():
            # Code with suppressed output
    """

    with open(os.devnull, "w", encoding="utf-8") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_backend = matplotlib.get_backend()
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            matplotlib.use("Agg")
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            matplotlib.use(old_backend)
            plt.close("all")
