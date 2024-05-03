import re
from typing import Tuple, Union, List
from urllib.parse import urlunsplit, urlsplit
from selenium import webdriver
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement

from wrapper import pypom
from wrapper.wait import Wait


class WrappedSeleniumWebdriver:
    def __init__(self, driver: webdriver.Remote):
        """Selenium Webdriver Wrapper that simplifies common tasks."""

        self.driver = driver
        self.timeout = 60

    def open(self, url: str):
        """Open the given url in the current window.

        Assumes the protocol is "http" if not included in URL.

        Args:
            url: the url to open
        """
        url = urlunsplit(urlsplit(url, scheme='http'))
        # if netloc not detected urlunsplit adds extra / to url
        url = url.replace('///', '//')
        try:
            self.driver.get(url)
        except Exception as e:
            raise e

    def refresh(self):
        """Refresh the current page.

        Identical to clicking the refresh button in the browser.
        """
        self.driver.refresh()

    def click(self, locator: str):
        """Click the specified element.

        Args:
            locator: the location of the input field to click
        """
        element = self._find_element(locator)
        element.click()

    def get_element_attribute_value(
            self,
            locator: str,
            attribute: str
    ) -> str:
        """Return the value of the specified element's specified attribute.

        Args:
            locator: the location of the expected attribute
            attribute: the name of the element attribute to store

        Returns:
            If the specified attribute is not found, returns None
        """
        element = self._find_element(locator)
        attribute_value = element.get_attribute(attribute)
        return attribute_value

    def get_element_css_property_value(
            self,
            locator: str,
            css_property: str
    ) -> str:
        """Return the value of the specified element's specified css property.

        Args:
            locator: the location of the specified element
            css_property: name of the css property to retrieve

        Returns:
            If the specified css property is not found, returns None
        """
        element = self._find_element(locator)
        css_property_value = element.value_of_css_property(css_property)
        return css_property_value

    def get_element_value(self, locator: str) -> str:
        """Return the value of the specified element's value attribute.

        Args:
            locator: the location of the specified element

        Returns:
            If the value attribute is not found, returns None
        """
        element = self._find_element(locator)
        value = element.get_attribute("value")
        return value

        # Private methods:
        # region

    def _find_element(self, locator: str) -> WebElement:
        """Return the specified element regardless of locator strategy.

        Parses the locator string to determine intended locator strategy.

        Args:
            locator: strategy and location for the specified element
        """
        try:
            return self.driver.find_element(*self._selector(locator))
        except selenium_exceptions.NoSuchElementException:
            raise selenium_exceptions.NoSuchElementException(
                "Unable to locate element {} on page {}".format(
                    locator,
                    self.driver.current_url
                )
            )

    def _find_elements(self, locator: str) -> List[WebElement]:
        """Return the specified elements regardless of locator strategy.

        Parses the locator string to determine intended locator strategy.

        Args:
            locator: strategy and location for the specified elements
        """
        try:
            return self.driver.find_elements(*self._selector(locator))
        except selenium_exceptions.NoSuchElementException:
            raise selenium_exceptions.NoSuchElementException(
                "Unable to locate any elements {} on page {}".format(
                    locator,
                    self.driver.current_url
                )
            )

    @staticmethod
    def _selector(locator: Union[str, pypom.by.By]) -> Tuple[By, str]:
        """Return a strategy and locator for a given locator string.

        Based on the Selenium IDE convention for locators, but with more
        flexibility.

        Args:
            locator: strategy and location for the specified element
        """
        if issubclass(type(locator), pypom.by.By):
            locator = str(locator)

        # supports e.g. css=, css = , CSS= , css :
        if re.match(r'css\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(r'css\s?[=:]\s?', '', locator,
                             flags=re.IGNORECASE)
            return By.CSS_SELECTOR, locator
        elif re.match(r'xpath\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(r'xpath\s?[=:]\s?', '', locator,
                             flags=re.IGNORECASE)
            return By.XPATH, locator
        elif re.match(r'id\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(r'id\s?[=:]\s?', '', locator, flags=re.IGNORECASE)
            return By.ID, locator
        elif re.match(r'class\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(r'class\s?[=:]\s?', '', locator,
                             flags=re.IGNORECASE)
            return By.CLASS_NAME, locator
        elif re.match(r'name\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(r'name\s?[=:]\s?', '', locator,
                             flags=re.IGNORECASE)
            return By.NAME, locator
        elif re.match(r'tag_name\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(r'tag_name\s?[=:]\s?', '', locator,
                             flags=re.IGNORECASE)
            return By.TAG_NAME, locator
        elif re.match(r'partial_link\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(
                r'partial_link\s?[=:]\s?', '',
                locator, flags=re.IGNORECASE)
            return By.PARTIAL_LINK_TEXT, locator
        elif re.match(r'link\s?[=:]\s?', locator, flags=re.IGNORECASE):
            locator = re.sub(
                r'link\s?[=:]\s?', '',
                locator, flags=re.IGNORECASE)
            return By.LINK_TEXT, locator
        else:
            raise ValueError(
                "The locator argument '%s' didn't have the expected prefix, "
                "such as 'css='" % locator
            )

    def get_element(self, locator: str) -> WebElement:
        """Return the specified element.

        Args:
            locator: the location of the specified element
        """
        return self._find_element(locator)

    def quit_driver(self):
        """Quit the wrapped webdriver, ignoring protestations."""
        try:
            self.driver.quit()
        # If an alert was present, close anyway.
        except selenium_exceptions.UnexpectedAlertPresentException:
            self.driver.quit()

    def switch_to_iframe(self, locator: str):
        """Switch to and select the given frame.

        Args:
            locator: location of the specified frame
        """
        frame = self._find_element(locator)
        self.driver.switch_to.frame(frame)

    def switch_from_iframe(self):
        """Switch to and select the default content of the page."""
        self.driver.switch_to.default_content()

    def is_element_enabled(self, locator: str) -> bool:
        """Return whether or not the specified element is currently enabled.

        Args:
            locator: the location of the page element
        """
        element = self._find_element(locator)
        return element.is_enabled()

    def hover(self, locator: str):
        """Move mouse over specified element.

        Args:
            locator: locator for target element
        """
        self.mouseover(locator)

    def mouseover(self, locator: str):
        """Move mouse over specified element.

        Args:
            locator: locator for specified element
        """
        element = self._find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def wait_for_element_exists(
            self, locator: str, duration: int = None, msg: str = None) -> bool:
        """Wait for the specified page element to exist.

        Args:
            locator: the location of the page element.
            duration: how long to wait, in seconds.
            msg: message to print with exception.
        """
        if duration is None:
            duration = self.timeout
        return Wait(timeout=duration).until_true(self.element_exists,
                                                 locator,
                                                 msg=msg)

    def element_exists(self, locator: str) -> bool:
        """Return whether or not the specified element currently exists.

        Args:
            locator: the location of the specified element
        """
        try:
            self.driver.find_element(*self._selector(locator))
        except selenium_exceptions.NoSuchElementException:
            return False
        return True

    def maximize_window(self) -> None:
        self.driver.maximize_window()

    def get_css_information(self, locator: str) -> dict[str:int]:
        """
        Returns the CSS information of the element such as width, height, border-radius, coordinates and paddings
        """
        element: WebElement = self._find_element(locator)
        w = element.value_of_css_property("width").replace("px", "")
        h = element.value_of_css_property("height").replace("px", "")
        pl = int(element.value_of_css_property("padding-left").replace("px", ""))
        pr = int(element.value_of_css_property("padding-right").replace("px", ""))
        pt = int(element.value_of_css_property("padding-top").replace("px", ""))
        pb = int(element.value_of_css_property("padding-bottom").replace("px", ""))
        br = int(element.value_of_css_property("border-radius").replace("px", ""))
        loc = element.location
        x1 = int(loc["x"])
        y1 = int(loc["y"])
        return {"x1": x1, "y1": y1, "x2": x1 + float(w) , "y2": y1 + float(h), "width": w, "height": h,
                "padding-left": pl, "padding-right": pr, "padding-top": pt, "padding-bottom": pb, "border-radius": br}
