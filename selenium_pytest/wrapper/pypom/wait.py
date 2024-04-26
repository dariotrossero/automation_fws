"""Wait related logic"""

import collections
import re
import time
from numbers import Real
from typing import (Any, Callable, Container, Iterable, Pattern, Sized, Tuple, Type, TypeVar)

Regex = TypeVar('Regex', str, Pattern)


class WaitTimeoutError(Exception):
    pass


POLL_FREQUENCY = 0.1  # How long to sleep in between calls to the method


def safe_repr(obj: Any) -> str:
    """Return a string representation of the given object.

    Supports instances of Old Style classes.
    """
    if hasattr(obj, '__qualname__'):
        return obj.__qualname__
    try:
        result = repr(obj)
    except Exception:  # pylint: disable=W0703
        result = object.__repr__(obj)
    return result.replace('{', '{{').replace('}', '}}')


def until(
    func: Callable[..., Tuple[Any, bool]],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    condition: str = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Calls the function provided until the second item
    in the returned tuple is True

    Args:
        func: a function that returns a tuple of two values, the last val
        of the function under test or None, and a bool representing
        whether the 'until' expression was met
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        condition: string version of failed 'until' expression, use {actual}
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    poll_time = poll_time or POLL_FREQUENCY
    end_time = time.time() + timeout
    ignored_exceptions = ignored_exceptions or tuple()

    last_val = None

    while True:
        exc = None
        try:
            last_val, condition_met = func()
            if condition_met:
                return last_val
        except tuple(ignored_exceptions) as e:
            exc = e

        time.sleep(poll_time)
        if time.time() <= end_time:
            continue

        if not raise_on_timeout:
            return last_val

        msg = '\n' + msg if msg else ''
        if condition:
            condition = condition.format(actual=safe_repr(last_val))
            msg = f"{condition} was still not true after {timeout} seconds.{msg}"

        if exc:
            raise WaitTimeoutError(msg) from exc
        raise WaitTimeoutError(msg)


def until_almost_equal(
    value: Real,
    func: Callable[..., Any],
    timeout: int,
    decimal_places: int = None,
    delta: Real = None,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() almost equal value

    Almost equal is defined as either:
      * x == (y ± delta)
      * round(abs(x - y), decimal places)

    Args:
        value: number to compare against
        func: func to poll
        timeout: seconds to poll
        decimal_places: how many places to round to
        delta: minimum difference between value and func
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    if delta is not None and decimal_places is not None:
        raise TypeError("specify delta or decimal_places not both")

    def assert_function():
        result = func()
        if result == value:
            return result, True

        if delta is not None:
            return result, abs(result - value) <= delta
        else:
            places = 7 if decimal_places is None else decimal_places
            return result, round(abs(value-result), places) == 0

    cond_repr = f"{{actual}} almost equal to {value}"

    return until(
        assert_function,
        timeout=timeout,
        condition=cond_repr,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_almost_equal(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    decimal_places: int = None,
    delta: Real = None,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() not almost equal value

    Almost equal is defined as either:
    * x == (y ± delta)
    * round(abs(x - y), decimal places)

    Args:
        value: number to compare against
        func: func to poll
        timeout: seconds to poll
        decimal_places: how many places to round to
        delta: maximum difference between value and func
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    if delta is not None and decimal_places is not None:
        raise TypeError("specify delta or places not both")

    def assert_function():
        result = func()
        if delta is not None:
            return result, abs(result - value) > delta
        else:
            places = 7 if decimal_places is None else decimal_places
            return result, round(abs(result-value), places) != 0

    cond_repr = f"{{actual}} not almost equal to {safe_repr(value)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_contains(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until value in func()

    Args:
        value: value to check for membership
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        container = func()
        return container, value in container

    cond_repr = f"{value} in {{actual}}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_contains(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until value not in func()

    Args:
        value: value to check for membership
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, value not in result

    cond_repr = f"{value} not in {{actual}}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_in(
    container: Container,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() in container

    Args:
        container: container to check
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result in container

    cond_repr = f"{{actual}} in {safe_repr(container)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_in(
    container: Container,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() not in container

    Args:
        container: container to check
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result not in container

    cond_repr = f"{{actual}} not in {safe_repr(container)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_members_in(
    members: Iterable,
    func: Callable[..., Container],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until all members in func()

    Args:
        members: items to check for membership
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        container = func()
        return container, all(item in container for item in members)

    cond_repr = f"All items in {{actual}} for item in {safe_repr(members)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_members_not_in(
    members: Iterable,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until all members not in func()

    Args:
        members: items to check for membership
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, all(item not in result for item in members)

    cond_repr = f"All items not in {{actual}} for item in {safe_repr(members)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_counts_equal(
    seq: Iterable,
    func: Callable[..., Iterable],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until same elements appear in func() and seq

    An unordered sequence comparison asserting that the same elements,
    regardless of order.  If the same element occurs more than once,
    it verifies that the elements occur the same number of times.

        self.assertEqual(Counter(list(first)),
                         Counter(list(second)))

     Example:
        - [0, 1, 1] and [1, 0, 1] compare equal.
        - [0, 0, 1] and [0, 1] compare unequal.

    Args:
        seq: sequence to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        # Stringify each element in the sequence to avoid an unhashable
        output = func()
        first_seq = map(safe_repr, list(output))
        second_seq = map(safe_repr, list(seq))
        # error
        # Use the update method to avoid IDE warnings about the
        # constructor
        first = collections.Counter()
        first.update(first_seq)
        second = collections.Counter()
        second.update(second_seq)
        return output, first == second

    cond_repr = (
        f"collections.Counter({{actual}}) == collections.Counter({safe_repr(seq)})"
    )

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_equal(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() == value

    Args:
        value: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result == value

    cond_repr = f"{{actual}} == {safe_repr(value)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_equal(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() != value

    Args:
        value: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result != value

    cond_repr = f"{{actual}} != {safe_repr(value)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_true(
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until bool(func()) == True

    Args:
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, bool(result)

    cond_repr = "bool({actual}) is True"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_false(
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until bool(func()) == False

    Args:
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        expr = func()
        return expr, not expr

    cond_repr = "bool({actual}) is False"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_greater(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() > value

    Args:
        value: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result > value

    cond_repr = f"{{actual}} > {safe_repr(value)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_greater_equal(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() >= value

    Args:
        value: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result >= value

    cond_repr = f"{{actual}} >= {safe_repr(value)}"

    return until(
        assert_function,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        condition=cond_repr,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_less(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() < value

    Args:
        value: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result < value

    cond_repr = f"{{actual}} < {safe_repr(value)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_less_equal(
    value: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() <= value

    Args:
        value: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result <= value

    cond_repr = f"{{actual}} <= {safe_repr(value)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_is(
    expr: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() is expr

    Args:
        expr: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, result is expr

    cond_repr = f"{{actual}} is {safe_repr(expr)}"

    return until(
        assert_function,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        condition=cond_repr,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_is_not(
    expr: Any,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() is not expr

    Args:
        expr: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        expr1 = func()
        expr2 = expr
        return expr1, expr1 is not expr2

    cond_repr = f"{{actual}} is not {safe_repr(expr)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_isinstance(
    cls: type,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until isinstance(func(), cls)

    Args:
        cls: cls to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        obj = func()
        return obj, isinstance(obj, cls)

    cond_repr = f"isinstance({{actual}}, {safe_repr(cls)})"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_isinstance(
    cls: type,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until not isinstance(func(), cls)

    Args:
        cls: cls to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        obj = func()
        return obj, not isinstance(obj, cls)

    cond_repr = f"not isinstance({{actual}}, {safe_repr(cls)})"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_is_none(
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() is None

    Args:
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        expr = func()
        return expr, expr is None

    cond_repr = "{actual} is None"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_is_not_none(
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() is not None

    Args:
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        expr = func()
        return expr, expr is not None

    cond_repr = "{actual} is not None"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_lengths_equal(
    value: Sized,
    func: Callable[..., Sized],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until len(func() == len(value)

    Args:
        value: sized object to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        result = func()
        return result, len(result) == len(value)

    cond_repr = f"len({{actual}}) == len({safe_repr(value)})"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_raises(
    expected_exception: Type[Exception],
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() raises expected_exception

    Fails immediately if any other type of exception is raised

    Args:
        expected_exception: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        try:
            result = func()
        except expected_exception as exc:
            return exc, True
        return result, False

    cond_repr = f"{getattr(func, '__name__', str(func))} raises {safe_repr(expected_exception)}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_raises(
    unexpected_exception: Type[Exception],
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() not raises unexpected_exception

    Fails immediately if any other type of exception is raised

    Args:
        unexpected_exception: value to compare against
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    def assert_function():
        try:
            return func(), True
        except unexpected_exception:
            return None, False

    cond_repr = (f"{getattr(func, '__name__', str(func))} doesn't "
                 f"raise {safe_repr(unexpected_exception)}")

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_regex_match_found(
    expected_regex: Regex,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until func() =~ expected_regex

    Args:
        expected_regex: regex used to match
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    if isinstance(expected_regex, (str, bytes)):
        expected_regex = re.compile(expected_regex)

    def assert_function():
        result = func()
        return result, bool(expected_regex.search(result))

    cond_repr = f"'{expected_regex.pattern}' finds match in {{actual}}"

    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )


def until_not_regex_match_found(
    unexpected_regex: Regex,
    func: Callable[..., Any],
    timeout: int,
    poll_time: float = None,
    ignored_exceptions: Iterable = None,
    msg: str = None,
    raise_on_timeout: bool = True
):
    """Wait until not(func() =~ unexpected_regex)

    Args:
        unexpected_regex: regex used to match
        func: func to poll
        timeout: seconds to poll
        poll_time: time between each attempt
        ignored_exceptions: exceptions to catch and ignore
        to format the last value of the function into it. prints with exception
        msg: optional message to include with the exception.
        raise_on_timeout: if false, will return last value on timeout instead
        of raising

    Returns:
        Last result of func()
    """
    if isinstance(unexpected_regex, (str, bytes)):
        unexpected_regex = re.compile(unexpected_regex)

    def assert_function():
        result = func()
        return result, not bool(unexpected_regex.search(result))

    cond_repr = f"'{unexpected_regex.pattern}' doesn't find match in {{actual}}"
    return until(
        assert_function,
        condition=cond_repr,
        timeout=timeout,
        poll_time=poll_time,
        ignored_exceptions=ignored_exceptions,
        msg=msg,
        raise_on_timeout=raise_on_timeout
    )
