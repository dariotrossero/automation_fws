from components.Hint import SimpleHintComponent, SimpleVerticalHintWithIcon
from pages.base_page import BasePage
from wrapper.wrapped_selenium_webdriver import WrappedSeleniumWebdriver


class StencilPage(BasePage):
    _URL = BasePage._BASE_PATH

    def __init__(self, webdriver: WrappedSeleniumWebdriver):
        super().__init__(webdriver)
        self.driver = webdriver

    def simple_hint_component_props(self):
        self.driver.wait_for_element_exists("xpath=(//div[@class='wrapper hint__lightmode sc-emerson-hint'])[17]")
        hint = SimpleHintComponent(self.driver, "xpath=(//div[@class='wrapper hint__lightmode sc-emerson-hint'])[17]")
        return hint.get_css_properties()

    def simple_vertical_hint_with_icon_component_props(self):
        self.driver.wait_for_element_exists("xpath=(//div[@class='wrapper hint__lightmode sc-emerson-hint'])[25]")
        hint = SimpleVerticalHintWithIcon(self.driver, "xpath=(//div[@class='wrapper hint__lightmode sc-emerson-hint'])[25]")
        return hint.get_distance_between_icon_and_text()

