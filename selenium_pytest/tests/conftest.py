import logging
import os

import pytest

from pages.button_page import ButtonPage
from pages.label_page import LabelPage
from wrapper.selenium_factory import create_wrapped_selenium_chrome_webdriver, create_wrapped_selenium_gecko_webdriver, \
    create_wrapped_selenium_edge_webdriver
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver

logging.getLogger('Conftest')


@pytest.fixture(scope="function", autouse=False)
def label_page(webdriver: WrappedSeleniumWebdriver) -> LabelPage:
    label_page = LabelPage(webdriver)
    label_page.navigate()
    return label_page


@pytest.fixture(scope="function", autouse=False)
def button_page(webdriver: WrappedSeleniumWebdriver) -> ButtonPage:
    button_page = ButtonPage(webdriver)
    button_page.navigate()
    return button_page


@pytest.fixture(scope="function", autouse=False)
def webdriver() -> WrappedSeleniumWebdriver:
    browser = os.getenv("BROWSER")
    try:
        if browser.lower() == 'firefox':
            return create_wrapped_selenium_gecko_webdriver()
        elif browser.lower() == 'chrome':
            return create_wrapped_selenium_chrome_webdriver()
        elif browser.lower() == 'edge':
            return create_wrapped_selenium_edge_webdriver()
    except AttributeError:
        logging.log(level=1, msg="Browser was not defined, using chrome as default")
        return create_wrapped_selenium_chrome_webdriver()


@pytest.fixture(scope="function", autouse=True)
def setup_up_and_teardown(webdriver, request) -> None:
    webdriver.maximize_window()
    yield
    webdriver.quit_driver()

