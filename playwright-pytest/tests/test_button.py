import logging

from pages.button_page import ButtonPage


class TestButton:

    logging.getLogger('TestButton')

    def test_primary_button_disabled(self, button_page: ButtonPage):
        assert button_page.primary_button_disabled()

    def test_primary_button_enabled(self, button_page: ButtonPage):
        assert button_page.primary_button_enabled()

    def test_hover_link_button(self, button_page):
        button_page.no_underline_link_button()
        button_page.hover_link_button()
        button_page.underline_link_button()
