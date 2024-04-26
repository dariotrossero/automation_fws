from selenium.common import exceptions

from wrapper import wait


class Wait(wait.Wait):
    """Wait class with selenium specific ignored exceptions.

    Use this Wait class to make a custom wait that by default ignores
    any exceptions raised by selenium that are listed below.

    Example:
        The below will raise a WaitTimeoutError after 10s instead of
        an ElementNotVisibleException.

        .. code-block:: python

           from shield.selenium.wait import Wait

           element = Wait(10).until_true(
               driver.is_element_visible, "someLocator"
           )
    """
    _EXTRA_IGNORED_EXCEPTIONS = [
        exceptions.ElementNotSelectableException,
        exceptions.ElementNotVisibleException,
        exceptions.NoSuchElementException,
        exceptions.StaleElementReferenceException,
        exceptions.NoSuchAttributeException,
        exceptions.NoAlertPresentException,
        exceptions.NoSuchFrameException,
        exceptions.NoSuchWindowException
    ]
    pass
