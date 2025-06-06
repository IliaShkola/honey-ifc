from textual.screen import ModalScreen
from textual.widgets import OptionList, Label, Rule
from textual.widgets.option_list import Option
from textual.containers import Vertical
from textual.app import ComposeResult
from config_manager import ConfigManager


class ThemeSelectorModal(ModalScreen):
    BINDINGS = [("escape", "close_modal", "Close"),
                ("q", "close_modal", "Close"),
                ("t", "close_modal", "Close"),
                ("j", "move_down", "Move Down"),
                ("k", "move_up", "Move Up"),
                ("l", "apply_theme", "Apply Theme"),
                ("enter", "apply_theme", "Apply Theme"), ]

    THEMES = [
        "nightbee",
        "choosenbee",
        "barbee",
        "farbee",
        "daybee",
        "beethoven",
        "cyberhive",
    ]

    def __init__(self):
        super().__init__()
        self.original_theme = None

        self.config_manager = ConfigManager("honeycomb")

    def compose(self) -> ComposeResult:
        with Vertical(id="theme-box"):
            yield Label("Choose Theme", id="theme-title")
            yield Label(f"Current: {self.app.theme}", id="current-theme")
            yield Rule()
            yield OptionList(*(Option(name) for name in self.THEMES), id="theme-options")

    def on_mount(self) -> None:
        self.original_theme = self.app.theme

        option_list = self.query_one(OptionList)
        option_list.focus()

        current_theme_index = 0
        if self.original_theme in self.THEMES:
            current_theme_index = self.THEMES.index(self.original_theme)

        option_list.highlighted = current_theme_index

    def on_option_list_option_highlighted(
            self, event: OptionList.OptionHighlighted
    ) -> None:
        if event.option:
            self.app.theme = event.option.prompt
            current_label = self.query_one("#current-theme")
            current_label.update(f"Current: {event.option.prompt}")

    def on_option_list_option_selected(
            self, event: OptionList.OptionSelected
    ) -> None:
        self.app.theme = event.option.prompt
        self.config_manager.set_theme(event.option.prompt)
        self.app.pop_screen()

    def action_close_modal(self) -> None:
        if self.original_theme:
            self.app.theme = self.original_theme
            current_label = self.query_one("#current-theme")
            current_label.update(f"Current: {self.original_theme}")
        self.app.pop_screen()

    def action_apply_theme(self) -> None:
        option_list = self.query_one(OptionList)
        highlighted_index = option_list.highlighted
        if highlighted_index is not None and 0 <= highlighted_index < len(self.THEMES):

            selected_theme = self.THEMES[highlighted_index]
            self.app.theme = selected_theme
            self.config_manager.set_theme(selected_theme)
            self.app.pop_screen()

    def action_move_down(self) -> None:
        self.query_one(OptionList).action_cursor_down()

    def action_move_up(self) -> None:
        self.query_one(OptionList).action_cursor_up()