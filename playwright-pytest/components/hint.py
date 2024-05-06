import logging

from playwright.sync_api import Page, expect


class HintBaseComponent:
    _BASE_LOCATOR = ""

    def __init__(self, page: Page, locator):
        self.page = page
        self._BASE_LOCATOR = locator


class SimpleHintComponent(HintBaseComponent):

    def __init__(self, page: Page, locator: str):
        super().__init__(page, locator)
        self.component = self.page.locator(self._BASE_LOCATOR)

    def validate_css_props(self, properties: dict) -> None:
        for k, v in properties.items():
            expect(self.component).to_have_css(k, v)


class SimpleVerticalHintWithIcon(HintBaseComponent):
    _ICON = "//img"
    _TEXT = "//img/../../div[3]"

    def __init__(self, page: Page, locator: str):
        super().__init__(page, locator)
        self._BASE_LOCATOR = locator
        self.icon = self.page.locator(self._BASE_LOCATOR).locator(self._ICON)
        self.text = self.page.locator(self._BASE_LOCATOR).locator(self._TEXT)

    def get_icon_props(self):
        return self.icon.bounding_box()

    def get_distance_between_icon_and_text(self):
        icon_prop = self.icon.bounding_box()
        logging.info(icon_prop)
        icon_prop["x2"] = icon_prop["x"] + icon_prop["width"]
        icon_prop["y2"] = icon_prop["y"] + icon_prop["height"]
        text_prop = self.text.bounding_box()
        logging.info(text_prop)
        text_prop["x2"] = text_prop["x"] + text_prop["width"]
        text_prop["y2"] = text_prop["y"] + text_prop["height"]
        return text_prop["y"] - icon_prop["y2"]
