from copy import copy

from selenium.webdriver.remote.webdriver import WebDriver
import urllib.parse as urlparse
from urllib.parse import urlencode

from wrapper.pypom import PageSection, By


class Page:

    def __init__(self, webdriver=None, timeout: int = None):
        """Sets driver on all locators

        Args:
            webdriver: driver executing commands
            timeout: default timeout for each element in this class
        """
        self.webdriver = webdriver
        # support for wrapped vs raw driver
        self.raw_webdriver: WebDriver = getattr(webdriver, 'driver', webdriver)
        self.timeout = timeout

        class_attrs = dict()
        for class_ in self.__class__.__mro__:
            class_attrs = {**class_.__dict__, **class_attrs}

        inst_attrs = self.__dict__

        for name, attr in {**class_attrs, **inst_attrs}.items():
            if isinstance(attr, PageSection):
                copy_section = copy(attr)
                copy_section._set_driver_from_parent(self.webdriver, self.timeout)
                self.__dict__[name] = copy_section
            elif isinstance(attr, By):
                copy_by: By = copy(attr)
                copy_by.driver = self.raw_webdriver
                if attr.timeout_is_default and self.timeout:
                    copy_by.default_timeout = timeout
                    copy_by.timeout_is_default = False
                self.__dict__[name] = copy_by

    @property
    def page_source(self) -> str:
        return self.raw_webdriver.page_source

    def open(self, url: str, **url_kwargs):
        """Open the page

        Args:
            url: url to open
            url_kwargs: url query params
        """
        self.raw_webdriver.get(self.build_url(url, **url_kwargs))

    @staticmethod
    def build_url(url, **url_kwargs):
        """Builds and encodes a url

        Args:
            url: url to encode
            url_kwargs: url query params
        """

        url_parts = list(urlparse.urlparse(url))
        query = urlparse.parse_qsl(url_parts[4])

        for k, v in url_kwargs.items():
            query.append((k, v))

        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)

    def get_title(self) -> str:
        return self.raw_webdriver.title
