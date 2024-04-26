from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


class BasePage:
    _BASE_PATH = "https://qa-design-system.coderfull.com/"

    def __init__(self, webdriver: WrappedSeleniumWebdriver):
        self.webdriver = webdriver

    def navigate(self) -> None:
        self.webdriver.open(self._URL)
