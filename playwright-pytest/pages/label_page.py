from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LabelPage(BasePage):
    _URL = BasePage.BASE_PATH + "?path=/story/coderfull-autocomplete--label"

    _DROPDOWN = "input[id='headlessui-combobox-input-:r0:']"

    def __init__(self, page: Page):
        self.page = page
        self._iframe = self.page.frame_locator('#storybook-preview-iframe')
        self._dropdown = self._iframe.locator(self._DROPDOWN)

    def enter_text_dropdown(self, text: str) -> None:
        self._dropdown.fill(text)

    def have_css(self, prop: str, value: str) -> None:
        expect(self._dropdown).to_have_css(prop, value)
