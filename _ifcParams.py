import os
import asyncio
import time
from typing import List, Tuple, Optional

from textual.widgets import DataTable, Label
from textual.widget import Widget
from textual.app import ComposeResult
from textual.binding import Binding
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import ifcopenshell

from _logbox import LogBox
from _statusBar import StatusWidget


class ExtractParametersHelper:
    """Helper class for robust parameter extraction"""

    @staticmethod
    def _get_element_pset_robust(element, pset_name, ifc_file):
        """Robust property set retrieval with multiple fallback methods"""

        # Method 1: Standard approach via ifcopenshell.util.element
        try:
            pset_data = ifcopenshell.util.element.get_pset(element, pset_name)
            if pset_data:
                return pset_data
        except Exception as e:
            print(f"Method 1 failed for element {element.id()}: {e}")

        # Method 2: Direct search through element relationships
        try:
            if hasattr(element, 'IsDefinedBy') and element.IsDefinedBy:
                for rel in element.IsDefinedBy:
                    if rel.is_a('IfcRelDefinesByProperties'):
                        prop_def = rel.RelatingPropertyDefinition
                        if (prop_def.is_a('IfcPropertySet') or prop_def.is_a('IfcElementQuantity')):
                            if prop_def.Name == pset_name:
                                return ExtractParametersHelper._extract_properties_from_definition(prop_def)
        except Exception as e:
            print(f"Method 2 failed for element {element.id()}: {e}")

        # Method 3: Search through all relationships in file
        try:
            for rel in ifc_file.by_type('IfcRelDefinesByProperties'):
                if element in rel.RelatedObjects:
                    prop_def = rel.RelatingPropertyDefinition
                    if (prop_def.is_a('IfcPropertySet') or prop_def.is_a('IfcElementQuantity')):
                        if prop_def.Name == pset_name:
                            return ExtractParametersHelper._extract_properties_from_definition(prop_def)
        except Exception as e:
            print(f"Method 3 failed for element {element.id()}: {e}")

        # Method 4: Alternative search via get_psets and filtering
        try:
            all_psets = ifcopenshell.util.element.get_psets(element)
            if pset_name in all_psets:
                pset_data = all_psets[pset_name]
                if isinstance(pset_data, dict):
                    return pset_data
        except Exception as e:
            print(f"Method 4 failed for element {element.id()}: {e}")

        return {}

    @staticmethod
    def _extract_properties_from_definition(prop_def):
        """Property extraction from IfcPropertySet or IfcElementQuantity"""
        properties = {}

        try:
            if prop_def.is_a('IfcPropertySet'):
                for prop in prop_def.HasProperties:
                    if prop.is_a('IfcPropertySingleValue'):
                        name = prop.Name
                        value = prop.NominalValue.wrappedValue if prop.NominalValue else None
                        properties[name] = value
                    elif prop.is_a('IfcPropertyEnumeratedValue'):
                        name = prop.Name
                        values = [v.wrappedValue for v in prop.EnumerationValues] if prop.EnumerationValues else []
                        properties[name] = ', '.join(map(str, values)) if values else None
                    # Add other property types as needed

            elif prop_def.is_a('IfcElementQuantity'):
                for quantity in prop_def.Quantities:
                    name = quantity.Name
                    if hasattr(quantity, 'LengthValue'):
                        properties[name] = quantity.LengthValue
                    elif hasattr(quantity, 'AreaValue'):
                        properties[name] = quantity.AreaValue
                    elif hasattr(quantity, 'VolumeValue'):
                        properties[name] = quantity.VolumeValue
                    elif hasattr(quantity, 'CountValue'):
                        properties[name] = quantity.CountValue
                    elif hasattr(quantity, 'WeightValue'):
                        properties[name] = quantity.WeightValue
                    elif hasattr(quantity, 'TimeValue'):
                        properties[name] = quantity.TimeValue

        except Exception as e:
            print(f"Error extracting properties from {prop_def.Name}: {e}")

        return properties

    @staticmethod
    def _safe_get_attribute(element, attribute_name, default_value="Empty"):
        """Safe retrieval of element attribute"""
        try:
            value = getattr(element, attribute_name, None)
            return value if value is not None else default_value
        except Exception:
            return default_value

class IFCDataProcessor:
    """Helper class for processing IFC data"""

    @staticmethod
    def extract_parameters(ifc_file, category: str, pset: str) -> Tuple[List[str], List[List]]:
        """Extracts parameters from an IFC file with robust fallback methods for PyInstaller"""
        try:
            elements = ifc_file.by_type(category)

            if not elements:
                return [], []

            # Step 1: Collect all unique parameters from all elements
            all_param_names = set()
            elements_with_psets = []

            for element in elements:
                element_pset = ExtractParametersHelper._get_element_pset_robust(element, pset, ifc_file)

                if element_pset:
                    # Add all found parameters to the general set
                    all_param_names.update(element_pset.keys())
                    elements_with_psets.append((element, element_pset))
                else:
                    # Even if pset is not found, add the element with an empty pset
                    elements_with_psets.append((element, {}))

            if not all_param_names:
                return [], []

            # Convert to a sorted list for stable column order
            param_names = sorted(list(all_param_names))
            rows = []

            # Step 2: Fill in data for all elements with all found parameters
            for index, (element, element_pset) in enumerate(elements_with_psets, start=1):
                try:
                    element_name = ExtractParametersHelper._safe_get_attribute(element, 'Name', "Unnamed")
                    ifc_category = element.is_a()  # Type of IFC element
                    predefined_type = ExtractParametersHelper._safe_get_attribute(element, 'PredefinedType', "Empty")
                    element_guid = ExtractParametersHelper._safe_get_attribute(element, 'GlobalId', "Empty")

                    # Form the row: No, IfcCategory, PredefinedType, IfcElementName, PsetName, ...parameters..., GUID
                    row_data = [index, ifc_category, predefined_type, element_name, pset]

                    # For each unique parameter, check its presence in the current element
                    for param in param_names:
                        value = element_pset.get(param) if element_pset else None
                        formatted_value = "Empty" if value in (None, "") else str(value)
                        row_data.append(formatted_value)

                    # Add GUID at the end
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
    """Optimized widget for displaying IFC parameters while preserving the interface"""

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
        """Updates the visibility of DataTable and Label (original interface preserved)"""
        if self.category and self.pset:
            self.message_label.display = False
            self.table.display = True
        else:
            self.message_label.display = True
            self.table.display = False

    def _move_cursor_safely(self, direction: int) -> None:
        """Safe cursor movement"""
        if self.table.row_count > 0:
            current_row = self.table.cursor_row
            new_row = (current_row + direction) % self.table.row_count
            self.table.move_cursor(row=new_row)

    def action_move_down(self) -> None:
        """Move cursor down (optimized)"""
        self._move_cursor_safely(1)

    def action_move_up(self) -> None:
        """Move cursor up (optimized)"""
        self._move_cursor_safely(-1)

    def on_focus(self) -> None:
        self.add_class("focus")
        self.table.focus()

    def on_blur(self):
        self.remove_class("focus")

    async def update_params(self, ifc_file, category, pset) -> None:
        """Updates parameters (optimized, but interface preserved)"""
        self.category = category
        self.pset = pset

        if not category or not pset:
            return

        log_box = self.app.query_one(LogBox)
        status_widget = self.app.query_one(StatusWidget)

        log_box.log(f"Params Widget: Parameters updating for {self.category} with {self.pset}...")

        # Clear previous data
        self.table.clear(columns=True)
        self.data_storage.clear()
        start_time = time.perf_counter()

        try:
            # Start processing in a background thread
            params_task = asyncio.create_task(
                asyncio.to_thread(IFCDataProcessor.extract_parameters, ifc_file, category, pset)
            )

            # Update timer
            await self._update_timer_while_processing(params_task, start_time, status_widget, category)

            elapsed_time = time.perf_counter() - start_time
            param_names, rows = params_task.result()

            if param_names and rows:
                # Add columns: No, IfcCategory, PredefinedType, IfcElementName, PsetName, ...parameters..., GUID
                self.table.add_columns("No", "IfcCategory", "PredefinedType", "IfcElementName", "PsetName",
                                       *param_names, "GUID")

                for row_data in rows:
                    self.table.add_row(*row_data)
                    self.data_storage.append(row_data)

                log_box.log(f"Params Widget: Added {len(rows)} rows with {len(param_names)} parameters")
                status_widget.log(f"[+++] Parameters updated for {category} with {pset} in {elapsed_time:.2f} seconds")
            else:
                status_widget.log(f"[---] No parameters to update for {category} with {pset}")

            # Update visibility after loading data
            self.update_view()
            log_box.log(
                f"Params Widget: Completed update for {self.category} with {self.pset} in {elapsed_time:.2f} seconds")

        except Exception as e:
            log_box.log(f"Error fetching parameters: {str(e)}")
            status_widget.log(f"[--] Error: {str(e)}")

    async def _update_timer_while_processing(self, task, start_time: float, status_widget, category: str) -> None:
        """Update timer while processing (moved to a separate method)"""
        while not task.done():
            elapsed_time = time.perf_counter() - start_time
            status_widget.log(f"[~~~] Updating parameters for {category}... [{elapsed_time:.1f} sec]")
            await asyncio.sleep(0.5)

    def _generate_export_file_path(self, ifc_file_path: str) -> str:
        """Generates a path for export (moved to a separate method)"""
        folder_path = os.path.dirname(ifc_file_path)
        ifc_base_name = os.path.splitext(os.path.basename(ifc_file_path))[0]

        # Safe names for the file system
        category_safe = self.category.replace(" ", "_").replace("/", "_")
        pset_safe = self.pset.replace(" ", "_").replace("/", "_")

        file_name = f"{ifc_base_name}_{category_safe}_{pset_safe}.xlsx"
        return os.path.join(folder_path, file_name)

    def _create_excel_table(self, ws, headers: List[str], data_count: int) -> None:
        """Creates an Excel table with formatting (moved to a separate method)"""
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
        """Export to Excel (optimized, interface preserved)"""
        log_box = self.app.query_one(LogBox)
        status_widget = self.app.query_one(StatusWidget)

        if not self.data_storage:
            error_msg = "No data to export"
            log_box.log(f"[--] {error_msg}")
            status_widget.log(f"[--] Export failed: {error_msg}")
            return

        try:
            # Creating workbook and worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = "IFC Data Export"

            # Forming headers for Excel
            headers = ["No", "IfcCategory", "PredefinedType", "IfcElementName", "PsetName"] + [
                str(column.label) for column in list(self.table.columns.values())[5:-1]
                # Parameters (excluding the first 5 and the last one)
            ] + ["GUID"]

            log_box.log(f"Headers: {headers}")

            # Writing data
            ws.append(headers)
            for row_data in self.data_storage:
                ws.append(row_data)

            # Creating a table with formatting
            self._create_excel_table(ws, headers, len(self.data_storage))

            # Saving the file
            file_path = self._generate_export_file_path(ifc_file_path)
            wb.save(file_path)

            log_box.log(f"Data exported successfully to {file_path}")
            status_widget.log(f"[+++] Data exported successfully to {file_path}")

        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            log_box.log(error_msg)
            status_widget.log(f"[--] {error_msg}")

