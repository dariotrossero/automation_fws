"""Wait related logic"""

import collections
from numbers import Real
import re
import time
from typing import (
    Any,
    Callable,
    Container,
    Iterable,
    Pattern,
    Sized,
    TypeVar
)
import warnings


Regex = TypeVar('Regex', str, Pattern)


IGNORED_EXCEPTIONS = (AssertionError, )
POLL_FREQUENCY = 0.5  # How long to sleep in between calls to the method


class WaitTimeoutError(Exception):
    pass


class Wait:
    _EXTRA_IGNORED_EXCEPTIONS = []

    def __init__(
            self,
            timeout: int,
            poll_frequency: Real = POLL_FREQUENCY,
            ignored_exceptions: Iterable[Exception] = None
    ):
        """Constructor, takes a timeout in seconds.

        Args:
            timeout - Number of seconds before timing out
            poll_frequency - sleep interval between calls
                By default, it is 0.5 second.
            ignored_exceptions - iterable structure of exception classes
                ignored during calls. By default, it contains AssertionError only.

        Example:
            .. code-block:: python

               from shield.wait import Wait

               element = Wait(10).until_true(driver.find_element_by_id, "someId")

               is_disappeared = Wait(
                   30,
                   1,
                   (ElementNotVisibleException)
               ).until_not(element.is_displayed)
        """
        self._timeout = timeout
        self._poll = poll_frequency
        # avoid the divide by zero
        if self._poll == 0:
            self._poll = POLL_FREQUENCY
        exceptions = list(IGNORED_EXCEPTIONS)
        exceptions.extend(self._EXTRA_IGNORED_EXCEPTIONS)
        if ignored_exceptions is not None:
            try:
                exceptions.extend(iter(ignored_exceptions))
            except TypeError:  # ignored_exceptions is not iterable
                exceptions.append(ignored_exceptions)
        self._ignored_exceptions = tuple(exceptions)

    def _until(
            self,
            func: Callable[..., Any],
            *args,
            conditional: str = None,
            msg: str = None,
            **kwargs
    ):
        """Calls the function provided until no exception is raised"""

        end_time = time.time() + self._timeout
        if conditional:
            msg = "{} was still not true after {} seconds.{}".format(
                conditional,
                self._timeout,
                "\n" + msg if msg else ""
            )

        while True:
            try:
                return func(*args, **kwargs)
            except self._ignored_exceptions as exc:
                time.sleep(self._poll)
                if time.time() > end_time:
                    raise WaitTimeoutError(msg) from exc

    def until_almost_equal(
            self,
            value: Real,
            func: Callable[..., Any],
            *args,
            decimal_places: int = None,
            delta: Real = None,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) almost equal value

        Almost equal is defined as either:
          * x == (y ± delta)
          * round(abs(x - y), decimal places)
        """
        if delta is not None and decimal_places is not None:
            raise TypeError("specify delta or decimal_places not both")

        def assert_function(*x, **y):
            first = func(*x, **y)
            second = value
            places = decimal_places
            if first == second:
                # shortcut
                return first

            if delta is not None:
                assert abs(first - second) <= delta

            else:
                if places is None:
                    places = 7

                assert round(abs(second-first), places) == 0

            return first

        cond_repr = "{} almost equal {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_contains(
            self,
            member: Any,
            func: Callable[..., Container],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: member in func(*args, **kwargs)"""
        def assert_function(*x, **y):
            container = func(*x, **y)
            assert member in container
            return container

        cond_repr = "{1} in {0}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(member)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_contains_members(
            self,
            members: Iterable,
            func: Callable[..., Container],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: member in func(*args, **kwargs) for all members"""
        def assert_function(*x, **y):
            container = func(*x, **y)
            for item in members:
                assert item in container
            return container

        cond_repr = "item in {} for item in {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(members)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_count_equal(
            self,
            seq: Iterable,
            func: Callable[..., Iterable],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: same elements appear in func(*args, **kwargs) and seq

        An unordered sequence comparison asserting that the same elements,
        regardless of order.  If the same element occurs more than once,
        it verifies that the elements occur the same number of times.

            self.assertEqual(Counter(list(first)),
                             Counter(list(second)))

         Example:
            - [0, 1, 1] and [1, 0, 1] compare equal.
            - [0, 0, 1] and [0, 1] compare unequal.

        """
        def assert_function(*x, **y):
            # Stringify each element in the sequence to avoid an unhashable
            output = func(*x, **y)
            first_seq = map(_safe_repr, list(output))
            second_seq = map(_safe_repr, list(seq))
            # error
            # Use the update method to avoid IDE warnings about the
            # constructor
            first = collections.Counter()
            first.update(first_seq)
            second = collections.Counter()
            second.update(second_seq)
            assert first == second
            return output

        cond_repr = (
            "collections.Counter({}) == collections.Counter({})".format(
                _call_repr(func, *args, **kwargs),
                _safe_repr(seq)
            )
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_equal(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) == value"""
        def assert_function(*x, **y):
            first = func(*x, **y)
            second = value
            assert first == second
            return first

        cond_repr = "{} == {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_false(
            self,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: bool(func(*args, **kwargs)) == False"""
        def assert_function(*x, **y):
            expr = func(*x, **y)
            assert not expr
            return expr

        cond_repr = "{} == False".format(
            _call_repr(func, *args, **kwargs),
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_greater(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) > value"""
        def assert_function(*x, **y):
            first = func(*x, **y)
            second = value
            assert first > second
            return first

        cond_repr = "{} > {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_greater_equal(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) >= value"""
        def assert_function(*x, **y):
            first = func(*x, **y)
            second = value
            assert first >= second
            return first

        cond_repr = "{} >= {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_in(
            self,
            container: Container,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) in container"""
        def assert_function(*x, **y):
            member = func(*x, **y)
            assert member in container
            return member

        cond_repr = "{} in {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(container)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_is(
            self,
            expr: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) is expr"""
        def assert_function(*x, **y):
            expr1 = func(*x, **y)
            expr2 = expr
            assert expr1 is expr2
            return expr1

        cond_repr = "{} is {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(expr)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_is_instance(
            self,
            cls: type,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: isinstance(func(*args, **kwargs), cls)"""
        def assert_function(*x, **y):
            obj = func(*x, **y)
            assert isinstance(obj, cls)
            return obj

        cond_repr = "isinstance({}, {})".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(cls)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_is_none(
            self,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) is None"""
        def assert_function(*x, **y):
            expr = func(*x, **y)
            assert expr is None
            return expr

        cond_repr = "{} is None".format(
            _call_repr(func, *args, **kwargs),
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_is_not(
            self,
            expr: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) is not expr"""
        def assert_function(*x, **y):
            expr1 = func(*x, **y)
            expr2 = expr
            assert expr1 is not expr2
            return expr1

        cond_repr = "{} is not {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(expr)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_is_not_none(
            self,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) is not None"""
        def assert_function(*x, **y):
            expr = func(*x, **y)
            assert expr is not None
            return expr

        cond_repr = "{} is not None".format(
            _call_repr(func, *args, **kwargs),
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_lengths_equal(
            self,
            value: Sized,
            func: Callable[..., Sized],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: len(func(*args, **kwargs) == len(value)"""
        def assert_function(*x, **y):
            first = func(*x, **y)
            second = value
            assert len(first) == len(second)
            return len(first)

        cond_repr = "len({}) == len({})".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_less(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) < value"""
        def assert_function(*x, **y):
            expr = func(*x, **y)
            assert expr < value
            return expr

        cond_repr = "{} < {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_less_equal(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) <= value"""
        def assert_function(*x, **y):
            expr = func(*x, **y)
            assert expr <= value
            return expr

        cond_repr = "{} <= {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_logs(self, func, value, *args, **kwargs):
        raise NotImplementedError

    def until_not_almost_equal(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            decimal_places: int = None,
            delta: Real = None,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) not almost equal value

        Almost equal is defined as either:
        * x == (y ± delta)
        * round(abs(x - y), decimal places)
        """
        if delta is not None and decimal_places is not None:
            raise TypeError("specify delta or places not both")

        def assert_function(*x, **y):
            places = decimal_places
            first = func(*x, **y)
            second = value
            if delta is not None:
                assert not (first == second) and abs(first - second) > delta
            else:
                if places is None:
                    places = 7
                assert (
                    first != second and round(abs(second-first), places) != 0
                )
            return first

        cond_repr = "{} not almost equal {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_contains(
            self,
            member: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: member not in func(*args, **kwargs)"""
        def assert_function(*x, **y):
            container = func(*x, **y)
            assert member not in container
            return container

        cond_repr = "{1} not in {0}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(member)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_contains_members(
            self,
            members: Iterable,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: member not in func(*args, **kwargs) for all members"""
        def assert_function(*x, **y):
            container = func(*x, **y)
            for item in members:
                assert item not in container
            return container

        cond_repr = "item not in {} for item in {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(members)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_equal(
            self,
            value: Any,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) != value"""
        def assert_function(*x, **y):
            expr = func(*x, **y)
            assert expr != value
            return expr

        cond_repr = "{} != {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(value)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_in(
            self,
            container: Container,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) not in container"""
        def assert_function(*x, **y):
            member = func(*x, **y)
            assert member not in container
            return member

        cond_repr = "{} not in {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(container)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_is_instance(
            self,
            cls: type,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: not isinstance(func(*args, **kwargs), cls)"""
        def assert_function(*x, **y):
            obj = func(*x, **y)
            assert not isinstance(obj, cls)
            return obj

        cond_repr = "not isinstance({}, {})".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(cls)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_raises(
            self,
            unexpected_exception: Exception,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*x, **y) not raises unexpected_exception

        Fails immediately if any other type of exception is raised
        """
        def assert_function(*x, **y):
            try:
                return func(*x, **y)
            except unexpected_exception:
                raise AssertionError(
                    "{} was raised.".format(unexpected_exception))

        cond_repr = "{} not raises {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(unexpected_exception)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_not_regex(
            self,
            unexpected_regex: Regex,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: not(func(*x, **y) =~ unexpected_regex)"""
        if isinstance(unexpected_regex, (str, bytes)):
            unexpected_regex = re.compile(unexpected_regex)

        def assert_function(*x, **y):
            output = func(*x, **y)
            assert not unexpected_regex.search(output)
            return output

        cond_repr = "not {} =~ re.compile('{}')".format(
            _call_repr(func, *args, **kwargs),
            unexpected_regex.pattern
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_raises(
            self,
            expected_exception: Exception,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*x, **y) raises expected_exception

        Fails immediately if any other type of exception is raised
        """
        def assert_function(*x, **y):
            try:
                func(*x, **y)
            except expected_exception as exc:
                return exc
            raise AssertionError(
                "{} was never raised.".format(expected_exception))

        cond_repr = "{} raises {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(expected_exception)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_raises_regex(
            self,
            expected_exception: Exception,
            expected_regex: Regex,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*x, **y)'s raised exception =~ expected_regex

        Fails immediately if any other type of exception is raised
        """
        if isinstance(expected_regex, (str, bytes)):
            expected_regex = re.compile(expected_regex)

        def assert_function(*x, **y):
            try:
                func(*x, **y)
            except expected_exception as exc:
                exc_msg = str(exc.with_traceback(None))
                assert expected_regex.search(exc_msg)
                return exc
            raise AssertionError(
                "{} was never raised.".format(expected_exception))

        # TODO; modify this to be appropriate
        cond_repr = (
            "{call} raises {exc} and {exc} =~ re.compile({pattern})".format(
                call=_call_repr(func, *args, **kwargs),
                exc=_safe_repr(expected_exception),
                pattern=expected_regex.pattern
            )
        )
        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_regex(
            self,
            expected_regex: Regex,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: func(*args, **kwargs) =~ expected_regex"""
        if isinstance(expected_regex, (str, bytes)):
            expected_regex = re.compile(expected_regex)

        def assert_function(*x, **y):
            output = func(*x, **y)
            assert expected_regex.search(output)
            return output

        cond_repr = "{} =~ re.compile('{}')".format(
            _call_repr(func, *args, **kwargs),
            expected_regex.pattern
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_true(
            self,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: bool(func(*args, **kwargs)) == True"""
        def assert_function(*x, **y):
            output = func(*x, **y)
            assert output
            return output

        cond_repr = "{} == True".format(
            _call_repr(func, *args, **kwargs)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_warns(
            self,
            expected_warning: Warning,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: any(func(*x, **y) warns expected warning)"""
        def assert_function():
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always', expected_warning)
                func(*args, **kwargs)
                matching = [x for x in w if x.category == expected_warning]
                assert matching
                return matching

        cond_repr = "{} issues warning {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(expected_warning)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def until_warns_regex(
            self,
            expected_warning: Warning,
            expected_regex: Pattern,
            func: Callable[..., Any],
            *args,
            msg: str = None,
            **kwargs
    ):
        """Wait until: any(func(*x, **y)'s warnings =~ expected_regex)"""
        def assert_function():
            with warnings.catch_warnings(record=True) as w:
                warnings.resetwarnings()
                warnings.simplefilter('ignore')
                warnings.simplefilter('always', expected_warning)
                func(*args, **kwargs)

                def warn_filter(x):
                    return (
                        expected_regex.search(x.message)
                        and x.category == expected_warning
                    )
                matching = [x for x in w if warn_filter(x)]
                assert matching
                return matching

        # TODO; modify this to be appropriate
        cond_repr = "{} issues warning {}".format(
            _call_repr(func, *args, **kwargs),
            _safe_repr(expected_warning)
        )

        return self._until(
            assert_function,
            *args,
            conditional=cond_repr,
            msg=msg,
            **kwargs
        )

    def __repr__(self):
        return '<{0.__module__}.{0.__qualname__}>'.format(type(self))


def _safe_repr(obj: Any) -> str:
    """Return a string representation of the given object.

    Supports instances of Old Style classes.
    """
    if hasattr(obj, '__qualname__'):
        return obj.__qualname__
    try:
        result = repr(obj)
    except Exception:  # pylint: disable=W0703
        result = object.__repr__(obj)
    return result


def _call_repr(func: Callable[..., Any], *args, **kwargs) -> str:
    """Return a string representation of a function call."""
    return "{0.__qualname__}({1}, {2})".format(
        func,
        ', '.join(map(str, args)),
        ', '.join(
            map(
                lambda x: '{}={}'.format(*x),
                zip(kwargs.keys(), kwargs.values())
            )
        )
    )
