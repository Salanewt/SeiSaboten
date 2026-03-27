"""
The view file for item data.

TODO:
- More data should be loaded; what data an item has seems to be dictated largely by its item type,
  meaning that the UI should be able to change dynamically based on what kind of item it is.
- Ideally, we can fill a groupBox with contents based on chosen item type.
  - May need to set a limit on the number of Materials that can be created, unless we patch the
    contents of that model into the generic item table where it probably should be.

Contains:
class ItemView(BaseView)        Defines interface behaviour for the Shops tab
  setup_connections             Links different UI elements to corresponding methods
  init_after_rom                Refreshes the UI when a ROM is loaded
  setup_table                   Makes the item table functional
  show_item_stats               Populates the UI with the selected item and its details 
  update_item_field             Updates the currently selected item
  update_item_type              Updates UI when selecting a new comboBox item
  
ItemTableModel               Defines how the item table displays data
"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from .base_view import BaseView
from controllers.itemman import ItemManager

import globals

class ItemView(BaseView):
    """
    See base_view for details.
    """
    def __init__(self, main_window):
        super().__init__(main_window)
        
        self.item_model = ItemTableModel()
        self.field_mapper = {}  # Will be populated in setup_connections

        # This filter model is used for filtering table entries (i.e. search bar functionality)
        self.filter_model = QtCore.QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.item_model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(0)  # Filter on the name column (column 0)

        self.setup_table()
        self.setup_connections()

    def setup_connections(self):
        # Table connection
        self.main_window.item_tableView.selectionModel().currentRowChanged.connect(
            self.show_item_stats
        )
        
        # Search bar connection
        self.main_window.item_search_lineEdit.textChanged.connect(
            self.filter_model.setFilterFixedString
        )
        
        # Create the field mapper dictionary for line edits
        # Format: line_edit: (attribute_name, max_value) - max_value=None for string fields
        self.field_mapper = {
            self.main_window.item_name_lineEdit: ('name', None),
            self.main_window.item_description_lineEdit: ('description', None),
            self.main_window.item_id_lineEdit: ('id_', 0xFF),
            self.main_window.item_price_lineEdit: ('price', 0xFFFF),
        }
        
        # Connect all line edits to the generic update method
        for line_edit, (field, max_val) in self.field_mapper.items():
            line_edit.editingFinished.connect(
                lambda le=line_edit, f=field, m=max_val: self.update_item_field(le, f, m)
            )
        
        # Connect combo box
        self.main_window.item_type_combo.currentIndexChanged.connect(
            self.update_item_type
        )

    def init_after_rom(self):
        globals.my_itemman = ItemManager()

        # Item table handling
        self.item_model.items = globals.my_itemman.full_item_list
        self.item_model.layoutChanged.emit()

        self.main_window.item_tableView.setHorizontalHeader(self.main_window.item_tableView.horizontalHeader())
        
        # Hide the first row in the source model (index 0)
        # We need to do this after the model is populated
        self.main_window.item_tableView.setRowHidden(0, True)

        self.main_window.item_tableView.resizeColumnsToContents()
        self.main_window.item_tableView.resizeRowsToContents()

    def setup_table(self):
        """The item table displays a list of all items (sans weapons/armour) in the game."""
        # Display horizontal header
        self.main_window.item_tableView.setHorizontalHeader(self.main_window.item_tableView.horizontalHeader())
        # Row selection properties
        self.main_window.item_tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.main_window.item_tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        # Other - use filter model instead of source model
        self.main_window.item_tableView.setModel(self.filter_model)
        self.main_window.item_tableView.verticalHeader().setSectionsMovable(True)
        self.main_window.item_tableView.verticalHeader().setDragEnabled(True)
        self.main_window.item_tableView.verticalHeader().setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.main_window.item_tableView.verticalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Interactive)

    # Generic update method for line edits
    def update_item_field(self, line_edit, field, max_val):
        """Update method for any item field from line edits."""
        current_index = self.main_window.item_tableView.currentIndex()
        if not current_index.isValid():
            return
        
        # Map to source model to get the actual item
        source_index = self.filter_model.mapToSource(current_index)
        item = self.item_model.items[source_index.row()]
        text = line_edit.text()
        
        if max_val is None:  # String field (like name, description)
            setattr(item, field, text)
        else:  # Numeric field
            if text.isdigit():
                clamped = self.clamp(int(text), max_val)
                setattr(item, field, clamped)
                line_edit.setText(str(clamped))  # Update with clamped value
            else:
                # Reset to current value if invalid
                line_edit.setText(str(getattr(item, field)))
        
        # Refresh table row in source model
        self.item_model.refresh_row(source_index.row())

    # Combo box update method
    def update_item_type(self, index):
        """Real-time update when type combo changes."""
        current_index = self.main_window.item_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.item_model.items[source_index.row()].type_ = index

    # Store stats of item that was viewed and load next selected item
    def show_item_stats(self, current, previous):
        """Load the selected item's data into the UI when selection changes."""
        if current.row() >= 0:
            # Map the filtered row back to the source model row
            source_index = self.filter_model.mapToSource(current)
            item = self.item_model.items[source_index.row()]
            self.main_window.item_name_lineEdit.setText(item.name)
            self.main_window.item_description_lineEdit.setText(item.description)
            self.main_window.item_id_lineEdit.setText(str(item.id_))
            self.main_window.item_price_lineEdit.setText(str(item.price))
            self.main_window.item_type_combo.setCurrentIndex(item.type_)


# Defines how item data is displayed in its table
class ItemTableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, items=None, **kwargs):
        super(ItemTableModel, self).__init__(*args, **kwargs)
        self.items = items or []
        self.header = ['Name']
    
    def refresh_row(self, row):
        """Refresh a specific row in the table to reflect data changes."""
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount(None) - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.items[index.row()].name
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        return True

    def rowCount(self, index):
        return len(self.items)
    
    def columnCount(self, index):
        return len(self.header)
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return col 
        return None
    
    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable