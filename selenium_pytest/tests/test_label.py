import logging


from pages.label_page import LabelPage


class TestLabel:

    logging.getLogger('TestLabel')

    def test_has_css_property(self, label_page: LabelPage):
        assert label_page.get_css_property("color") == 'rgba(34, 22, 72, 1)'
        assert label_page.get_css_property("background-color") == 'rgba(0, 0, 0, 0)'
        assert label_page.get_css_property("font-family") == 'Montserrat'
        assert label_page.get_css_property("width") == '442px'
        assert label_page.get_css_property("height") == '26px'
