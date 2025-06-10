from textual.widgets import RichLog
from textual.widget import Widget
from textual.app import ComposeResult

class LogBox(Widget):
    def __init__(self):
        super().__init__()
        self.log_content = RichLog()

    def compose(self) -> ComposeResult:
        yield self.log_content

    def on_mount(self):
        self.log_content.write("Log messages will appear here...")

    def log(self, message: str):
        self.log_content.write(message)
        self.log_content.scroll_end(animate=False)

