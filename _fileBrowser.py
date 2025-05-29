import os
from textual.widgets import DataTable
from textual.widget import Widget
from textual.app import ComposeResult
from textual.message import Message
from textual.binding import Binding
from _logbox import LogBox
from _statusBar import StatusWidget


class BrowserWidget(Widget):
    BINDINGS = [
        Binding("j", "move_down", "Move Down"),
        Binding("k", "move_up", "Move Up"),
        Binding("l", "select_file", "Select File"),
    ]
    class FileSelected(Message):
        def __init__(self, filename: str):
            self.filename = filename
            super().__init__()

    def compose(self) -> ComposeResult:
        self.table = DataTable()
        yield self.table


    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        # table.add_columns("Name", "Size,MB", "Status")  # Add Size column
        table.add_columns("Name", "Size,MB")

        files = os.listdir("./")

        sorted_ifc_files = sorted(
            [f for f in files if f.lower().endswith(".ifc")],
            key=lambda x: x.lower()  # Alphabetical order
        )

        for filename in sorted_ifc_files:
            file_name, file_extension = os.path.splitext(filename)
            #file_format = file_extension[1:] if file_extension else "N/A"

            # Calculate file size in MB if it's a file
            if os.path.isfile(filename):
                file_size_mb = os.path.getsize(filename) / (1024 * 1024)  # Convert bytes to MB
            else:
                file_size_mb = 0.0

            # table.add_row(filename, f"{file_size_mb:.2f}", "-", key=filename)
            table.add_row(filename, f"{file_size_mb:.2f}", key=filename)
        self.table.focus()

    def action_move_down(self) -> None:
        if self.table.row_count > 0:
            current_row = self.table.cursor_row
            next_row = (current_row + 1) % self.table.row_count
            self.table.move_cursor(row=next_row)

    def action_move_up(self) -> None:
        if self.table.row_count > 0:
            current_row = self.table.cursor_row
            prev_row = (current_row - 1) % self.table.row_count
            self.table.move_cursor(row=prev_row)

    def action_select_file(self) -> None:
        if self.table.row_count > 0:
            selected_row_key = self.table.get_row_at(self.table.cursor_row)[0]
            self.handle_file_selection(selected_row_key)

    def handle_file_selection(self, filename: str) -> None:
        if filename and filename.lower().endswith('.ifc'):
            self.post_message(self.FileSelected(filename))
            self.app.query_one(LogBox).log(f"Selected IFC file: {filename}")
            self.app.query_one(StatusWidget).log(f"[+++] IFC file {filename} has been opened.")
        else:
            self.app.query_one(LogBox).log(f"Selected file is not an IFC!")
            self.app.query_one(StatusWidget).log("[!!!] Selected file is not an IFC!")

    def on_focus(self) -> None:
        self.add_class("focus")
        self.table.focus()

    def on_blur(self):
        self.remove_class("focus")

    def on_data_table_focus(self):
        self.add_class("focus")

    def on_data_table_blur(self):
        self.remove_class("focus")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.handle_file_selection(event.row_key.value)
