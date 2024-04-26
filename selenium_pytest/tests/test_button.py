import logging

from pages.button_page import ButtonPage


class TestButton:

    logging.getLogger('TestButton')

    def test_primary_button_disabled(self, button_page: ButtonPage):
        assert button_page.primary_button_disabled()

    def test_primary_button_enabled(self, button_page: ButtonPage):
        assert button_page.primary_button_enabled()

    def test_hover_link_button(self, button_page):
        assert button_page.get_button_css_property("text-decoration") != "underline solid rgb(8, 71, 165)"
        button_page.hover_link_button()
        assert button_page.get_button_css_property("text-decoration") == "underline solid rgb(8, 71, 165)"
