import logging


from pages.label_page import LabelPage


class TestLabel:

    logging.getLogger('TestLabel')

    def test_has_css_property(self, label_page: LabelPage):
        label_page.have_css("color", "rgb(34, 22, 72)")
        label_page.have_css("background-color", "rgba(0, 0, 0, 0)")
        label_page.have_css("font-family", "Montserrat")
        label_page.have_css("width", "442px")
        label_page.have_css("height", "26px")
