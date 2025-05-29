from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from _fileBrowser import BrowserWidget
from _ifcCategories import CategoryWidget
from _ifcPsets import PsetWidget
from _appname import AppNameWidget
from _systemInfo import SystemInfoWidget
from _ifcParams import ParamsWidget
from _logbox import LogBox
from _ifcInfo import IfcInfoWidget
from _footer import FooterBox
from _statusBar import StatusWidget
from _ifcStatus import IfcStatus
from _appInfo import InfoModal
import ifcopenshell
import asyncio
import time
from datetime import datetime
import sys
from pathlib import Path
from honeyThemes import nightbee, choosenbee, barbee, farbee, daybee, beethoven, cyberhive
from _themeModal import ThemeSelectorModal
from config_manager import ConfigManager


class VerticalLayoutExample(App):
    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller uses this attribute to store the temp directory
            return Path(sys._MEIPASS) / relative_path
        return Path(relative_path)

    CSS_PATH = str(resource_path("styles/nightbee.tcss"))
    THEME = "nightbee"
    BINDINGS = [
        Binding("p", "toggle_fullscreen", "Toggle Parameters Fullscreen"),
        Binding("g", "toggle_log", "Toggle log widget"),
        Binding("e", "export_xlsx", "Export selected parameters to XLSX"),
        Binding("1", "focus_file_explorer", "Focus File Explorer"),
        Binding("2", "focus_category_widget", "Focus Category Widget"),
        Binding("3", "focus_pset_widget", "Focus Pset Widget"),
        Binding("4", "focus_params_widget", "Focus Params Widget"),
        Binding("i", "toggle_info_modal", "Show Info Modal"),
        Binding("q", "quit", "Quit App"),
        Binding("t", "toggle_theme_modal", "Select Theme"),
    ]

    def get_theme_variable_defaults(self) -> dict[str, str]:
        from honeyThemes import nightbee
        return nightbee.variables

    def on_load(self) -> None:
        for theme in (nightbee, choosenbee, barbee, farbee, daybee, beethoven, cyberhive):
            self.register_theme(theme)

    def __init__(self):
        super().__init__()
        self.ifc_file = None
        self.ifc_filename = None
        self.ifc_filepath = None
        self.selected_category = None
        self.selected_pset = None
        self.is_fullscreen = False
        self.is_log = False

        self.config_manager = ConfigManager("honeycomb")
        self.saved_theme = self.config_manager.get_theme()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes='TopRow') as top_row:
                self.top_row = top_row

                app_name_widget = AppNameWidget()
                app_name_widget.classes = "TopRowColumnName"
                yield app_name_widget
                
                ifc_status_widget = IfcStatus()
                ifc_status_widget.classes = "TopRowColumnStatus"
                yield ifc_status_widget
                
                system_info_widget = SystemInfoWidget()
                system_info_widget.classes = "TopRowColumnSystem"
                yield system_info_widget

            with Horizontal(classes='MiddleRow'):
                with Vertical(classes="IfcFiles"):
                    self.file_explorer = BrowserWidget()
                    self.file_explorer.border_title = r"FileExplorer \[1]"
                    self.file_explorer.can_focus = True
                    yield self.file_explorer

                    self.ifc_info_widget = IfcInfoWidget()
                    self.ifc_info_widget.border_title = "IfcInfo"
                    self.ifc_info_widget.update_info(self.ifc_file, self.ifc_filename)
                    yield self.ifc_info_widget

                with Vertical(classes="IfcProperties"):
                    self.category_widget = CategoryWidget()
                    self.category_widget.border_title = r"IfcCategories \[2]"
                    self.category_widget.can_focus = True
                    #self.category_widget.border_subtitle = "c - Expand"
                    yield self.category_widget

                    self.pset_widget = PsetWidget()
                    self.pset_widget.border_title = r"IfcPsets \[3]"
                    self.pset_widget.can_focus = True
                    yield self.pset_widget

                self.params_widget = ParamsWidget()
                self.params_widget.border_title = r"IfcProperties \[4]"
                self.params_widget.border_subtitle = r"\[p] - Expand, \[e] - Export in xlsx"
                self.params_widget.can_focus = True
                yield self.params_widget
            
            self.status_widget= StatusWidget()
            self.status_widget.border_title = "Status"
            yield self.status_widget

            self.log_box = LogBox()
            self.log_box.border_title = "Log"
            self.log_box.display = False
            yield self.log_box

            yield FooterBox()

    async def on_mount(self) -> None:
        self.theme = self.saved_theme
        self.set_focus(self.file_explorer)
        self.log_box.log("Application started")
        self.log_box.log("Main App: Mounted")
        self.status_widget.log("")

        # Schedule a timer to update the title with the current time every second
        self.set_interval(1, self.update_top_row_title)

    def update_top_row_title(self) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        self.top_row.border_title = f"{current_time}"
        self.refresh()

    def action_toggle_info_modal(self) -> None:
        if self.is_screen_installed("info_modal"):
            self.pop_screen()
        else:
            self.push_screen(InfoModal())


    async def on_browser_widget_file_selected(self, message: BrowserWidget.FileSelected) -> None:
        self.log_box.log(f"File selected: {message.filename}")
        self.ifc_filename = message.filename
        self.selected_category = None
        self.selected_pset = None  # Clear previous selections

        # Reset the PsetWidget and ParamsWidget
        self.pset_widget.category = None
        self.pset_widget.update_view()
        self.params_widget.category = None
        self.params_widget.pset = None
        self.params_widget.update_view()

        try:
            status_widget = self.query_one(StatusWidget)
            status_widget.log("[~~~] Opening Ifc... [0.0 sec]")

            start_time = time.perf_counter()

            # Create a task to open the file in the background
            open_task = asyncio.create_task(asyncio.to_thread(ifcopenshell.open, message.filename))

            # Run a loop to update the counter while the file is being opened
            async def update_counter():
                while not open_task.done():
                    elapsed_time = time.perf_counter() - start_time
                    status_widget.log(f"[~~~] Opening Ifc... [{elapsed_time:.1f} sec]")
                    await asyncio.sleep(0.5)

            await asyncio.gather(open_task, update_counter())

            self.ifc_file = open_task.result()

            elapsed_time = time.perf_counter() - start_time
            self.log_box.log(f"IFC file loaded successfully in {elapsed_time:.2f} seconds")
            status_widget.log(f"[OK] IFC opened in {elapsed_time:.2f} seconds")

            # Update the UI with the loaded IFC data
            self.ifc_info_widget.update_info(self.ifc_file, message.filename)
            self.category_widget.update_categories(self.ifc_file, message.filename)

            # Clear the IfcStatus widget and update it with the new file name
            self.query_one(IfcStatus).update_status(ifc_name=message.filename, category=None, pset=None)

        except Exception as e:
            self.log_box.log(f"Error loading IFC file: {str(e)}")
            status_widget.log(f"[ERROR] Failed to open IFC file: {str(e)}")


    async def on_category_widget_category_selected(self, message: CategoryWidget.CategorySelected) -> None:
        self.selected_category = message.category
        self.selected_pset = None  # Reset the selected property set when a new category is selected
        self.log_box.log(f"Main App: Category selected: {self.selected_category}")

        # Reset the ParamsWidget to its initial state
        self.params_widget.pset = None
        self.params_widget.update_view()

        if self.ifc_file and self.selected_category:
            self.log_box.log(f"Main App: Updating PsetWidget with category {self.selected_category}")
            
            # Properly await the async `update_psets` function
            await self.pset_widget.update_psets(self.ifc_file, self.selected_category)
            
            # Update the IfcStatus widget with the selected category and clear the property set
            self.query_one(IfcStatus).update_status(ifc_name=self.ifc_filename, category=self.selected_category, pset=None)
        else:
            self.log_box.log(f"Main App: IFC file exists: {self.ifc_file is not None}, Category: {self.selected_category}")


    async def on_pset_widget_pset_selected(self, message: PsetWidget.PsetSelected) -> None:
        self.selected_pset = message.pset
        self.log_box.log(f"Main App: Pset selected: {self.selected_pset}")

        # Properly await the async update_params function
        await self.params_widget.update_params(self.ifc_file, self.selected_category, self.selected_pset)

        # Update the IfcStatus widget with the selected property set
        self.query_one(IfcStatus).update_status(ifc_name=self.ifc_filename, category=self.selected_category, pset=self.selected_pset)

    def action_toggle_fullscreen(self) -> None:
        ifcfiles = self.query_one(".IfcFiles")
        ifcProperties = self.query_one(".IfcProperties")
        if self.is_fullscreen:
            ifcfiles.remove_class("hidden")
            ifcProperties.remove_class("hidden")
            self.is_fullscreen = False
        else:
            ifcfiles.add_class("hidden")
            ifcProperties.add_class("hidden")
            self.is_fullscreen = True
        self.log_box.log(f"Fullscreen mode: {'On' if self.is_fullscreen else 'Off'}")

    def action_toggle_log(self) -> None:
        self.log_box.display = not self.log_box.display
        self.log_box.log(f"Log box {'shown' if self.log_box.display else 'hidden'}")

    def action_export_xlsx(self) -> None:
        self.params_widget.export_to_excel(self.ifc_filename)

    def action_focus_file_explorer(self) -> None:
        self.set_focus(self.file_explorer)
        self.log_box.log("Focused on File Explorer")

    def action_focus_category_widget(self) -> None:
        self.set_focus(self.category_widget)
        self.log_box.log("Focused on Category Widget")

    def action_focus_pset_widget(self) -> None:
        self.set_focus(self.pset_widget)
        self.log_box.log("Focused on Pset Widget")

    def action_focus_params_widget(self) -> None:
        self.set_focus(self.params_widget)
        self.log_box.log("Focused on Params Widget")

    def action_quit(self) -> None:
        self.log_box.log("Exiting application...")
        self.exit()

    def action_toggle_theme_modal(self) -> None:
        if self.is_screen_installed("theme_modal"):
            self.pop_screen()
        else:
            self.push_screen(ThemeSelectorModal())


if __name__ == "__main__":
    app = VerticalLayoutExample()
    app.run()
