from textual.message import Message
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import DataTable, Label
from textual.binding import Binding
from _logbox import LogBox
from _statusBar import StatusWidget


class CategoryWidget(Widget):
    BINDINGS = [
        Binding("j", "move_down", "Move Down"),
        Binding("k", "move_up", "Move Up"),
        Binding("l", "select_category", "Select Category"),
    ]

    class CategorySelected(Message):
        def __init__(self, category: str) -> None:
            super().__init__()
            self.category = category

    def __init__(self) -> None:
        super().__init__()
        self.ifc_file = None
        self.message_label = Label("Please, select IfcFile", classes="warning")

    def compose(self) -> ComposeResult:
        self.table = DataTable()
        yield self.message_label
        yield self.table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("No", "Ifc Category", "Amount")

        table.styles.scrollbar_gutter = "stable"
        table.styles.overflow_y = "auto"

        self.update_view()

    def update_view(self) -> None:
        """Update visibility of the DataTable and Label based on the presence of an IFC file."""
        if self.ifc_file:
            self.message_label.display = False
            self.table.display = True
        else:
            self.message_label.display = True
            self.table.display = False

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

    def action_select_category(self) -> None:
        if self.table.row_count > 0:
            selected_row = self.table.get_row_at(self.table.cursor_row)
            if selected_row:
                category = selected_row[1]
                self.handle_category_selection(category)

    def handle_category_selection(self, category: str) -> None:
        log_box = self.app.query_one(LogBox)
        log_box.log(f"CategoryWidget: Category selected: {category}")
        self.post_message(self.CategorySelected(category))

    def on_focus(self) -> None:
        self.add_class("focus")
        self.table.focus()

    def on_blur(self):
        self.remove_class("focus")

    def update_categories(self, ifc_file, filename) -> None:
        self.ifc_file = ifc_file
        self.update_view()

        if not ifc_file and not filename:
            return

        table = self.query_one(DataTable)
        table.clear()
        log_box = self.app.query_one(LogBox)

        try:
            log_box.log("Processing IFC file for categories")
            products = ifc_file.by_type("IfcProduct")
            categories = {}

            for product in products:
                entity_type = product.is_a()
                if entity_type not in categories:
                    categories[entity_type] = 0
                categories[entity_type] += 1

            log_box.log(f"Found {len(categories)} IfcProduct-related categories")
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

            for i, (category, amount) in enumerate(sorted_categories, start=1):
                table.add_row(str(i), category, str(amount))

            log_box.log("Categories table updated")

            self.app.query_one(StatusWidget).log(
                f"[+++] IFC file {filename} has been opened. IfcCategories has been updated.")
        except Exception as e:
            error_message = f"Error processing IFC file: {str(e)}"
            table.add_row("Error", error_message, "")
            log_box.log(error_message)
            self.app.query_one(StatusWidget).log(f"[---] Error during opening IFC file {filename}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is not None:
            category = self.table.get_row_at(event.cursor_row)[1]
            self.handle_category_selection(category)
