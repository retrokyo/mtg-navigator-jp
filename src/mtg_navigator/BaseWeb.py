from abc import ABC, abstractmethod
from playwright.async_api import BrowserContext, Page


class BaseWeb(ABC):
    def __init__(self, context: BrowserContext, url: str):
        self.context = context
        self.url = url
        self.page: Page | None = None

    async def open(self) -> Page:
        for page in self.context.pages:
            if page.url.startswith(self.url):
                self.page = page
                return self.page
        self.page = await self.context.new_page()
        await self.page.goto(self.url)
        return self.page

    @abstractmethod
    async def search(self, search_term: str, in_stock: bool = True) -> None:
        pass
