from playwright.async_api import BrowserContext, Page, expect
from .BaseWeb import BaseWeb


class Hareruya(BaseWeb):
    def __init__(self, context: BrowserContext):
        super().__init__(context, "https://www.hareruyamtg.com")

    async def search(self, search_term: str, in_stock: bool = True) -> None:
        hareruya_page = await self.open()
        loading_locator = hareruya_page.locator("xpath=//div[@class='loadingImg']")

        search_input = hareruya_page.locator(
            "xpath=//input[@id='leftmenu_search_goods_name']"
        ).and_(hareruya_page.locator("xpath=//input[@class='name_ unisuggest']"))

        search_input_value = await search_input.input_value()
        if search_input_value.strip() != "":
            await search_input.clear()

        await search_input.click()
        await search_input.press_sequentially(search_term)
        await search_input.press("Enter")

        await expect(loading_locator).to_be_visible(timeout=10000)
        await expect(loading_locator).not_to_be_visible(timeout=10000)

        sort_links = hareruya_page.locator("span[data-sort='price'][data-order='ASC']")
        await sort_links.click()

        await expect(loading_locator).to_be_visible(timeout=10000)
        await expect(loading_locator).not_to_be_visible(timeout=10000)

        if in_stock:
            in_stock_checkbox = hareruya_page.get_by_alt_text(
                "在庫有りのみ表示する"
            ).and_(
                hareruya_page.locator(
                    "xpath=//img[@src='/ja/assets/img/stock_available.png']"
                )
            )
            await in_stock_checkbox.click()


async def open(browser_context: BrowserContext) -> Page:
    hareruya_page = None
    for page in browser_context.pages:
        if page.url.startswith("https://www.hareruyamtg.com"):
            hareruya_page = page

    if hareruya_page is None:
        hareruya_page = await browser_context.new_page()

    await hareruya_page.goto("https://www.hareruyamtg.com")

    return hareruya_page
