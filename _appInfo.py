from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Label, Static, Rule, Markdown
from textual.containers import Grid, Horizontal, Vertical, Container

from __version__ import __version__


class InfoModal(ModalScreen):
    """A modal screen to display app and developer information."""
    BINDINGS = [("i", "close_modal", "Close"),
                ("escape", "close_modal", "Close"),
                ("q", "close_modal", "Close"),
                ("j", "scroll_down", "Scroll Down"),
                ("k", "scroll_up", "Scroll Up"),
                ("down", "scroll_down", "Scroll Down"),
                ("up", "scroll_up", "Scroll Up"),
                ("g", "scroll_home", "Go to Top"),
                ("shift+g", "scroll_end", "Go to Bottom")]

    def __init__(self):
        super().__init__()
        self.app_name = "honeycomb"
        self.version = f"v.{__version__}"
        self.description = "A sleek and user-friendly tool for exploring and exporting IFC file data — fast and hassle-free."
        self.developer = "IliaShkola"
        self.controls = """
        Navigation Controls

        Section Switching
          1 — File Explorer  
          2 — IFC Categories  
          3 — IFC Psets  
          4 — IFC Properties

        Movement
          j / ↓ — Move down  
          k / ↑ — Move up   
          l / ENTER — Select

        Exporting
         e - Export IFC data to xlsx
         p - Expand IFCProperty tab

        Additional
          q — Quit application  
          Enter — Select item / toggle section  
          i — Show Help / Shortcuts
        """.strip()

    def compose(self) -> ComposeResult:
        ascii_title = r"""

██   ██  ██████  ███    ██ ███████ ██    ██ 
██   ██ ██    ██ ████   ██ ██       ██  ██  
███████ ██    ██ ██ ██  ██ █████     ████   
██   ██ ██    ██ ██  ██ ██ ██         ██    
██   ██  ██████  ██   ████ ███████    ██                              
                """.strip("\n")

        with Vertical(id="dialog") as dialog:
            yield Static(ascii_title, id="ascii_art")
            yield Static(f"{self.version}", classes="info-label", shrink=True)
            yield Label(f"Developer: {self.developer}", classes="info-label")
            yield Rule()
            yield Static(f"{self.description}", classes="info-label", shrink=True)
            yield Rule()
            yield Static(self.controls, classes="info-label", shrink=True)

    def on_mount(self) -> None:
        dialog = self.query_one("#dialog")
        dialog.focus()

    def action_close_modal(self) -> None:
        self.app.pop_screen()

    def action_scroll_down(self) -> None:
        dialog = self.query_one("#dialog")
        dialog.scroll_down(animate=False)

    def action_scroll_up(self) -> None:
        dialog = self.query_one("#dialog")
        dialog.scroll_up(animate=False)

    def action_scroll_home(self) -> None:
        dialog = self.query_one("#dialog")
        dialog.scroll_home(animate=False)

    def action_scroll_end(self) -> None:
        dialog = self.query_one("#dialog")
        dialog.scroll_end(animate=False)
        dialog.scroll_end(animate=False)