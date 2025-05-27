from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Static
from textual.widget import Widget


class FooterBox(Widget):
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("\[q] - Exit. \[i] - App Info. \[t] - Select theme")
