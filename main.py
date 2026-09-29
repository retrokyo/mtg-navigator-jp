import queue
import tkinter as tk
from typing import Callable

from mtg_navigator import BrowserSession, CardNotFoundError


def build_gui() -> None:
    session = BrowserSession()
    session.start()

    root = tk.Tk()
    root.title("MTG Navigator JP")

    # BrowserSession callbacks fire on its background asyncio thread. Tkinter
    # is not thread-safe, so those callbacks must never touch widgets or call
    # root.after() directly (root.after() invoked from another thread can
    # queue a callback without waking the Tk main loop, e.g. on macOS, so it
    # sits idle until some other event nudges it). Instead they push work
    # onto this thread-safe queue, which the main thread drains itself.
    ui_queue: "queue.Queue[Callable[[], None]]" = queue.Queue()

    def poll_ui_queue() -> None:
        try:
            while True:
                update_ui = ui_queue.get_nowait()
                update_ui()
        except queue.Empty:
            pass
        root.after(100, poll_ui_queue)

    root.after(100, poll_ui_queue)

    frm = tk.Frame(root, padx=10, pady=10)
    frm.grid()

    tk.Label(frm, text="Card Name:").grid(column=0, row=0)
    card_name_entry = tk.Entry(frm, width=30)
    card_name_entry.grid(column=1, row=0)

    in_stock_var = tk.BooleanVar(value=True)
    tk.Label(frm, text="In Stock Only").grid(column=0, row=1)
    tk.Checkbutton(frm, variable=in_stock_var).grid(column=1, row=1)

    status_var = tk.StringVar(value="")
    status_label = tk.Label(frm, textvariable=status_var, fg="gray")
    status_label.grid(column=0, row=2, columnspan=2)

    def set_status(text: str, color: str = "gray") -> None:
        status_var.set(text)
        status_label.config(fg=color)

    search_button = tk.Button(frm, text="Search")
    search_button.grid(column=1, row=3)

    def on_search(event=None):
        card_name = card_name_entry.get()
        if not card_name.strip():
            set_status("Enter a card name to search.", "red")
            return

        search_button.config(state=tk.DISABLED)
        set_status(f"Searching for '{card_name}'...", "gray")

        def on_done(exc: BaseException | None) -> None:
            def update_ui() -> None:
                search_button.config(state=tk.NORMAL)
                if exc is None:
                    set_status(f"Search complete for '{card_name}'.", "green")
                elif isinstance(exc, CardNotFoundError):
                    set_status(str(exc), "red")
                else:
                    set_status(f"Search failed: {exc}", "red")

            ui_queue.put(update_ui)

        session.submit_search(card_name, in_stock_var.get(), on_done)

    search_button.config(command=on_search)

    root.bind("<Return>", on_search)

    def on_close() -> None:
        session.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    build_gui()
