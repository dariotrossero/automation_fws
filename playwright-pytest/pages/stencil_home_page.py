from playwright.sync_api import Page

from components.hint import SimpleHintComponent, SimpleVerticalHintWithIcon
from pages.base_page import BasePage


class StencilHomePage(BasePage):
    _URL = "http://localhost:3333"

    def __init__(self, page: Page):
        self.page = page

    def simple_hint_component_props(self, props: dict):
        hint = SimpleHintComponent(self.page, "(//div[@class='wrapper hint__lightmode sc-emerson-hint'])[17]")
        hint.validate_css_props(props)

    def simple_vertical_hint_with_icon_component_props(self):
        hint = SimpleVerticalHintWithIcon(self.page, "(//div[@class='wrapper hint__lightmode sc-emerson-hint'])[25]")
        return hint.get_distance_between_icon_and_text()

