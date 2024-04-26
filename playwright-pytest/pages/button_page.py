from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ButtonPage(BasePage):
    _URL = BasePage.BASE_PATH + "?path=/docs/coderfull-button--buttons"

    _PRIMARY_BUTTON = "css=div[id='story--coderfull-button--primary-inner'] button:nth-child(1)"
    _PRIMARY_BUTTON_DISABLED = "css=div[id='story--coderfull-button--primary-inner'] button:nth-child(2)"
    _LINK_BUTTON = "css=div[id='story--coderfull-button--link-inner'] button:nth-child(1)"

    def __init__(self, page: Page):
        self.page = page
        self._iframe = self.page.frame_locator('#storybook-preview-iframe')
        self._primary_button_disabled = self._iframe.locator(self._PRIMARY_BUTTON_DISABLED)
        self._primary_button = self._iframe.locator(self._PRIMARY_BUTTON)
        self._link_button = self._iframe.locator(self._LINK_BUTTON)

    def primary_button_disabled(self) -> bool:
        return self._primary_button_disabled.is_disabled()

    def primary_button_enabled(self) -> bool:
        return self._primary_button.is_enabled()

    def hover_link_button(self) -> None:
        self._link_button.hover()

    def underline_link_button(self):
        expect(self._link_button).to_have_css("text-decoration", "underline solid rgb(8, 71, 165)")

    def no_underline_link_button(self):
        expect(self._link_button).not_to_have_css("text-decoration", "underline solid rgb(8, 71, 165)")
