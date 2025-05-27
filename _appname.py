import psutil
from textual.widgets import Static
from textual.widget import Widget
from textual.app import App, ComposeResult


class AppNameWidget(Widget):
    """Widget to display the application name."""

    def compose(self) -> ComposeResult:
        yield Static("*** Honeycomb ***")
