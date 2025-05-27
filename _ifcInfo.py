from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
import os


class IfcInfoWidget(Widget):
    """Widget to display general info about the IFC model."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name_label = Static("Name: -")
        self.size_label = Static("File Size: -")
        self.version_label = Static("IFC Version: -")
        self.elements_label = Static("Number of Elements: -")

    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        # Always display all labels, even if no data is loaded
        yield self.name_label
        yield self.size_label
        yield self.version_label
        yield self.elements_label

    def update_info(self, ifc_file, filename):
        """Update the IFC info widget with data from the opened file."""
        ifc_name = os.path.basename(filename) if filename else "-"
        ifc_size = f"{os.path.getsize(filename) / (1024 * 1024):.2f} MB" if filename else "-"
        ifc_version = ifc_file.schema if ifc_file else "-"
        num_elements = len(ifc_file.by_type("IfcProduct")) if ifc_file else "-"

        # Update labels with detailed information
        self.name_label.update(f"Name: {ifc_name}")
        self.size_label.update(f"File Size: {ifc_size}")
        self.version_label.update(f"IFC Version: {ifc_version}")
        self.elements_label.update(f"Number of Elements: {num_elements}")
