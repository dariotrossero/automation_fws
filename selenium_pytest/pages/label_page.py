from pages.base_page import BasePage
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


class LabelPage(BasePage):
    _URL = BasePage._BASE_PATH + "?path=/story/coderfull-autocomplete--label"
    _DROPDOWN = "css=input[id='headlessui-combobox-input-:r0:']"

    def __init__(self, webdriver: WrappedSeleniumWebdriver):
        super().__init__(webdriver)
        self.driver = webdriver

    def get_css_property(self, prop: str) -> str:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        value = self.webdriver.get_element_css_property_value(self._DROPDOWN, prop)
        self.driver.switch_from_iframe()
        return value


