from playwright.async_api import BrowserContext, Page, expect
from .BaseWeb import BaseWeb


class BigWeb(BaseWeb):
    def __init__(self, context: BrowserContext):
        super().__init__(context, "https://mtg.bigweb.co.jp")

    async def search(self, search_term: str, in_stock: bool = True) -> None:
        bigweb_page = await self.open()
        direct_url = f"{self.url}/cards/filter?big_keyword={search_term}&order1=price&order2=&locale=jp"

        if in_stock:
            direct_url = f"{direct_url}&has_stock=true"

        await bigweb_page.goto(direct_url)

        # loading_locator = bigweb_page.locator("div.loading")

        # search_input = bigweb_page.locator("#big_keyword")
        # await search_input.click()
        # await search_input.press_sequentially(search_term)
        # await search_input.press("Enter")

        # await expect(loading_locator).not_to_be_visible(timeout=15000)

        # order1_dropdown = bigweb_page.locator("select.sortBox-selecter[name='order1']")

        # await order1_dropdown.select_option(value="price")

        # await expect(loading_locator).not_to_be_visible(timeout=15000)

        # order2_dropdown = bigweb_page.locator("select.sortBox-selecter[name='order2']")

        # await order2_dropdown.select_option(index=0)

        # await expect(loading_locator).not_to_be_visible(timeout=15000)

        # if in_stock:
        #     in_stock_btn = bigweb_page.locator("label.btn.btn-default[for='has_stock']")
        #     await in_stock_btn.click()


# switch this to
# https://mtg.bigweb.co.jp/cards/filter?order1=price&order2=&locale=jp&listcount=48&foiltype=foil_and_nomal&has_stock=true
