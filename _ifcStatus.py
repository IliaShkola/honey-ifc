from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult


class IfcStatus(Widget):
    """Widget to display the current IFC status: file name, selected category, and Pset."""

    def __init__(self):
        super().__init__()
        self.ifc_name = None
        self.category = None
        self.pset = None
        self.status_display = None

    def compose(self) -> ComposeResult:
        self.status_display = Static(self._generate_status_text())
        yield self.status_display

    def _generate_status_text(self) -> str:
        """Generate the text to display in the IFC status widget."""
        if self.ifc_name is None:
            return ""  # Show nothing if no IFC is selected
        status = self.ifc_name
        if self.category:
            status += f" => {self.category}"
        if self.pset:
            status += f" => {self.pset}"
        return status

    def update_status(self, ifc_name: str = None, category: str = None, pset: str = None) -> None:
        self.ifc_name = ifc_name
        self.category = category
        self.pset = pset
        """Update the IFC status information and refresh the display."""
        if ifc_name is not None:
            self.ifc_name = ifc_name
        if category is not None:
            self.category = category
        if pset is not None:
            self.pset = pset

        # Update the text in the Static widget
        if self.status_display:
            self.status_display.update(self._generate_status_text())
