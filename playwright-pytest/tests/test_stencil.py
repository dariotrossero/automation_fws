import logging

from pages.stencil_home_page import StencilHomePage


class TestStencil:
    logging.getLogger('TestStencil')

    def test_hint_has_css_property(self, stencil_home_page: StencilHomePage):
        css = {"padding-bottom": "18px",
               "padding-top": "18px",
               "border-radius": "12px",
               "padding-left": "24px",
               "padding-right": "24px"}
        stencil_home_page.simple_hint_component_props(css)

    def test_hint_with_icon(self, stencil_home_page: StencilHomePage):
        props = stencil_home_page.simple_vertical_hint_with_icon_component_props()
        assert int(props) == 24
