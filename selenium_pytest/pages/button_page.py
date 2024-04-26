from pages.base_page import BasePage
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


class ButtonPage(BasePage):
    _URL = BasePage._BASE_PATH + "?path=/docs/coderfull-button--buttons"

    _PRIMARY_BUTTON = "css=div[id='story--coderfull-button--primary-inner'] button:nth-child(1)"
    _PRIMARY_BUTTON_DISABLED = "css=div[id='story--coderfull-button--primary-inner'] button:nth-child(2)"
    _LINK_BUTTON = "css=div[id='story--coderfull-button--link-inner'] button:nth-child(1)"

    def __init__(self, webdriver: WrappedSeleniumWebdriver):
        super().__init__(webdriver)
        self.driver = webdriver

    def primary_button_disabled(self) -> bool:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        self.driver.wait_for_element_exists(self._LINK_BUTTON)
        result = self.driver.is_element_enabled(self._PRIMARY_BUTTON_DISABLED) is False
        self.driver.switch_from_iframe()
        return result

    def primary_button_enabled(self) -> bool:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        self.driver.wait_for_element_exists(self._LINK_BUTTON)
        result = self.driver.is_element_enabled(self._PRIMARY_BUTTON) is True
        self.driver.switch_from_iframe()
        return result

    def hover_link_button(self) -> None:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        self.driver.wait_for_element_exists(self._LINK_BUTTON)
        result = self.driver.hover(self._LINK_BUTTON)
        self.driver.switch_from_iframe()
        return result

    def underline_link_button(self) -> bool:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        self.driver.wait_for_element_exists(self._LINK_BUTTON)
        result = self.driver.get_element_css_property_value(self._LINK_BUTTON, "text-decoration") == "underline solid rgb(8, 71, 165)"
        self.driver.switch_from_iframe()
        return result

    def no_underline_link_button(self) -> bool:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        self.driver.wait_for_element_exists(self._LINK_BUTTON)
        result = self.driver.get_element_css_property_value(self._LINK_BUTTON, "text-decoration") != "underline solid rgb(8, 71, 165)"
        self.driver.switch_from_iframe()
        return result

