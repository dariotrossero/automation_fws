"""Functions to create Selenium Webdriver or Appium instances."""

import logging

from selenium import webdriver as selenium_webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.remote.remote_connection import LOGGER

from conf.config import Config
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver

LOGGER.setLevel(logging.WARNING)


def create_wrapped_selenium_chrome_webdriver(
) -> WrappedSeleniumWebdriver:
    """Return a wrapped version of the provided selenium webdriver.

    """
    chrome_options: ChromeOptions = ChromeOptions()
    # Configure Chrome to run in headless mode
    if Config.headless():
        chrome_options.add_argument('--headless')
    wrapped_webdriver = WrappedSeleniumWebdriver(selenium_webdriver.Chrome(options=chrome_options))
    return wrapped_webdriver


def create_wrapped_selenium_gecko_webdriver(
) -> WrappedSeleniumWebdriver:
    """Return a wrapped version of the provided selenium webdriver.

    """
    firefox_options: FirefoxOptions = FirefoxOptions()
    # Configure Firefox to run in headless mode
    if Config.headless():
        firefox_options.add_argument("--headless")
    wrapped_webdriver = WrappedSeleniumWebdriver(selenium_webdriver.Firefox(options=firefox_options))
    return wrapped_webdriver


def create_wrapped_selenium_edge_webdriver(
) -> WrappedSeleniumWebdriver:
    """Return a wrapped version of the provided selenium webdriver.

    """
    edge_options: EdgeOptions = EdgeOptions()
    # Configure Firefox to run in headless mode
    if Config.headless():
        edge_options.add_argument("--headless")
    wrapped_webdriver = WrappedSeleniumWebdriver(selenium_webdriver.Edge(options=edge_options))
    return wrapped_webdriver
