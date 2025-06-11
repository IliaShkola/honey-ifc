import os
import asyncio
import time
import re
from typing import List, Tuple, Optional, Dict, Set

from textual.widgets import DataTable, Label
from textual.widget import Widget
from textual.app import ComposeResult
from textual.binding import Binding
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import ifcopenshell

from ._logbox import LogBox
from ._statusBar import StatusWidget


class OptimizedExtractParametersHelper:
    """Optimized helper for parameter extraction"""

    @staticmethod
    def _get_element_pset_fast(element, pset_name):
        """Fast property set extraction with minimal fallback"""
        try:
            pset_data = ifcopenshell.util.element.get_pset(element, pset_name)
            if pset_data:
                return pset_data
        except:
            pass

        try:
            all_psets = ifcopenshell.util.element.get_psets(element)
            return all_psets.get(pset_name, {})
        except:
            return {}

    @staticmethod
    def _safe_get_attribute(element, attribute_name, default_value="Empty"):
        try:
            value = getattr(element, attribute_name, None)
            if value is not None:
                # Специальная обработка для имени элемента
                if attribute_name == 'Name':
                    value_str = str(value)
                    # Убираем ID в конце строки (например: ":1234567" или "#1234567")
                    cleaned_value = re.sub(r'[:#]\d+$', '', value_str).strip()
                    return cleaned_value if cleaned_value else default_value
                return value
            return default_value
        except:
            return default_value


class OptimizedIFCDataProcessor:
    """Optimized IFC data processor"""

    @staticmethod
    def extract_parameters_optimized(ifc_file, category: str, pset: str) -> Tuple[List[str], List[List]]:
        """Extract parameters with caching for better performance"""
        try:
            elements = ifc_file.by_type(category)
            if not elements:
                return [], []

            # Single pass to collect all parameters and cache element data
            all_params = set()
            elements_data = []

            for element in elements:
                pset_data = OptimizedExtractParametersHelper._get_element_pset_fast(element, pset)
                if pset_data:
                    all_params.update(pset_data.keys())

                elements_data.append((element, pset_data))

            # Handle case with no parameters
            if not all_params:
                rows = []
                for index, (element, _) in enumerate(elements_data, start=1):
                    try:
                        element_name = OptimizedExtractParametersHelper._safe_get_attribute(element, 'Name', "Unnamed")
                        ifc_category = element.is_a()
                        predefined_type = OptimizedExtractParametersHelper._safe_get_attribute(element,
                                                                                               'PredefinedType',
                                                                                               "Empty")
                        element_guid = OptimizedExtractParametersHelper._safe_get_attribute(element, 'GlobalId',
                                                                                            "Empty")

                        row_data = [index, ifc_category, predefined_type, element_name, pset, element_guid]
                        rows.append(row_data)
                    except Exception as row_error:
                        error_row = [index, "ERROR", "ERROR", f"Error: {str(row_error)}", pset, "ERROR"]
                        rows.append(error_row)

                return [], rows

            param_names = sorted(list(all_params))
            rows = []

            # Build rows for all elements
            for index, (element, pset_data) in enumerate(elements_data, start=1):
                try:
                    element_name = OptimizedExtractParametersHelper._safe_get_attribute(element, 'Name', "Unnamed")
                    ifc_category = element.is_a()
                    predefined_type = OptimizedExtractParametersHelper._safe_get_attribute(element, 'PredefinedType',
                                                                                           "Empty")
                    element_guid = OptimizedExtractParametersHelper._safe_get_attribute(element, 'GlobalId', "Empty")

                    row_data = [index, ifc_category, predefined_type, element_name, pset]

                    for param in param_names:
                        value = pset_data.get(param) if pset_data else None
                        formatted_value = "Empty" if value in (None, "") else str(value)
                        row_data.append(formatted_value)

                    row_data.append(element_guid)
                    rows.append(row_data)

                except Exception as row_error:
                    error_row = [index, "ERROR", "ERROR", f"Error: {str(row_error)}", pset]
                    for _ in param_names:
                        error_row.append("ERROR")
                    error_row.append("ERROR")
                    rows.append(error_row)

            return param_names, rows

        except Exception as e:
            raise Exception(f"Error extracting parameters: {str(e)}")


class ParamsWidget(Widget):
    """Optimized widget for displaying IFC parameters"""

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
        self.table.styles.scrollbar_gutter = "stable"
        self.table.styles.overflow_y = "auto"
        self.update_view()

    def update_view(self) -> None:
        if self.category and self.pset:
            self.message_label.display = False
            self.table.display = True
        else:
            self.message_label.display = True
            self.table.display = False

    def _move_cursor_safely(self, direction: int) -> None:
        if self.table.row_count > 0:
            current_row = self.table.cursor_row
            new_row = (current_row + direction) % self.table.row_count
            self.table.move_cursor(row=new_row)

    def action_move_down(self) -> None:
        self._move_cursor_safely(1)

    def action_move_up(self) -> None:
        self._move_cursor_safely(-1)

    def on_focus(self) -> None:
        self.add_class("focus")
        self.table.focus()

    def on_blur(self):
        self.remove_class("focus")

    async def update_params(self, ifc_file, category, pset) -> None:
        self.category = category
        self.pset = pset

        if not category or not pset:
            return

        log_box = self.app.query_one(LogBox)
        status_widget = self.app.query_one(StatusWidget)

        log_box.log(f"Params Widget: Parameters updating for {self.category} with {self.pset}...")

        self.table.clear(columns=True)
        self.data_storage.clear()
        start_time = time.perf_counter()

        try:
            params_task = asyncio.create_task(
                asyncio.to_thread(OptimizedIFCDataProcessor.extract_parameters_optimized, ifc_file, category, pset)
            )

            await self._update_timer_while_processing(params_task, start_time, status_widget, category)

            elapsed_time = time.perf_counter() - start_time
            param_names, rows = params_task.result()

            if param_names and rows:
                self.table.add_columns("No", "IfcCategory", "PredefinedType", "IfcElementName", "PsetName",
                                       *param_names, "GUID")

                for row_data in rows:
                    self.table.add_row(*row_data)
                    self.data_storage.append(row_data)

                log_box.log(f"Params Widget: Added {len(rows)} rows with {len(param_names)} parameters")
                status_widget.log(f"[+++] Parameters updated for {category} with {pset} in {elapsed_time:.2f} seconds")
            else:
                status_widget.log(f"[---] No parameters found for {category} with {pset}")

            self.update_view()
            log_box.log(
                f"Params Widget: Completed update for {self.category} with {self.pset} in {elapsed_time:.2f} seconds")

        except Exception as e:
            log_box.log(f"Error fetching parameters: {str(e)}")
            status_widget.log(f"[--] Error: {str(e)}")

    async def _update_timer_while_processing(self, task, start_time: float, status_widget, category: str) -> None:
        while not task.done():
            elapsed_time = time.perf_counter() - start_time
            status_widget.log(f"[~~~] Updating parameters for {category}... [{elapsed_time:.1f} sec]")
            await asyncio.sleep(0.5)

    def _generate_export_file_path(self, ifc_file_path: str) -> str:
        folder_path = os.path.dirname(ifc_file_path)
        ifc_base_name = os.path.splitext(os.path.basename(ifc_file_path))[0]

        category_safe = self.category.replace(" ", "_").replace("/", "_")
        pset_safe = self.pset.replace(" ", "_").replace("/", "_")

        file_name = f"{ifc_base_name}_{category_safe}_{pset_safe}.xlsx"
        return os.path.join(folder_path, file_name)

    def _create_excel_table(self, ws, headers: List[str], data_count: int) -> None:
        table_range = f"A1:{chr(65 + len(headers) - 1)}{data_count + 1}"
        table = Table(displayName="IFCDataTable", ref=table_range)

        style = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )
        table.tableStyleInfo = style
        ws.add_table(table)

    def export_to_excel(self, ifc_file_path: str) -> None:
        log_box = self.app.query_one(LogBox)
        status_widget = self.app.query_one(StatusWidget)

        if not self.data_storage:
            error_msg = "No data to export"
            log_box.log(f"[--] {error_msg}")
            status_widget.log(f"[--] Export failed: {error_msg}")
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "IFC Data Export"

            headers = ["No", "IfcCategory", "PredefinedType", "IfcElementName", "PsetName"] + [
                str(column.label) for column in list(self.table.columns.values())[5:-1]
            ] + ["GUID"]

            log_box.log(f"Headers: {headers}")

            ws.append(headers)
            for row_data in self.data_storage:
                ws.append(row_data)

            self._create_excel_table(ws, headers, len(self.data_storage))

            file_path = self._generate_export_file_path(ifc_file_path)
            wb.save(file_path)

            log_box.log(f"Data exported successfully to {file_path}")
            status_widget.log(f"[+++] Data exported successfully to {file_path}")

        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            log_box.log(error_msg)
            status_widget.log(f"[--] {error_msg}")