from textual.widget import Widget
from textual.app import ComposeResult
from rich.text import Text
from textual.widgets import RichLog

class StatusWidget(Widget):
    def __init__(self):
        super().__init__()
        self.log_content = RichLog()

    def compose(self) -> ComposeResult:
        yield self.log_content

    def on_mount(self):
        self.log_content.write("IFC://")

    def log(self, message: str):
        self.log_content.write(f"IFC:// {message}")

