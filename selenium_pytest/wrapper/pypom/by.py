from abc import ABC, abstractmethod
from copy import copy
from typing import List, Union

from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By as Strategy
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select

from wrapper.common import scripts
from wrapper.pypom import wait


class By(ABC):
    DEFAULT_TIMEOUT = 15
    _SELENIUM_IDE_BY = ''

    def __init__(
        self, by: str, value: str, *args, driver: WebDriver = None, timeout: int = None, **kwargs
    ):
        """
        Args:
            by: one of the options available in selenium.common.By
            value: the locator
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element, takes precedence over
            timeout set in a page's init
        """
        self.by = by
        self.value = value

        self.driver = driver
        self.timeout_is_default = not bool(timeout)
        self.default_timeout = self.DEFAULT_TIMEOUT if timeout is None else timeout

    def format(self, *args, **kwargs) -> 'By':
        """Return a formatted version of this selector's value,
        using str.format(*args, **kwargs).

        Args:
            args: positional substitution value
            kwargs: keyword substitution args
        """
        return self.__class__(self.value.format(*args, **kwargs), self.driver)

    def _validate_driver(self):
        if self.driver is None:
            raise AttributeError("""
                Element was not properly initialized with a driver.
                Ensure a webdriver was passed to the owning Page/PageSection
                and Page/PageSection.__init__ was called.
            """)

    def __str__(self) -> str:
        return f'{self._SELENIUM_IDE_BY}={self.value}'

    def __add__(self, value: str) -> 'By':
        """Creates a new By element with the value param appended."""
        copied = copy(self)
        copied.value += value
        return copied

    def __bool__(self) -> bool:
        """Defines the truthy/falsey behavior of a By selector based
        on its value (string). For example:
             - ByCss('') evaluates to False
             - ByClass('something') evaluates to True
        """
        return bool(self.value)

    # region actions

    def clear(self):
        """Clear the specified input field."""
        element = self.find_when_visible()
        element.clear()

    def clear_react_field(self):
        """Clear stubborn react input fields that do not work with .clear().

        emulates the user selecting all on the field and using backspace
        """
        element = self.find_when_visible()
        element.click()
        (ActionChains(self.driver)
            .send_keys(Keys.HOME)
            .key_down(Keys.SHIFT).send_keys(Keys.END).key_up(Keys.SHIFT)
            .send_keys(Keys.BACKSPACE).perform()
         )

    def click(self):
        """Click the specified element."""
        element = self.find_when_visible()
        element.click()

    def click_and_wait(self, timeout: int = None, raise_on_timeout: bool = True) -> bool:
        """Click the specified element and wait for staleness.

        Waits for the element to become stale to verify a new DOM with the
        server response.

        Args:
            timeout: how long to wait for the server to respond
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        element.click()
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after clicking.",
            raise_on_timeout=raise_on_timeout
        )

    def double_click(self):
        """Double clicks the element."""
        element = self.find_when_visible()
        ActionChains(self.driver).double_click(element).perform()

    def drag_and_drop(self, target: 'By'):
        """Drags the element into another.

        Args:
            target: drop target
        """
        start = self.find_when_visible()
        finish = target.find_when_visible()
        ActionChains(self.driver).drag_and_drop(start, finish).perform()

    def mouseover(self):
        """Move mouse over the element."""
        element = self.find_when_visible()
        ActionChains(self.driver).move_to_element(element).perform()

    def mousedown(self):
        """Click Left mouse on the element."""
        element = self.find_when_visible()
        ActionChains(self.driver).click_and_hold(element).perform()

    def mouseup(self):
        """Release left mouse button on the element."""
        element = self.find_when_visible()
        ActionChains(self.driver).release(element).perform()

    def has_attribute(self, attribute: str) -> bool:
        """Checks whether the given element contains the supplied attribute
        name. There is no direct call for this in webdriver, so here we first
        attempt to fetch the attribute, then check for any value on it.

        Args:
            attribute: the name of the element attribute to check for

        Returns:
            bool: whether the element has the target attribute
        """
        return self.get_attribute_value(attribute) is not None

    def get_attribute_value(self, attribute: str) -> Union[str, None]:
        """Return the value of the specified element's specified attribute.

        Args:
            attribute: the name of the element attribute to store

        Returns:
            Union[str, None]: attribute value if has attribute, else None
        """
        return self.find_when_exists().get_attribute(attribute)

    def get_css_property(self, css_property: str) -> str:
        """Return the value of the specified element's specified css property.

        Args:
            css_property: name of the css property to retrieve

        Returns:
            Union[str, None]: If the css property is not found, returns None
        """
        element = self.find_when_exists()
        return element.value_of_css_property(css_property)

    def get_value(self) -> str:
        """Return the value of the specified element's value attribute.
        Returns:
            Union[str, None]: If value attribute is not found, returns None
        """
        element = self.find_when_exists()
        return element.get_attribute("value")

    def get_all_attributes(self, attribute_name: str) -> List[str]:
        """
        Returns a list of the specified locator elements' attribute strings

        Args:
            attribute_name: string name of the html attribute to retrieve for each element

        Returns:
            List[str]: list of all specified attribute_name
        """
        elements = self.find_all_when_exists()
        return [element.get_attribute(attribute_name) for element in elements]

    def get_all_values(self) -> List[str]:
        """
        Returns a list of the specified locator elements' "value" attribute strings

        Returns:
            List[str]: list of all specified "value" attribute
        """
        return self.get_all_attributes("value")

    def get_classes(self) -> List[str]:
        """Return a list of the element's classes.
        Returns:
            List[str]: list of all classes, empty list if no class attribute found
        """
        classes = self.get_attribute_value("class")
        if classes:
            return classes.split()
        else:
            return []

    def has_class(self, class_name: str) -> bool:
        """ Return whether the specified element has the given class name.

        Args:
            class_name: the name of the class to try to match

        Returns:
            bool: True if the element has no class attribute or
            doesn't have the given class name else False
        """
        return class_name in self.get_classes()

    def has_classes(self, *class_names: str) -> bool:
        """ Return whether the specified element has the given class names.

        Args:
            class_names: the names of the classes to try to match

        Returns:
            bool: True if the element has no class attribute or
            doesn't have the given class names else False
        """
        classes = self.get_classes()
        return all([name in classes for name in class_names])

    def exists(self) -> bool:
        """Return whether or not the specified element currently exists."""
        try:
            self.find()
        except selenium_exceptions.NoSuchElementException:
            return False
        return True

    def is_visible(self) -> bool:
        """Return whether or not the specified element is currently visible."""
        element = self.find_when_exists()
        return element.is_displayed()

    def is_element_completely_in_viewport(self) -> bool:
        """Return whether or not the specified element is in the current viewport."""
        element = self.find_when_exists()
        return self.driver.execute_script(scripts.IS_ELEMENT_COMPLETELY_IN_VIEWPORT, element)

    def is_element_partially_in_viewport(self) -> bool:
        """Return whether or not the specified element is partially in the current viewport."""
        element = self.find_when_exists()
        return self.driver.execute_script(scripts.IS_ELEMENT_PARTIALLY_IN_VIEWPORT, element)

    def get_count(self) -> int:
        """Return the number of all matching elements."""
        return len(self.find_all())

    def get_text(self) -> str:
        """Return the element's text."""
        return self.find_when_exists().text

    def get_all_text(self) -> List[str]:
        """Return a list of each matching element's text."""

        elements = self.find_all_when_exists()
        return [element.text for element in elements]

    def get_location(self) -> dict:
        """Return the x, y coordinates of the specified element.

        Returns:
            dict: The element's location on the page as a dict with keys
            "x" and "y"
        """
        element = self.find_when_exists()
        return element.location

    def select_option_by_value(self, value: str):
        """Select an option within the specified 'select' element by value.

        Args:
            value: the value of the specified option
        """
        self.find_select_when_exists().select_by_value(value)

    def select_option_by_value_and_wait(
        self, value: str, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Select a 'select' element option by value and wait for staleness.

        Args:
            value: the value of the specified option
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        Select(element).select_by_value(value)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after selecting.",
            raise_on_timeout=raise_on_timeout
        )

    def select_option_by_index(self, index: int):
        """Select an option within the specified 'select' element by index.

        Args:
            index: the index of the specified option
        """
        self.find_select_when_exists().select_by_index(index)

    def select_option_by_index_and_wait(
        self, index: int, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Select a 'select' element option by index and wait for staleness.

        Args:
            index: the index of the specified option
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        Select(element).select_by_index(index)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after selecting.",
            raise_on_timeout=raise_on_timeout
        )

    def select_option_by_visible_text(self, text: str):
        """Select an option within the specified 'select' element by get_text.

        Args:
            text: the get_text of the specified option
        """
        self.find_select_when_exists().select_by_visible_text(text)

    def select_option_by_visible_text_and_wait(
        self, text: str, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Select a 'select' element option by get_text and wait for staleness.

        Args:
            text: the get_text of the specified option
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        Select(element).select_by_visible_text(text)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after selecting.",
            raise_on_timeout=raise_on_timeout
        )

    def deselect_option_by_value(self, value: str):
        """Deselect an option within the specified 'select' element by value.

        Args:
            value: the value of the specified option
        """
        self.find_select_when_exists().deselect_by_value(value)

    def deselect_option_by_value_and_wait(
        self, value: str, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Deselect a 'select' element option by value and wait for staleness.

        Args:
            value: the value of the specified option
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        Select(element).deselect_by_value(value)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after deselecting.",
            raise_on_timeout=raise_on_timeout
        )

    def deselect_option_by_index(self, index: int):
        """Deselect an option within the specified 'select' element by index

        Args:
            index: the index of the specified option
        """
        self.find_select_when_exists().deselect_by_index(index)

    def deselect_option_by_index_and_wait(
        self, index: int, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Deselect a 'select' element option by index and wait for staleness.

        Args:
            index: the index of the specified option
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        Select(element).deselect_by_index(index)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after deselecting.",
            raise_on_timeout=raise_on_timeout
        )

    def deselect_option_by_visible_text(self, text: str):
        """Deselect an option within the specified 'select' element by get_text.

        Args:
            text: the get_text of the specified option
        """
        self.find_select_when_exists().deselect_by_visible_text(text)

    def deselect_option_by_visible_text_and_wait(
        self, text: str, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Deselect a 'select' element option by get_text and wait for staleness.

        Args:
            text: the get_text of the specified option
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        Select(element).deselect_by_visible_text(text)

        return self._wait_until_stale(
            element,
            msg=f"Element {self} still attached to DOM after deselecting.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout
        )

    def deselect_all_options(self):
        """Deselect all options within a 'select' element."""
        self.find_select_when_exists().deselect_all()

    def is_selected(self) -> bool:
        """Return whether the specified element is selected.

        Applies to options within a 'select' as well as checkboxes and radio
        buttons.
        """
        return self.find_when_exists().is_selected()

    def get_first_selected_option(self) -> WebElement:
        """Return the first selected option in the Select element"""
        return self.find_select_when_exists().first_selected_option

    def get_first_selected_option_value(self) -> str:
        """Return the value of the selected option for the 'select' element.

        If multiple options are selected, returns the value from the first.
        """
        return self.get_first_selected_option().get_attribute("value")

    def get_first_selected_option_text(self) -> str:
        """Return the get_text of the selected option for the 'select' element.

        If multiple options are selected, returns the get_text from the first.
        """
        return self.get_first_selected_option().text

    def get_all_selected_options(self) -> List[WebElement]:
        """Return all selected options for the 'select' element"""
        return self.find_select_when_exists().all_selected_options

    def get_all_selected_options_values(self) -> List[str]:
        """Return the value of all selected options for the 'select' element."""
        selections = self.get_all_selected_options()
        return [selection.get_attribute("value") for selection in selections]

    def get_all_selected_options_text(self) -> List[str]:
        """Return the get_text of all selected options for the 'select' element."""
        selections = self.get_all_selected_options()
        return [selection.text for selection in selections]

    def get_all_select_options(self) -> List[WebElement]:
        """Return all options elements in a 'select' element."""
        return self.find_select_when_exists().options

    def get_all_select_options_values(self) -> List[str]:
        """Return the value of all options for a 'select' element."""
        options = self.get_all_select_options()
        return [option.get_attribute("value") for option in options]

    def get_all_select_options_text(self) -> List[str]:
        """Return the get_text of all options for a 'select' element."""
        options = self.get_all_select_options()
        return [option.text for option in options]

    def submit_form(self):
        """Submit the form associated with the specified element.

        Specified element may either be the form itself or any input within
        that form
        """
        element = self.find_when_visible()
        element.submit()

    def submit_form_and_wait(
        self, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Submit the element's form and wait for staleness.

        Specified element may either be the form itself or any input within
        that form.

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        element = self.find_when_visible()
        element.submit()
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Element {self} still attached to DOM after submitting form",
            raise_on_timeout=raise_on_timeout
        )

    def type(self, value: str):
        """Clear the element then send the specified characters to it.

        Args:
            value: the string to type
        """
        # I don't like that Selenium happily types None, True, False, etc.
        if type(value) is None:
            raise ValueError(
                "'value' argument is expected to not be None."
            )
        element = self.find_when_visible()
        element.clear()
        element.send_keys(value)

    def type_react(self, value: str):
        """Clear the react element then send the specified characters to it.

        Args:
            value: the string to type
        """
        self.clear_react_field()
        self.type(value)

    def type_and_wait(
        self, value: str, timeout: int = None, raise_on_timeout: bool = True
    ) -> bool:
        """Clear the element then send the characters and wait for staleness.

        Args:
            value: the string to type
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout

        if type(value) is None:
            raise ValueError("'value' argument cannot be None.")

        element = self.find_when_visible()
        element.clear()
        element.send_keys(value)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Input element {self} still attached to DOM after typing '{value}'",
            raise_on_timeout=raise_on_timeout
        )

    def send_keys(self, value: str):
        """Send the specified characters to the specified element.

        Args:
            value: the string to send
        """
        if type(value) is None:
            raise ValueError("'value' argument cannot be None.")

        element = self.find_when_visible()
        element.send_keys(value)

    def send_keys_and_wait(
        self,
        value: str,
        timeout: int = None,
        raise_on_timeout: bool = True
    ) -> bool:
        """Send the specified characters to the element and wait for staleness.

        Args:
            value: the string to send
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_stale

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still attached to DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        if type(value) is None:
            raise ValueError("'value' argument cannot be None.")

        element = self.find_when_visible(timeout=timeout)
        element.send_keys(value)
        return self._wait_until_stale(
            element,
            timeout=timeout,
            msg=f"Input element {self} still attached to DOM after typing '{value}'",
            raise_on_timeout=raise_on_timeout
        )

    def send_tab(self):
        """Emulates pressing tab while focused on a certain element."""
        self.send_keys(Keys.TAB)

    def send_enter(self):
        """Emulates pressing enter while focused on a certain element"""
        self.send_keys(Keys.ENTER)

    def send_enter_and_wait(self):
        """Emulates pressing enter while focused on a certain element"""
        self.send_keys_and_wait(Keys.ENTER)

    def send_escape(self):
        """Emulates pressing escape while focused on a certain element"""
        self.send_keys(Keys.ESCAPE)

    def send_down_arrow(self):
        """Emulates pressing down arrow while focused on a certain element"""
        self.send_keys(Keys.ARROW_DOWN)

    def send_up_arrow(self):
        """Emulates pressing up arrow while focused on a certain element"""
        self.send_keys(Keys.ARROW_UP)

    def send_left_arrow(self):
        """Emulates pressing left arrow while focused on a certain element"""
        self.send_keys(Keys.ARROW_LEFT)

    def send_right_arrow(self):
        """Emulates pressing right arrow while focused on a certain element"""
        self.send_keys(Keys.ARROW_RIGHT)

    def send_backspace(self):
        """Emulates pressing backspace while focused on a certain element"""
        self.send_keys(Keys.BACKSPACE)

    def send_delete(self):
        """Emulates pressing delete while focused on a certain element"""
        self.send_keys(Keys.DELETE)

    def fire_event(self, event: str):
        """Fire a javascript event at a web element.

        Args:
            event: name of the event to trigger
        """

        self._validate_driver()
        script = f"{self.js_find()}.{event}();"
        self.driver.execute_script(script)

    def set_attribute(self, atr: str, value: str):
        """Set an element's attribute.

        Args:
            atr: the name of the attribute to set
            value: the value of the attribute to set
        """
        self._validate_driver()
        script = f'{self.js_find()}.{atr} = "{value}"'
        self.driver.execute_script(script)

    def switch_to_iframe(self):
        """Switch to and select the given frame."""
        self._validate_driver()
        frame = self.find_when_exists()
        self.driver.switch_to.frame(frame)
        # todo: iframe handling

    # endregion

    # region waits

    def wait_until_exists(
        self, timeout: int = None, msg: str = None, raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to exist.

        Args:
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: exists

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still doesn't exist after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            self.exists,
            msg=msg or f"Element {self} still doesn't exist after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_not_exists(
        self, timeout: int = None, msg: str = None, raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to not exist.

        Args:
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: exists

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still exists after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            lambda: not self.exists(),
            msg=msg or f"Element {self} still exists after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_visible(
        self, timeout: int = None, msg: str = None, raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to be visible.

        Args:
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_visible

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still not visible after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            self.is_visible,
            msg=msg or f"Element {self} still not visible after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_not_visible(
        self, timeout: int = None, msg: str = None, raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to not be visible.

        Args:
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_visible

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still visible after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            lambda: not self.is_visible(),
            msg=msg or f"Element {self} still visible after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_completely_in_viewport(
        self, timeout: int = None, msg: str = None, raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to be completely in viewport.

        Args:
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: is_element_completely_in_viewport

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still not visible after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            self.is_element_completely_in_viewport,
            msg=msg or f"Element {self} still not in viewport after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_completely_not_in_viewport(
        self, timeout: int = None, msg: str = None, raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to be completely not in viewport.

        Args:
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: not is_element_partially_in_viewport

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still not visible after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            lambda: not self.is_element_partially_in_viewport(),
            msg=msg or f"Element {self} still in viewport after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_text_equals(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the element's get_text to have a certain value.

        Args:
            value: the expected value of the element's get_text.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's text

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            text still doesn't equal :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_equal(
            value,
            self.get_text,
            msg=msg or f"Element {self} text still doesn't equal value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_text_not_equals(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the element's get_text to not have a certain value.

        Args:
            value: the value the element's get_text is not expected to be.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's text

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            text still equals :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_equal(
            value,
            self.get_text,
            msg=msg or f"Element {self} text still equals value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_text_contains(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the element's get_text to contain a certain value.

        Args:
            value: the expected value of the element's get_text.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's text

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            text still doesn't contain :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_contains(
            value,
            self.get_text,
            msg=msg or f"Element {self} text still doesn't contain value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_text_not_contains(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the element's get_text to not contain a certain value.

        Args:
            value: the value the element's get_text is not expected to contain.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's text

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            text still contains :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_contains(
            value,
            self.get_text,
            msg=msg or f"Element {self} text still contains value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_attribute_equals(
        self,
        attribute: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for an attribute of the element to have a certain value.

        Args:
            attribute: the name of the element attribute.
            value: the value the element attribute is expected to have.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :attribute: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :attribute: still doesn't equal :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_equal(
            value,
            lambda: self.get_attribute_value(attribute),
            msg=msg or f"Element {self} attribute {attribute} still doesn't equal value "
                       f"after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_attribute_not_equals(
        self,
        attribute: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for an attribute of the element to not have a certain value.

        Args:
            attribute: the name of the element attribute.
            value: the value the element attribute is expected to not have.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :attribute: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :attribute: still equals :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_equal(
            value,
            lambda: self.get_attribute_value(attribute),
            msg=msg or f"Element {self} attribute {attribute} still equals value "
                       f"after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_attribute_contains(
        self,
        attribute: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for an attribute of the element to contain a certain value.

        Args:
            attribute: the name of the element attribute.
            value: the value the element attribute is expected to contain.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :attribute: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :attribute: still doesn't contain :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_contains(
            value,
            lambda: self.get_attribute_value(attribute) or '',
            msg=msg or f"Element {self} attribute {attribute} still doesn't contain value "
                       f"after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_attribute_not_contains(
        self,
        attribute: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for an attribute of the element to not contain a certain value.

        Args:
            attribute: the name of the element attribute.
            value: the value the element attribute is expected to not contain.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :attribute: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :attribute: still contains :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_contains(
            value,
            lambda: self.get_attribute_value(attribute),
            msg=msg or f"Element {self} attribute {attribute} still contains value "
                       f"after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_value_equals(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the value attribute of the element's to equal a value.

        Typically used with <input> elements.

        Args:
            value: the expected element value.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's value attribute's value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            value attribute still doesn't equal :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_equal(
            value,
            self.get_value,
            msg=msg or f"Element {self} value attribute still not value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_value_not_equals(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the value attribute of the element's to not equal a value.

        Typically used with <input> elements.

        Args:
            value: the unexpected element value.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's value attribute's value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            value attribute still equals :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_equal(
            value,
            self.get_value,
            msg=msg or f"Element {self} value attribute still value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_value_contains(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the value attribute of the element to contain a value

        Typically used with <input> elements.

        Args:
            value: the expected element value.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's value attribute's value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            value attribute still doesn't contain :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_contains(
            value,
            self.get_value,
            msg=msg or f"Element {self} still doesnt contain value after {timeout} seconds.",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_value_not_contains(
        self,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for the value attribute of the element to not contain a value

        Typically used with <input> elements.

        Args:
            value: the unexpected element value.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's value attribute's value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            value attribute still contains :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_contains(
            value,
            self.get_value,
            msg=msg or f"Element {self} value attribute still contains value"
                       f"after {timeout} seconds",
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_count_equals(
        self,
        count: int,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> int:
        """Wait for the count of matching elements to equal a value
        Args:
            count: the value that the element count is expected to be equal.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            int: final count

        Raises:
            WaitTimeoutError: if raise_on_timeout and
            element count still not equal to :count:
        """
        timeout = self.default_timeout if timeout is None else timeout

        return wait.until_equal(
            count,
            self.get_count,
            timeout=timeout,
            msg=msg or f"Element {self} count not equal to value after {timeout} seconds.",
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_count_greater_than(
        self,
        value: int,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> int:
        """Wait for the count of matching elements to be greater than a value
        Args:
            value: the value that the element count is expected to exceed.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            int: final count

        Raises:
            WaitTimeoutError: if raise_on_timeout and
            element count not greater than :count:
        """
        timeout = self.default_timeout if timeout is None else timeout

        return wait.until_greater(
            value,
            self.get_count,
            timeout=timeout,
            msg=msg or f"Element {self} count not greater than value after {timeout} seconds.",
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_count_greater_than_or_equals(
        self,
        value: int,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> int:
        """Wait for the count of matching elements to be greater than or equal to a value
        Args:
            value: the value that the element count is expected to equal or exceed.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            int: final count

        Raises:
            WaitTimeoutError: if raise_on_timeout and
            element count not greater than or equal to :count:
        """
        timeout = self.default_timeout if timeout is None else timeout

        return wait.until_greater_equal(
            value,
            self.get_count,
            timeout=timeout,
            msg=msg or f"Element {self} count not greater than or equal to value after {timeout} seconds.",
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_count_less_than(
        self,
        value: int,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> int:
        """Wait for the count of matching elements to be less than a value
        Args:
            value: the value that the element count is expected to drop below.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            int: final count

        Raises:
            WaitTimeoutError: if raise_on_timeout and
            element count not less than :count:
        """
        timeout = self.default_timeout if timeout is None else timeout

        return wait.until_less(
            value,
            self.get_count,
            timeout=timeout,
            msg=msg or f"Element {self} count not less than value after {timeout} seconds.",
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_count_less_than_or_equals(
        self,
        value: int,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> int:
        """Wait for the count of matching elements to be less than or equal to a value
        Args:
            value: the value that the element count is expected to drop equal to or below.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            int: final count

        Raises:
            WaitTimeoutError: if raise_on_timeout and
            element count not less than or equal to :count:
        """
        timeout = self.default_timeout if timeout is None else timeout

        return wait.until_less_equal(
            value,
            self.get_count,
            timeout=timeout,
            msg=msg or f"Element {self} count not less than or equal to value after {timeout} seconds.",
            raise_on_timeout=raise_on_timeout
        )

    def wait_until_css_property_equals(
        self,
        css_property: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for a css property on the element to have a certain value.

        Args:
            css_property: the name of the element css property.
            value: the value the css property is expected to be.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :css_property: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :css_property: still doesn't equal :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_equal(
            value,
            lambda: self.get_css_property(css_property),
            msg=(
                msg or
                f"Element {self} css property '{css_property}' "
                f"not equal to value after {timeout} seconds."
            ),
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_css_property_not_equals(
        self,
        css_property: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for a css property on the element to have a certain value.

        Args:
            css_property: the name of the element css property.
            value: the value the css property is not expected to be.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :css_property: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :css_property: still equals :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_equal(
            value,
            lambda: self.get_css_property(css_property),
            msg=(
                msg or
                f"Element {self} css property '{css_property}' "
                f"still equal to value after {timeout} seconds."
            ),
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_css_property_contains(
        self,
        css_property: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for a css property of the element to contain a certain value.

        Args:
            css_property: the name of the element css property.
            value: the value the css property is expected to contain.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :css_property: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :css_property: still doesn't contain :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_contains(
            value,
            lambda: self.get_css_property(css_property),
            msg=(
                msg or
                f"Element {self} css property '{css_property}' "
                f"still doesn't contain value after {timeout} seconds."
            ),
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_css_property_not_contains(
        self,
        css_property: str,
        value: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> str:
        """Wait for a css property of the element to not contain a certain value.

        Args:
            css_property: the name of the element css property.
            value: the value the css property is not expected to contain.
            timeout: how long to wait, in seconds.
            msg: message to print with exception.
            raise_on_timeout: raise an error if wait times out

        Returns:
            str: element's :css_property: value

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :css_property: still contains :value: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_not_contains(
            value,
            lambda: self.get_css_property(css_property),
            msg=(
                msg or
                f"Element {self} css property '{css_property}' "
                f"still contains value after {timeout} seconds."
            ),
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_has_attribute(
        self,
        attribute: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to have a target attribute

        Args:
            attribute: The target attribute to wait for
            timeout: how long to wait, in seconds
            msg: message to print with exception
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: result of has_attribute

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still does not have :attribute: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            lambda: self.has_attribute(attribute),
            msg=(
                msg or
                f"Element {self} still doesn't have attribute '{attribute}' "
                f"after {timeout} seconds."
            ),
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def wait_until_not_has_attribute(
        self,
        attribute: str,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> bool:
        """Wait for the element to not have a target attribute

        Args:
            attribute: The target attribute to wait for
            timeout: how long to wait, in seconds
            msg: message to print with exception
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: result of has_attribute

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            element still has :attribute: after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            lambda: not self.has_attribute(attribute),
            msg=(
                msg or
                f"Element {self} still has attribute '{attribute}' "
                f"after {timeout} seconds."
            ),
            timeout=timeout,
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    def _wait_until_stale(
        self,
        element: WebElement,
        timeout: int = None,
        msg: str = None,
        raise_on_timeout: bool = True
    ) -> bool:
        """Wait until the element is stale

        Args:
            element: the element to wait for staleness
            timeout: time to wait in seconds
            msg: msg to print on timeout error
            raise_on_timeout: raise an error if wait times out

        Returns:
            bool: True if element goes stale, else False

        Raises:
            WaitTimeoutError: If raise_on_timeout and
            :element: is still attached to the DOM after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        return wait.until_true(
            lambda: ec.staleness_of(element)(None),
            timeout=timeout,
            msg=msg or f"Element still attached to DOM after {timeout} seconds.",
            raise_on_timeout=raise_on_timeout,
            ignored_exceptions=[selenium_exceptions.NoSuchElementException]
        )

    # endregion

    # region finds

    def find_when_exists(
        self, timeout: int = None, raise_on_timeout: bool = True, msg: str = None
    ) -> WebElement:
        """Wait for an element to exist and return it

        Args:
            timeout: how long to wait before timing out
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception

        Raises:
            WaitTimeoutError: Element still doesnt exist after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        try:
            return wait.until_not_raises(
                selenium_exceptions.NoSuchElementException,
                self.find,
                timeout=timeout,
                raise_on_timeout=raise_on_timeout
            )
        except wait.WaitTimeoutError:
            raise selenium_exceptions.NoSuchElementException(
                msg or f'Could not find element {self} after {timeout} seconds.'
            )

    def find_when_visible(
        self, timeout: int = None, raise_on_timeout: bool = True, msg: str = None
    ) -> WebElement:
        """Finds an element once it's visible.

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception

        Raises:
            WaitTimeoutError: Element still isn't visible after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout

        def get_if_visible():
            element = self.find()
            if element.is_displayed():
                return element
            else:
                raise selenium_exceptions.NoSuchElementException

        try:
            return wait.until_not_raises(
                selenium_exceptions.NoSuchElementException,
                get_if_visible,
                timeout=timeout,
                raise_on_timeout=raise_on_timeout
            )
        except wait.WaitTimeoutError:
            raise selenium_exceptions.NoSuchElementException(
                f"Could not find existing & visible "
                f"element {self} after {timeout} seconds"
            )

    def find_select_when_exists(
        self, timeout: int = None, raise_on_timeout: bool = True, msg: str = None
    ) -> Select:
        """Find the element as a Select when visible

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception

        Raises:
            WaitTimeoutError: No matching elements exist after :timeout: seconds
        """
        return Select(
            self.find_when_exists(timeout=timeout, raise_on_timeout=raise_on_timeout, msg=msg))

    def find_all_when_exists(
        self, timeout: int = None, raise_on_timeout: bool = True, msg: str = None
    ) -> List[WebElement]:
        """Finds all matching elements once at least one exists

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception

        Raises:
            WaitTimeoutError: No matching elements exist after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout
        try:
            return wait.until_not_equal(
                [],
                self.find_all,
                timeout=timeout,
                raise_on_timeout=raise_on_timeout
            )
        except wait.WaitTimeoutError:
            raise selenium_exceptions.NoSuchElementException(
                msg or f'Could not find any elements matching {self} after {timeout} seconds.'
            )

    def find_all_when_visible(
        self, timeout: int = None, raise_on_timeout: bool = True, msg: str = None
    ) -> List[WebElement]:
        """Finds all matching element once they're visible.

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception

        Raises:
            WaitTimeoutError: Element still isn't visible after :timeout: seconds
        """
        timeout = self.default_timeout if timeout is None else timeout

        def get_if_visible():
            elements = self.find_all()
            if elements and all([element.is_displayed() for element in elements]):
                return elements

        try:
            return wait.until_is_not_none(
                get_if_visible,
                timeout=timeout,
                raise_on_timeout=raise_on_timeout
            )
        except wait.WaitTimeoutError:
            raise selenium_exceptions.NoSuchElementException(
                msg or
                f"Could not find matching elements {self} "
                f"where all elements are visible."
            )

    def find(self) -> WebElement:
        """Finds a matching element

        Raises:
            NoSuchElementException: If no matching element is found
        """

        self._validate_driver()
        try:
            return self.driver.find_element(self.by, self.value)
        except selenium_exceptions.NoSuchElementException as e:
            raise selenium_exceptions.NoSuchElementException(
                f"Unable to locate any element where {self} on page {self.driver.current_url}"
            ) from e

    def find_all(self) -> List[WebElement]:
        """Return all matching elements"""

        self._validate_driver()
        return self.driver.find_elements(self.by, self.value)

    def js_find(self) -> str:
        """Return js obj string finder for the element.

        Raises:
            ValueError: if selector strategy is one of [XPath, LinkText, PartialLinkText]
        """

        get_element_by = {
            Strategy.CLASS_NAME: 'getElementsByClassName("{}")[0]',
            Strategy.CSS_SELECTOR: 'querySelector("{}")',
            Strategy.ID: 'getElementById("{}")',
            Strategy.NAME: 'getElementsByName("{}")[0]',
            Strategy.TAG_NAME: 'getElementsByTagName("{}")[0]',
            # todo By.XPATH : '',
            # todo By.PARTIAL_LINK_TEXT : '',
            # todo By.LINK_TEXT : '',
        }
        if self.by in get_element_by.keys():
            return "document." + get_element_by[self.by].format(self.value)

        raise ValueError(
            f'Cannot use selector strategy of "{self.by}" with javascript functions.'
        )

    # endregion


class CssFriendlyBy(By, ABC):

    def __init__(self, by: str, value: str, driver: WebDriver = None, timeout: int = None):
        super().__init__(by, value, driver=driver, timeout=timeout)

    def __add__(self, other: Union['CssFriendlyBy', str]) -> 'CssFriendlyBy':
        """Create a new selector.
        If other is a By element, it appends as a descendant with an added space.
        If other a string, it will append as is.

        Raises:
            TypeError if other is not a string or CssFriendlyBy
        """
        if isinstance(other, str):
            return super().__add__(other)
        if not isinstance(other, CssFriendlyBy):
            raise TypeError('`other` must be a string or subclass of CssFriendlyBy')
        return self.descendant(other.css)

    def or_(self, other: Union['CssFriendlyBy', str]) -> 'CssFriendlyBy':
        """Create a new selector.
        If other is a By element, a new ByCss is created
            with other's CSS appended after a comma ( , ) - CSS "or" operator.
        If other is a string, it will be appended after a comma.

        Raises:
            TypeError if other is not a string or CssFriendlyBy
        """
        if isinstance(other, str):
            copied = copy(self)
            copied.value += f',{other}'
            return copied
        if not isinstance(other, CssFriendlyBy):
            raise TypeError('`other` must be a string or subclass of CssFriendlyBy')
        return ByCss(f'{self.css},{other.css}', self.driver)

    @property
    @abstractmethod
    def css(self) -> str:
        """Get the css version of the locator value"""
        pass

    def direct_descendant(self, css: str) -> 'ByCss':
        """Create a new ByCss that matches a direct descendant of this one
        Args:
            css: css to select the sibling

        Example:
            In the following html, '.bar' is not sufficient to grab the target div

            <div id='foo'>
                <div class='bar'></div>  # target
            </div>

            <div id='baz'>
                <div class='bar'></div>
            </div>

            ById('foo').immediate_descendant('.bar')
            Note: this is equivalent to ByCss('#foo > .bar')
        """
        return ByCss(f'{self.css} > {css}', self.driver)

    def descendant(self, css: str) -> 'ByCss':
        """Create a new ByCss that matches a descendant anywhere in this one's hierarchy
        Args:
            css: css to select the sibling

        Example:
            In the following html, '.bar' is not sufficient to grab the target div

            <div id='foo'>
                <div>
                    <div class='bar'></div>  # target
                </div>
            </div>

            <div id='baz'>
                <div class='bar'></div>
            </div>

            ById('foo').immediate_descendant('.bar')
            Note: this is equivalent to ByCss('#foo .bar')
        """
        return ByCss(f'{self.css} {css}', self.driver)

    def immediate_sibling(self, css: str) -> 'ByCss':
        """Create a new ByCss that matches a sibling immediately following this one
        Args:
            css: css to select the sibling

        Example:
            In the following html, '.bar' is not sufficient to grab the target div

            <div id='foo'></div>
            <div class='bar'></div>  # target

            <div id='baz'>
                <div class='bar'></div>
            </div>

            ById('foo').immediate_sibling('.bar')
            Note: this is equivalent to ByCss('#foo + .bar')
        """
        return ByCss(f'{self.css} + {css}', self.driver)

    def general_sibling(self, css: str) -> 'ByCss':
        """Create a new ByCss that matches any sibling following this one
        Args:
            css: css to select the sibling

        Example:
            In the following html, '.bar' is not sufficient to grab the target div

            <div id='foo'></div>
            <div></div>
            <div class='bar'></div>  # target

            <div id='baz'></div>
                <div class='bar'></div>

            ById('foo').immediate_sibling('.bar')
            Note: this is equivalent to ByCss('#foo ~ .bar')
        """
        return ByCss(f'{self.css} ~ {css}', self.driver)


class ByID(CssFriendlyBy):
    _SELENIUM_IDE_BY = 'id'

    def __init__(self, value: str, driver=None, timeout: int = None):
        """
        Args:
            value: css selector
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element

        Example:
            <div id='foo'></div>
            foo = ByID('foo')
        """
        super().__init__(Strategy.ID, value, driver=driver, timeout=timeout)

    @property
    def css(self) -> str:
        return '#' + self.value


class ByCss(CssFriendlyBy):
    _SELENIUM_IDE_BY = 'css'

    def __init__(self, value: str, driver=None, timeout: int = None):
        """
        Args:
            value: css selector
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element

        Example:
            <div class='foo'></div>
            foo = ByCss('.foo')

        Css Selector Reference:
            https://www.w3schools.com/cssref/css_selectors.asp
        """
        super().__init__(Strategy.CSS_SELECTOR, value, driver=driver, timeout=timeout)

    @property
    def css(self) -> str:
        return self.value


class ByClass(CssFriendlyBy):
    _SELENIUM_IDE_BY = 'class'

    def __init__(self, value: str, driver=None, timeout: int = None):
        """
        Args:
            value: css class, can only match on one class
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element

        Example:
            <div class='foo'></div>
            foo = ByClass('foo')
        """
        super().__init__(Strategy.CLASS_NAME, value, driver=driver, timeout=timeout)

    @property
    def css(self) -> str:
        return '.' + self.value


class ByName(CssFriendlyBy):
    _SELENIUM_IDE_BY = 'name'

    def __init__(self, value: str, driver=None, timeout: int = None):
        """
        Args:
            value: name attribute value
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element

        Example:
            <div name='foo'></div>
            foo = ByName('foo')
        """
        super().__init__(Strategy.NAME, value, driver=driver, timeout=timeout)

    @property
    def css(self) -> str:
        return f'[name="{self.value}"]'


class ByTag(CssFriendlyBy):
    _SELENIUM_IDE_BY = 'tag_name'

    def __init__(self, value: str, driver=None, timeout: int = None):
        """
        Args:
            value: tag name, ie 'div'
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element
        """
        super().__init__(Strategy.TAG_NAME, value, driver=driver, timeout=timeout)

    @property
    def css(self) -> str:
        return self.value


class ByXPath(By):
    _SELENIUM_IDE_BY = 'xpath'

    def __init__(self, value: str, driver=None, timeout: int = None):
        """
        Args:
            value: xpath to element
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element
        """
        super().__init__(Strategy.XPATH, value, driver=driver, timeout=timeout)

    def __add__(self, other: 'ByXPath'):
        """Returns a new selector with the second as a descendant of the first"""
        if type(other) is not ByXPath:
            raise ValueError()
        return ByXPath(f'{self.value}//{other.value.lstrip("/")}', self.driver)


class ByLinkText(By):
    _SELENIUM_IDE_BY = 'link_text'

    def __init__(self, value: str, driver: WebDriver = None, timeout: int = None):
        """
        Args:
            value: full text of a link element
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element
        """
        super().__init__(Strategy.LINK_TEXT, value, driver=driver, timeout=timeout)

    def __add__(self, other):
        raise ValueError('Cannot combine link text locators.')


class ByPartialLinkText(By):
    _SELENIUM_IDE_BY = 'partial_link_text'

    def __init__(self, value: str, driver: WebDriver = None, timeout: int = None):
        """
        Args:
            value: partial text of a link element
            driver: driver to use, usually set by Page object
            timeout: default poll time when waiting for this element
        """
        super().__init__(Strategy.PARTIAL_LINK_TEXT, value, driver=driver, timeout=timeout)

    def __add__(self, other):
        raise ValueError('Cannot combine partial link text locators.')
