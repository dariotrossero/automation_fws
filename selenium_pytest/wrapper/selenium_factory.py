"""Functions to create Selenium Webdriver or Appium instances."""

import logging

from selenium import webdriver as selenium_webdriver
from selenium.webdriver.remote.remote_connection import LOGGER

from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver

LOGGER.setLevel(logging.WARNING)


def create_wrapped_selenium_chrome_webdriver(
) -> WrappedSeleniumWebdriver:
    """Return a wrapped version of the provided selenium webdriver.

    """
    wrapped_webdriver = WrappedSeleniumWebdriver(selenium_webdriver.Chrome())
    return wrapped_webdriver


def create_wrapped_selenium_gecko_webdriver(
) -> WrappedSeleniumWebdriver:
    """Return a wrapped version of the provided selenium webdriver.

    """
    wrapped_webdriver = WrappedSeleniumWebdriver(selenium_webdriver.Firefox())
    return wrapped_webdriver
