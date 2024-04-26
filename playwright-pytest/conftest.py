import pytest

from pages.button_page import ButtonPage
from pages.label_page import LabelPage


@pytest.fixture(autouse=False)
def label_page(page):
    label_page = LabelPage(page)
    label_page.open()
    return label_page


@pytest.fixture(autouse=False)
def button_page(page):
    button_page = ButtonPage(page)
    button_page.open()
    return button_page
