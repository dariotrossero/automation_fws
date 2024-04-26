from copy import copy
from typing import List, TypeVar

from selenium.webdriver.remote.webdriver import WebDriver

from wrapper.pypom import ByCss, CssFriendlyBy, By

T = TypeVar('T', bound='PageSection')


class PageSection(ByCss):
    nth_child_offset = 0
    root: CssFriendlyBy = None

    def __init__(
        self,
        webdriver=None,
        root: CssFriendlyBy = None,
        nth_child: int = None,
        append_css: str = None,
        prepend_css: str = None,
        timeout: int = None,
    ):
        """Sets driver on all locators.

        Args:
            webdriver: driver executing commands, must include unless
            this section has been instantiated as a class attribute on
            a Page class
            root: ancestor element for all others
            append_css: append any css value to the root css
            prepend_css: prepend any css value to the root css
            nth_child: append an nth-child value to the root css. base 1 index.
            timeout: default timeout for each element in this class


        Raises:
            ValueError: if root element hasn't been set, passed in, or isn't
            css friendly.
        """
        self.webdriver = webdriver

        self.root = root or self.root

        if self.root is None:
            raise ValueError('Must set or pass in a root element')

        if not issubclass(type(self.root), CssFriendlyBy):
            raise ValueError('root element must be one of ByID, ByCss, '
                             'ByClass, ByName, ByClass, or ByTag')

        self.root = ByCss(self.root.css)
        if append_css:
            self.root.value += append_css
        if prepend_css:
            self.root.value = prepend_css + self.root.value
        if nth_child:
            self.root.value += f':nth-child({nth_child})'

        super().__init__(
            value=self.root.css,
            driver=getattr(self.webdriver, 'driver', webdriver),
            timeout=timeout
        )

        class_attrs = dict()
        for class_ in self.__class__.__mro__:
            class_attrs = {**class_.__dict__, **class_attrs}

        inst_attrs = self.__dict__

        for name, attr in {**class_attrs, **inst_attrs}.items():
            if isinstance(attr, PageSection):
                copy_section = copy(attr)
                copy_section._set_driver_from_parent(self.webdriver, timeout)
                copy_section._clean_attrs(copy_section.root)
                copy_section._prepend_root(self.root)
                self.__dict__[name] = copy_section
            elif isinstance(attr, By):
                if isinstance(attr, CssFriendlyBy) and attr is not self.root:
                    copy_by = ByCss(
                        value=f"{self.root.css} {attr.css}",
                        timeout=attr.default_timeout
                    )
                else:
                    copy_by = copy(attr)

                if attr.timeout_is_default and timeout:
                    copy_by.default_timeout = timeout
                    copy_by.timeout_is_default = False
                copy_by.driver = self.driver

                self.__dict__[name] = copy_by

    def _clean_attrs(self, root: CssFriendlyBy = None):
        inst_attrs = self.__dict__
        root = root or copy(self.__class__.root)
        self.root = ByCss(root.css, root.driver, root.default_timeout)

        for name, attr in inst_attrs.items():
            if isinstance(attr, CssFriendlyBy) and name != 'root':
                copy_by = ByCss(value=attr.css, driver=self.driver, timeout=attr.default_timeout)
                self.__dict__[name] = copy_by

    def _prepend_root(self, prepend: CssFriendlyBy):
        inst_attrs = self.__dict__

        for name, attr in inst_attrs.items():
            if isinstance(attr, CssFriendlyBy):
                attr.value = f"{prepend.css} {attr.css}"

            elif isinstance(attr, PageSection):
                attr._clean_attrs()
                attr._prepend_root(prepend)

    def _set_driver_from_parent(self, webdriver, timeout: int = None):
        """Set a driver on all By elements.
        Args:
            webdriver: driver to set
            timeout: timeout
        """
        self.webdriver = webdriver
        self.driver: WebDriver = getattr(webdriver, 'driver', webdriver)
        for attr in self.__dict__.values():
            if isinstance(attr, PageSection):
                attr._set_driver_from_parent(webdriver)
            elif isinstance(attr, By):
                attr.driver = self.driver
                if attr.timeout_is_default and timeout:
                    attr.default_timeout = timeout
                    attr.timeout_is_default = False

    @property
    def value(self) -> str:
        return self.root.value

    @value.setter
    def value(self, value):
        return  # value should only be set through the root

    @property
    def page_source(self) -> str:
        return self.root.get_attribute_value('outerHTML')

    def find_all(self: T, webdriver=None, offset: int = None) -> List[T]:
        """Find all sections matching the root.
        Appends an nth-child to each found section's root. If the sections you seek to find
        live at different levels of the DOM, this function will

        Args:
            webdriver: webdriver to use, defaults to webdriver in config
            offset: number to offset the child index by for each element
        """
        offset = offset if offset is not None else self.nth_child_offset
        count = self.root.get_count()
        sections = [
            self.__class__(
                webdriver=self.webdriver,
                root=copy(self.root),
                nth_child=i + 1 + offset
            )
            for i in range(count)
        ]
        return sections

    def find_all_when_exists(
            self: T,
            timeout: int = None,
            raise_on_timeout: bool = True,
            msg: str = None,
            offset: int = None
    ) -> List[T]:
        """Finds all matching elements once at least one exists

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception
            offset: number to offset the child index by for each element

        Raises:
            WaitTimeoutError: No matching elements exist after :timeout: seconds
        """
        offset = offset if offset is not None else self.nth_child_offset
        count = len(self.root.find_all_when_exists(
            timeout=timeout, msg=msg, raise_on_timeout=raise_on_timeout
        ))
        sections = [
            self.__class__(
                webdriver=self.webdriver,
                root=copy(self.root),
                nth_child=i + 1 + offset
            )
            for i in range(count)
        ]
        return sections

    def find_all_when_visible(
            self: T,
            timeout: int = None,
            raise_on_timeout: bool = True,
            msg: str = None,
            offset: int = None
    ) -> List[T]:
        """Finds all matching elements once at least one exists

        Args:
            timeout: number of seconds to wait
            raise_on_timeout: raise an error if wait times out
            msg: message to print with exception
            offset: number to offset the child index by for each element

        Raises:
            WaitTimeoutError: No matching elements visible after :timeout: seconds
        """
        offset = offset if offset is not None else self.nth_child_offset
        count = len(self.root.find_all_when_visible(
            timeout=timeout, msg=msg, raise_on_timeout=raise_on_timeout
        ))
        sections = [
            self.__class__(
                webdriver=self.webdriver,
                root=copy(self.root),
                nth_child=i + 1 + offset
            )
            for i in range(count)
        ]
        return sections
