import pytest

from pages.button_page import ButtonPage
from pages.label_page import LabelPage
from wrapper.selenium_factory import create_wrapped_selenium_chrome_webdriver
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


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
    return create_wrapped_selenium_chrome_webdriver()


@pytest.fixture(scope="function", autouse=True)
def _test(webdriver) -> None:
    yield
    webdriver.quit_driver()
