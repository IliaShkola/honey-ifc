import psutil
from textual.widgets import Static
from textual.widget import Widget
from textual.app import App, ComposeResult
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align

class SystemInfoWidget(Widget):
    """Widget to display system status information with right-center alignment."""

    cpu_usage = reactive(0.0)
    ram_usage = reactive(0.0)

    def compose(self) -> ComposeResult:
        # Adding padding to center the content vertically
        yield Static("", id="system_info", classes="right-aligned")

    def on_mount(self):
        self.update_stats()
        self.set_interval(1, self.update_stats)

    def update_stats(self):
        self.cpu_usage = psutil.cpu_percent()
        self.ram_usage = psutil.virtual_memory().percent
        self.update_display()

    def update_display(self):
        cpu_bar = self.create_bar(self.cpu_usage, "CPU")
        ram_bar = self.create_bar(self.ram_usage, "RAM")

        display_text = Text.assemble(cpu_bar, "\n", ram_bar, justify="right")
        self.query_one("#system_info").update(Align(display_text, align="center"))

    def create_bar(self, usage, label):
        """Creates a styled bar for CPU or RAM usage with right alignment."""
        color = "green" if usage < 50 else "yellow" if usage < 80 else "red"

        # Bar and label with right alignment
        bar = Text(f"{label}: {usage:.1f}% ", justify="right")
        bar.append("▏" * int(usage // 5), style=color)
        bar.append("▏" * (20 - int(usage // 5)), style="dim")

        return bar
