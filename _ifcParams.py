from textual.widgets import DataTable, Label
from textual.widget import Widget
from textual.app import ComposeResult
from _logbox import LogBox
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from _statusBar import StatusWidget
from textual.binding import Binding
import os
import asyncio
import time
import ifcopenshell


class ParamsWidget(Widget):
    BINDINGS = [
        Binding("j", "move_down", "Move Down"),
        Binding("k", "move_up", "Move Up"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_storage = []
        self.category = None
        self.pset = None
        self.message_label = Label("Please, select IfcPset", classes="warning")

    def compose(self) -> ComposeResult:
        self.table = DataTable()
        yield self.message_label
        yield self.table

    def on_mount(self) -> None:
        self.table.cursor_type = "row"

        # Enable keyboard navigation
        self.table.styles.scrollbar_gutter = "stable"
        self.table.styles.overflow_y = "auto"

        self.update_view()

    def update_view(self) -> None:
        """Update visibility of the DataTable and Label based on the presence of a category and Pset."""
        if self.category and self.pset:
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

    def on_focus(self) -> None:
        self.add_class("focus")
        self.table.focus()

    def on_blur(self):
        self.remove_class("focus")

    async def update_params(self, ifc_file, category, pset) -> None:
        self.category = category
        self.pset = pset
        #self.update_view()

        if not category or not pset:
            return

        log_box = self.app.query_one(LogBox)
        log_box.log(f"Params Widget: Parameters updating for {self.category} with {self.pset}...")

        self.table.clear(columns=True)
        self.data_storage.clear()

        start_time = time.perf_counter()

        def fetch_params():
            try:
                elements = ifc_file.by_type(category)

                if not elements:
                    log_box.log(f"No elements found for category: {category}")
                    return [], []

                first_element = elements[0]
                pset_obj = ifcopenshell.util.element.get_pset(first_element, pset)

                if not pset_obj:
                    log_box.log(f"Property set {pset} not found for {category}")
                    return [], []

                param_names = list(pset_obj.keys())
                rows = []

                for index, element in enumerate(elements, start=1):
                    pset_obj = ifcopenshell.util.element.get_pset(element, pset)
                    if pset_obj:
                        ifc_element_name = element.Name or "Unnamed"
                        row_data = [index, ifc_element_name, pset]
                        for param in param_names:
                            value = pset_obj.get(param)
                            row_data.append("Empty" if value is None or value == "" else str(value))
                        rows.append(row_data)
                    else:
                        log_box.log(f"Property set {pset} not found for element {index}")
                self.update_view()
                return param_names, rows

            except Exception as e:
                log_box.log(f"Error fetching parameters: {str(e)}")
                return [], []

        # Run the fetch_params function in a background thread
        params_task = asyncio.create_task(asyncio.to_thread(fetch_params))

        # Update the timer while the task is running
        async def update_timer():
            while not params_task.done():
                elapsed_time = time.perf_counter() - start_time
                self.app.query_one(StatusWidget).log(f"[~~~] Updating parameters for {category}... [{elapsed_time:.1f} sec]")
                await asyncio.sleep(0.5)

        await asyncio.gather(params_task, update_timer())

        elapsed_time = time.perf_counter() - start_time
        param_names, rows = params_task.result()

        if param_names and rows:
            self.table.add_columns("No", "IfcElementName", "PsetName", *param_names)

            for row_data in rows:
                self.table.add_row(*row_data)
                self.data_storage.append(row_data)

            log_box.log(f"Params Widget: Added {len(rows)} rows with {len(param_names)} parameters")
            self.app.query_one(StatusWidget).log(f"[+++] Parameters updated for {category} with {pset} in {elapsed_time:.2f} seconds")
        else:
            self.app.query_one(StatusWidget).log(f"[---] No parameters to update for {category} with {pset}")

        log_box.log(f"Params Widget: Completed update for {self.category} with {self.pset} in {elapsed_time:.2f} seconds")

    def export_to_excel(self, ifc_file_path: str) -> None:
        log_box = self.app.query_one(LogBox)

        if not self.data_storage:
            log_box.log("[--] No data to export")
            self.app.query_one(StatusWidget).log("[--] Export failed: No data to export")
            return

        try:
            # Create a new workbook and sheet
            wb = Workbook()
            ws = wb.active
            ws.title = "IFC Data Export"

            headers = ["No", "IfcElementName", "PsetName"] + [str(column.label) for column in
                                                              self.table.columns.values()][3:]
            log_box.log(f"Headers: {headers}")  # Log the headers for debugging
            ws.append(headers)

            for row_data in self.data_storage:
                ws.append(row_data)

            # Define the range of the table
            table_range = f"A1:{chr(65 + len(headers) - 1)}{len(self.data_storage) + 1}"  # Adjust for columns and rows
            table = Table(displayName="IFCDataTable", ref=table_range)

            style = TableStyleInfo(
                name="TableStyleMedium9",  # Predefined style
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=False
            )
            table.tableStyleInfo = style

            ws.add_table(table)

            # Determine folder for export
            folder_path = os.path.dirname(ifc_file_path)
            ifc_base_name = os.path.splitext(os.path.basename(ifc_file_path))[0]
            category_safe = self.category.replace(" ", "_")
            pset_safe = self.pset.replace(" ", "_")
            file_name = f"{ifc_base_name}_{category_safe}_{pset_safe}.xlsx"
            file_path = os.path.join(folder_path, file_name)

            wb.save(file_path)

            log_box.log(f"Data exported successfully to {file_path}")
            self.app.query_one(StatusWidget).log(f"[+++] Data exported successfully to {file_path}")

        except Exception as e:
            log_box.log(f"Error exporting data: {str(e)}")
            self.app.query_one(StatusWidget).log(f"[--] Error exporting data: {str(e)}")
