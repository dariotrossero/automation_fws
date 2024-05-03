import logging


from pages.label_page import LabelPage
from pages.stencil_page import StencilPage


class TestStencil:

    logging.getLogger('TestLabel')

    def test_has_css_property(self, stencil_page: StencilPage):
        props = stencil_page.simple_hint_component_props()
        assert props["padding-bottom"] == 18
        assert props["padding-top"] == 18
        assert props["border-radius"] == 12
        assert props["padding-left"] == 24
        assert props["padding-right"] == 24

    def test_hint_with_icon(self, stencil_page: StencilPage):
        props = stencil_page.simple_vertical_hint_with_icon_component_props()
        assert props == 24

