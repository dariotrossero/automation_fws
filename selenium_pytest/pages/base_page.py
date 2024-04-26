from conf.config import Config
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


class BasePage:
    _BASE_PATH = Config.base_url()

    def __init__(self, webdriver: WrappedSeleniumWebdriver):
        self.webdriver = webdriver

    def navigate(self) -> None:
        self.webdriver.open(self._URL)
