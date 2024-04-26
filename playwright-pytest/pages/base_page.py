class BasePage:
    BASE_PATH = "https://qa-design-system.coderfull.com"

    def open(self, timeout=None):
        self.page.goto(self._URL, timeout=timeout)
