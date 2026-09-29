import asyncio
import threading
from typing import Callable

from playwright.async_api import Playwright, async_playwright, BrowserContext, Browser

from mtg_navigator import BigWeb, Hareruya, SingleStar, fuzzy_search


class BrowserSession:
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._bigweb: BigWeb | None = None
        self._hareruya: Hareruya | None = None
        self._singlestar: SingleStar | None = None
        self._init_lock: asyncio.Lock | None = None

    def start(self) -> None:
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _ensure_browser(self) -> None:
        if self._init_lock is None:
            self._init_lock = asyncio.Lock()

        async with self._init_lock:
            if self._browser is None or not self._browser.is_connected():
                if self._playwright is None:
                    self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(headless=False)
                self._context = await self._browser.new_context()
                self._bigweb = BigWeb(self._context)
                self._hareruya = Hareruya(self._context)
                self._singlestar = SingleStar(self._context)

    async def _search(self, card_name: str, in_stock_only: bool) -> None:
        await self._ensure_browser()
        card = await fuzzy_search(card_name)
        await asyncio.gather(
            self._bigweb.search(card.name, in_stock=in_stock_only),
            self._hareruya.search(card.name, in_stock=in_stock_only),
            self._singlestar.search(card.name, in_stock=in_stock_only),
        )

    def submit_search(
        self,
        card_name: str,
        in_stock_only: bool,
        on_done: Callable[[BaseException | None], None] | None = None,
    ) -> None:
        if not card_name.strip():
            return
        fut = asyncio.run_coroutine_threadsafe(
            self._search(card_name, in_stock_only), self.loop
        )
        fut.add_done_callback(lambda f: self._on_search_done(f, on_done))

    @staticmethod
    def _on_search_done(
        fut: asyncio.Future,
        on_done: Callable[[BaseException | None], None] | None,
    ) -> None:
        exc = fut.exception()
        if exc:
            print(f"Search failed: {exc}")
        if on_done is not None:
            on_done(exc)

    async def _shutdown(self) -> None:
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()

    def close(self) -> None:
        fut = asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
        fut.result(timeout=10)  # wait for cleanup before stopping the loop
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join(timeout=5)
