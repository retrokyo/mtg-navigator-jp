from playwright.async_api import BrowserContext, expect
from mtg_navigator.BaseWeb import BaseWeb


class SingleStar(BaseWeb):
    def __init__(self, context: BrowserContext):
        super().__init__(context, "https://www.singlestar.jp")

    async def search(self, search_term: str, in_stock: bool = True) -> None:
        singlestar_page = await self.open()
        direct_url = (
            f"{self.url}/product-list/0/0/photo?keyword={search_term}&order=asc"
        )

        if in_stock:
            direct_url = f"{direct_url}&available=1"

        await singlestar_page.goto(direct_url)

        # search_input = singlestar_page.locator("input[type='text'][name='keyword'].form.searchsuggest")
        # await search_input.click()
        # await search_input.press_sequentially(search_term)
        # await search_input.press("Enter")

        # sort = singlestar_page.locator("select[name='order'][id='order']")
        # await sort.select_option(value="asc")

        # if in_stock:
        #     in_stock_btn = singlestar_page.locator("label.check_label[for='available']")
        #     await in_stock_btn.click()

    # https://www.singlestar.jp/product-list/0/0/photo?keyword=Reliquary+Tower&num=100&img=160&available=1&order=asc
