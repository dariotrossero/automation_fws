import logging

import pytest

from conf.config import Config
from pages.button_page import ButtonPage
from pages.label_page import LabelPage
from pages.stencil_page import StencilPage
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
def stencil_page(webdriver: WrappedSeleniumWebdriver) -> StencilPage:
    stencil_page = StencilPage(webdriver)
    stencil_page.navigate()
    return stencil_page

@pytest.fixture(scope="function", autouse=False)
def webdriver() -> WrappedSeleniumWebdriver:
    browser = Config.browser()
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # if test failed
    if rep.when == "call" and rep.failed:
        try:
            # Accessing the fixture from the test
            driver = item.funcargs['webdriver'].driver
        except KeyError:
            logging.log(1, "No driver fixture found, skip taking screenshot")
            # No driver fixture found, skip taking screenshot
            return

        # Take screenshot
        try:
            if not Config.save_screenshot():
                return
            screenshot_path = f"screenshots/screenshot_{item.name}.png"
            driver.save_screenshot(screenshot_path)
            print(f"\nScreenshot saved as {screenshot_path}")
        except Exception as e:
            print(f"\nFailed to capture screenshot: {str(e)}")
