"""
Helper functions that are intented to be used in the assert cells of master notebook projects.
Many of the checks that are placed into these assert cells are repetitive, checking
first that the variable the student is supposed to define is of the proper type,
and then checking something about its value.  By calling functions from this assert_helpers
file, this repetitive nature can be avoided.
"""

import math
from collections import Counter
import pandas as pd
import numpy as np


_FLOAT_ABS_TOL = 1e-9
_FLOAT_REL_TOL = 1e-9


def _is_container(x):
    return isinstance(x, (dict, list, tuple, set))


def _fmt_path(root, path):
    s = root
    for p in path:
        s += f"[{p}]" if isinstance(p, int) else f"[{p!r}]"
    return s


def _err_here(name, path, msg):
    raise AssertionError(f"For {_fmt_path(name, path)}: {msg}")


def _expect_not_ellipsis(name, under_eval):
    if under_eval == Ellipsis:
        raise AssertionError(
            f"For {name}: replace the ... with the correct Python code.\n"
        )


def _type_check(name, under_eval, expected_value, feedback_level: int):
    if type(under_eval) is not type(expected_value):
        if feedback_level >= 1:
            raise AssertionError(
                f"For {name}: expected type {type(expected_value).__name__}, "
                f"but got {type(under_eval).__name__}.\n"
            )
        raise AssertionError(f"For {name}: incorrect type.\n")


def _raise_for_unequal_values(name, under_eval, expected, feedback_level: int):
    if feedback_level >= 1:
        raise AssertionError(
            f"For {name}: expected value '{expected}', but got '{under_eval}'.\n"
        )
    raise AssertionError(f"For {name}: incorrect value.\n")


def _value_check(name, under_eval, expected, feedback_level: int):
    if isinstance(under_eval, float) and isinstance(expected, float):
        if math.isnan(under_eval) and math.isnan(expected):
            return
        if not math.isclose(
            under_eval, expected, rel_tol=_FLOAT_REL_TOL, abs_tol=_FLOAT_ABS_TOL
        ):
            _raise_for_unequal_values(name, under_eval, expected, feedback_level)
        return
    if under_eval != expected:
        _raise_for_unequal_values(name, under_eval, expected, feedback_level)


def _length_check(name, under_eval_container, expected_container, feedback_level: int):
    lu, le = len(under_eval_container), len(expected_container)
    if lu != le:
        if feedback_level >= 1:
            raise AssertionError(f"For {name}: expected length {le}, but got {lu}.\n")
        raise AssertionError(f"For {name}: incorrect length.\n")


def assert_check(
    name,
    under_eval,
    expected_value,
    reorder: bool = False,
    feedback_level: int = 1,
    _path: tuple = (),
):
    _expect_not_ellipsis(_fmt_path(name, _path), under_eval)
    if not _is_container(expected_value):
        _type_check(_fmt_path(name, _path), under_eval, expected_value, feedback_level)
        _value_check(_fmt_path(name, _path), under_eval, expected_value, feedback_level)
        return
    assert_check_container(
        name,
        under_eval,
        expected_value,
        reorder=reorder,
        feedback_level=feedback_level,
        _path=_path,
    )


def assert_check_simple(
    name: str, under_eval: any, expected: any, feedback_level: int = 1
) -> None:
    _expect_not_ellipsis(name, under_eval)
    _type_check(name, under_eval, expected, feedback_level)
    _value_check(name, under_eval, expected, feedback_level)


def _assert_dict(
    name,
    under_eval: dict,
    expected_value: dict,
    feedback_level: int,
    reorder: bool,  # unused but kept for uniform signature
    _path: tuple,
):
    # 1) Report missing/extra keys at this level
    missing = [k for k in expected_value if k not in under_eval]
    extra = [k for k in under_eval if k not in expected_value]
    if missing or extra:
        if feedback_level == 0:
            _err_here(name, _path, "incorrect value")
        if feedback_level == 1:
            if missing:
                _err_here(name, _path, f"it is missing the key {missing[0]!r}.")
            _err_here(
                name, _path, f"you have the key {extra[0]!r} which shouldn't be there."
            )
        _err_here(
            name, _path, f"expected value '{expected_value}', but got '{under_eval}'."
        )

    # 2) For common keys, recurse or compare directly and let the deepest error surface
    for k in expected_value.keys() & under_eval.keys():
        ev, uv = expected_value[k], under_eval[k]
        p = _path + (k,)
        if _is_container(ev) or isinstance(ev, pd.DataFrame):
            assert_check(name, uv, ev, reorder, feedback_level, p)
        else:
            _value_check(_fmt_path(name, p), uv, ev, feedback_level)


def _assert_list(
    name,
    under_eval: list,
    expected_value: list,
    reorder: bool,
    feedback_level: int,
    _path: tuple,
):
    if reorder:
        if any(_is_container(x) or isinstance(x, pd.DataFrame) for x in expected_value):
            _err_here(
                name,
                _path,
                "cannot reorder lists containing nested containers; set reorder=False.",
            )
        try:
            if sorted(under_eval) == sorted(expected_value):
                return
        except TypeError:
            try:
                if Counter(under_eval) == Counter(expected_value):
                    return
            except TypeError:
                _err_here(
                    name,
                    _path,
                    "cannot reorder unorderable and unhashable elements; set reorder=False or provide comparable elements.",
                )
        if feedback_level == 0:
            _err_here(name, _path, "incorrect value")
        if feedback_level == 1:
            diff_missing = Counter(expected_value) - Counter(under_eval)
            if diff_missing:
                bad = next(iter(diff_missing.elements()))
                _err_here(name, _path, f"missing element {bad!r} when order ignored.")
            diff_extra = Counter(under_eval) - Counter(expected_value)
            if diff_extra:
                bad = next(iter(diff_extra.elements()))
                _err_here(
                    name, _path, f"unexpected element {bad!r} when order ignored."
                )
            _err_here(name, _path, "incorrect value")
        _err_here(
            name, _path, f"expected value '{expected_value}' but got '{under_eval}'."
        )

    # Elementwise compare (no try/except — let deepest error bubble up)
    for i, (a, b) in enumerate(zip(under_eval, expected_value)):
        p = _path + (i,)
        if _is_container(b) or isinstance(b, pd.DataFrame):
            assert_check(name, a, b, reorder, feedback_level, p)
        else:
            _value_check(_fmt_path(name, p), a, b, feedback_level)


def _assert_tuple(
    name,
    under_eval: tuple,
    expected_value: tuple,
    feedback_level: int,
    reorder: bool,  # unused for tuples; kept for signature parity
    _path: tuple,
):
    # Elementwise compare (no try/except — let deepest error bubble up)
    for i, (a, b) in enumerate(zip(under_eval, expected_value)):
        p = _path + (i,)
        if _is_container(b) or isinstance(b, pd.DataFrame):
            assert_check(name, a, b, reorder, feedback_level, p)
        else:
            _value_check(_fmt_path(name, p), a, b, feedback_level)


def _assert_set(
    name, under_eval: set, expected_value: set, feedback_level: int, _path: tuple
):
    missing = expected_value - under_eval
    extra = under_eval - expected_value
    if not (missing or extra):
        return
    if feedback_level == 0:
        _err_here(name, _path, "incorrect value")
    if feedback_level == 1:
        if missing:
            _err_here(name, _path, f"missing element {next(iter(missing))!r}.")
        _err_here(name, _path, f"unexpected element {next(iter(extra))!r}.")
    _err_here(name, _path, f"expected value '{expected_value}' but got '{under_eval}'.")


def assert_check_container(
    name: str,
    under_eval,
    expected_value,
    reorder: bool = False,
    feedback_level: int = 1,
    _path: tuple = (),
) -> None:
    disp = _fmt_path(name, _path)
    _expect_not_ellipsis(disp, under_eval)
    _type_check(disp, under_eval, expected_value, feedback_level)
    if isinstance(expected_value, (list, tuple)):
        _length_check(disp, under_eval, expected_value, feedback_level)

    if isinstance(expected_value, dict):
        _assert_dict(name, under_eval, expected_value, feedback_level, reorder, _path)
    elif isinstance(expected_value, set):
        _assert_set(name, under_eval, expected_value, feedback_level, _path)
    elif isinstance(expected_value, list):
        _assert_list(name, under_eval, expected_value, reorder, feedback_level, _path)
    elif isinstance(expected_value, tuple):
        _assert_tuple(name, under_eval, expected_value, feedback_level, reorder, _path)
    else:
        # Fallback exact compare for other container-likes
        if expected_value != under_eval:
            if feedback_level > 1:
                _err_here(
                    name,
                    _path,
                    f"expected value '{expected_value}' but got '{under_eval}'.",
                )
            _err_here(name, _path, "incorrect value")


def assert_check_dataframe(name, under_eval, expected_df, feedback_level=1):
    """Cellwise DF comparison with float tolerance; requires same shape, columns, index."""
    if not isinstance(expected_df, pd.DataFrame):
        raise AssertionError(f"For {name}: expected a DataFrame to compare against.")
    if not isinstance(under_eval, pd.DataFrame):
        raise AssertionError(
            f"For {name}: expected type DataFrame, but got {type(under_eval).__name__}."
        )

    # shape
    if under_eval.shape != expected_df.shape:
        if feedback_level == 0:
            raise AssertionError(f"For {name}: DataFrame shape mismatch.")
        raise AssertionError(
            f"For {name}: has shape {under_eval.shape}, but expected {expected_df.shape}."
        )

    # columns
    if not under_eval.columns.equals(expected_df.columns):
        if feedback_level == 0:
            raise AssertionError(f"For {name}: DataFrame columns mismatch.")
        raise AssertionError(
            f"For {name}: has columns {list(under_eval.columns)}, "
            f"but expected {list(expected_df.columns)}."
        )

    # index
    if not under_eval.index.equals(expected_df.index):
        if feedback_level == 0:
            raise AssertionError(f"For {name}: DataFrame index mismatch.")
        raise AssertionError(
            f"For {name}: has index {list(under_eval.index)}, "
            f"but expected {list(expected_df.index)}."
        )

    n_rows, n_cols = expected_df.shape
    matches = np.ones((n_rows, n_cols), dtype=bool)

    # numeric vs non-numeric
    numeric_cols = [
        col
        for col in expected_df.columns
        if pd.api.types.is_numeric_dtype(expected_df[col])
        and pd.api.types.is_numeric_dtype(under_eval[col])
    ]
    non_numeric_cols = [c for c in expected_df.columns if c not in numeric_cols]

    # numeric compare (with tolerances)
    if numeric_cols:
        exp_num = expected_df[numeric_cols].to_numpy()
        got_num = under_eval[numeric_cols].to_numpy()
        num_equal = np.isclose(
            got_num, exp_num, rtol=_FLOAT_REL_TOL, atol=_FLOAT_ABS_TOL, equal_nan=True
        )
        col_idx = {c: i for i, c in enumerate(expected_df.columns)}
        for k, c in enumerate(numeric_cols):
            j = col_idx[c]
            matches[:, j] = num_equal[:, k]

    # non-numeric compare (exact, NaN==NaN)
    if non_numeric_cols:
        exp_obj = expected_df[non_numeric_cols]
        got_obj = under_eval[non_numeric_cols]
        exp_arr = exp_obj.to_numpy()
        got_arr = got_obj.to_numpy()
        try:
            obj_equal = got_arr == exp_arr
        except Exception:
            obj_equal = np.vectorize(lambda x, y: x == y)(got_arr, exp_arr)
        both_nan = pd.isna(got_obj).to_numpy() & pd.isna(exp_obj).to_numpy()
        obj_equal = obj_equal | both_nan
        col_idx = {c: i for i, c in enumerate(expected_df.columns)}
        for k, c in enumerate(non_numeric_cols):
            j = col_idx[c]
            matches[:, j] = obj_equal[:, k]

    if matches.all():
        return

    # first mismatch
    i, j = np.argwhere(~matches)[0]
    idx_label = expected_df.index[i]
    col_label = expected_df.columns[j]
    expected_val = expected_df.iloc[i, j]
    actual_val = under_eval.iloc[i, j]

    exp_display = repr(expected_val) if isinstance(expected_val, str) else expected_val
    act_display = repr(actual_val) if isinstance(actual_val, str) else actual_val

    if isinstance(idx_label, (int, float, np.integer, np.floating)):
        loc_desc = (
            f"index {idx_label}" if idx_label == i else f"row {i} (index {idx_label})"
        )
    else:
        loc_desc = f"index {idx_label}"

    if feedback_level == 0:
        raise AssertionError(f"For {name}: the value is not correct.")
    elif feedback_level == 1:
        raise AssertionError(
            f"For {name}: at {loc_desc}, column '{col_label}', expected {exp_display} but got {act_display}."
        )
    else:
        expected_row = expected_df.iloc[i]
        actual_row = under_eval.iloc[i]
        raise AssertionError(
            f"For {name}: at {loc_desc},\nExpected row:\n\n{expected_row}\n\nActual row:\n\n{actual_row}"
        )
