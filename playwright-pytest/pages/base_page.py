class BasePage:
    #BASE_PATH = "https://qa-design-system.coderfull.com"
    BASE_PATH = "http://localhost:3333/"

    def open(self, timeout=None):
        self.page.goto(self._URL, timeout=timeout)
