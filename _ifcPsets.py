from textual.widgets import DataTable, Label
from textual.widget import Widget
from textual.app import ComposeResult
import ifcopenshell
import ifcopenshell.util.element
from _logbox import LogBox
from textual.message import Message
from _statusBar import StatusWidget
from textual.binding import Binding
import asyncio
import time


class PsetWidget(Widget):
    BINDINGS = [
        Binding("j", "move_down", "Move Down"),
        Binding("k", "move_up", "Move Up"),
        Binding("l", "select_pset", "Select Pset"),
    ]

    class PsetSelected(Message):
        def __init__(self, pset: str) -> None:
            super().__init__()
            self.pset = pset

    def __init__(self) -> None:
        super().__init__()
        self.category = None
        self.message_label = Label("Please, select IfcCategory", classes="warning")

    def compose(self) -> ComposeResult:
        self.table = DataTable()
        yield self.message_label
        yield self.table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("No", "Pset Name")

        table.styles.scrollbar_gutter = "stable"
        table.styles.overflow_y = "auto"

        self.update_view()

    def update_view(self) -> None:
        """Update visibility of the DataTable and Label based on the presence of a category."""
        if self.category:
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

    def action_select_pset(self) -> None:
        if self.table.row_count > 0:
            selected_row = self.table.get_row_at(self.table.cursor_row)
            if selected_row:
                pset = selected_row[1]
                self.handle_pset_selection(pset)

    def handle_pset_selection(self, pset: str) -> None:
        log_box = self.app.query_one(LogBox)
        log_box.log(f"PsetWidget: Pset selected: {pset}")
        self.post_message(self.PsetSelected(pset))

    def on_focus(self) -> None:
        self.add_class("focus")
        self.table.focus()

    def on_blur(self):
        self.remove_class("focus")

    async def update_psets(self, ifc_file, category: str) -> None:
        self.category = category
        #self.update_view()

        if not category:
            return

        table = self.query_one(DataTable)
        table.clear()
        log_box = self.app.query_one(LogBox)
        status_widget = self.app.query_one(StatusWidget)

        log_box.log(f"PsetWidget: Updating Psets for category: {category}")
        status_widget.log(f"[~~~] Updating Psets for {category}... [0.0 sec]")

        start_time = time.perf_counter()

        def fetch_psets():
            try:
                elements = ifc_file.by_type(category)
                log_box.log(f"PsetWidget: Found {len(elements)} elements of type {category}")

                psets = set()
                for element in elements:
                    element_psets = ifcopenshell.util.element.get_psets(element)
                    psets.update(element_psets.keys())
                    log_box.log(f"PsetWidget: Element {element.id()} has Psets: {list(element_psets.keys())}")
                self.update_view()
                return sorted(psets)
            except Exception as e:
                error_message = f"PsetWidget: Error fetching Psets: {str(e)}"
                log_box.log(error_message)
                self.app.query_one(StatusWidget).log(f"[---] Error during processing Psets from {category}")
                return []

        # Run the fetch_psets function in a background thread
        psets_task = asyncio.create_task(asyncio.to_thread(fetch_psets))

        # Update the timer while the task is running
        async def update_timer():
            while not psets_task.done():
                elapsed_time = time.perf_counter() - start_time
                status_widget.log(f"[~~~] Updating Psets for {category}... [{elapsed_time:.1f} sec]")
                await asyncio.sleep(0.5)

        await asyncio.gather(psets_task, update_timer())

        elapsed_time = time.perf_counter() - start_time
        sorted_psets = psets_task.result()

        if sorted_psets:
            for i, pset_name in enumerate(sorted_psets, start=1):
                table.add_row(str(i), pset_name)

            log_box.log(f"PsetWidget: Added {len(sorted_psets)} unique Psets to the table")
            status_widget.log(f"[+++] Psets from {category} added to the table in {elapsed_time:.2f} seconds")
        else:
            table.add_row("Error", "Failed to fetch Psets")
            status_widget.log(f"[---] Failed to add Psets for {category}")

        log_box.log(f"PsetWidget: Completed update for {category} in {elapsed_time:.2f} seconds")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is not None:
            pset = self.table.get_row_at(event.cursor_row)[1]
            self.handle_pset_selection(pset)
