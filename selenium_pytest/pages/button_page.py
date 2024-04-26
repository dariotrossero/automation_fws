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
        self.driver.get_element(self._LINK_BUTTON)
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

    def get_button_css_property(self, property: str) -> str:
        self.driver.switch_to_iframe('css=#storybook-preview-iframe')
        self.driver.wait_for_element_exists(self._LINK_BUTTON)
        css_property = self.driver.get_element_css_property_value(self._LINK_BUTTON, property)
        self.driver.switch_from_iframe()
        return css_property
