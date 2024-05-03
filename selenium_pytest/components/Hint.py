from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


class HintBaseComponent:
    _BASE_LOCATOR = ""

    def __init__(self, webdriver: WrappedSeleniumWebdriver, locator):
        self.driver = webdriver
        self._BASE_LOCATOR = locator


class SimpleHintComponent(HintBaseComponent):

    def __init__(self, webdriver: WrappedSeleniumWebdriver, locator: str):
        super().__init__(webdriver, locator)
        self.driver = webdriver
        self._BASE_LOCATOR = locator

    def get_css_properties(self) -> dict:
        return self.driver.get_css_information(self._BASE_LOCATOR)


class SimpleVerticalHintWithIcon(HintBaseComponent):
    _ICON = "//img"
    _TEXT = "//img/../../div[3]"

    def __init__(self, webdriver: WrappedSeleniumWebdriver, locator: str):
        super().__init__(webdriver, locator)
        self.driver = webdriver
        self._BASE_LOCATOR = locator

    def get_icon_props(self):
        return self.driver.get_css_information(self._BASE_LOCATOR + self._ICON)

    def get_distance_between_icon_and_text(self):
        icon_prop = self.driver.get_css_information(self._BASE_LOCATOR + self._ICON)
        text_prop = self.driver.get_css_information(self._BASE_LOCATOR + self._TEXT)
        return text_prop["y1"] - icon_prop["y2"]
