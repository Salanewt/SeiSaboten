"""
The view file for shop data/UI stuff.

TODO:
- It would be nice if more of the selected item's data could be loaded into the UI and edited.

Contains:
class ShopView(BaseView)        Defines interface behaviour for the Shops tab
  setup_connections             Links different UI elements to corresponding methods
  init_after_rom                Refreshes the UI when a ROM is loaded
  setup_shop_table              Makes the shop table functional
  setup_shop_stock_table        Makes the shop stock table functional
  update_item_field             Updates the currently selected item/weapon/armour's fields
  process_shop_inventory        Refreshes inventory list, calling following method to do so
  show_shop_inventory           Fills the shop_stock_tableView with the selected shop's items
  process_item_details          Refreshes item details, calling following method to do so
  show_current_item             Populates the UI with the selected stock item and its details             
  link_item_combo               Updates the items in the comboBox based on selected stock slot
  refresh_item_selection        Updates the item and shop's stock (and also the view)

ShopTableModel                  Defines how the shop table displays data
ShopStockTableModel             Defines how the shop stock table displays data
"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from .base_view import BaseView
from controllers.shopman import ShopManager

import globals

class ShopView(BaseView):
    """
    See base_view for details.
    """
    def __init__(self, main_window):
        super().__init__(main_window)
        
        self.shop_model = ShopTableModel()
        self.shop_stock_model = ShopStockTableModel()
        self.field_mapper = {}  # For line edit updates

        # This filter model is used for filtering table entries (i.e. search bar functionality)
        self.stock_filter_model = QtCore.QSortFilterProxyModel()
        self.stock_filter_model.setSourceModel(self.shop_stock_model)
        self.stock_filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.stock_filter_model.setFilterKeyColumn(0)  # Filter on the item name column

        self.current_slot_index = -1

        self.setup_shop_table()
        self.setup_shop_stock_table()
        self.setup_connections()

    def setup_connections(self):
        # Table connections
        self.main_window.shop_tableView.selectionModel().currentRowChanged.connect(
            self.process_shop_inventory
        )
        self.main_window.shop_stock_tableView.selectionModel().currentRowChanged.connect(
            self.process_item_details
        )
        self.main_window.shop_comboBox.currentIndexChanged.connect(
            self.refresh_item_selection
        )

        # Search bar connection - only for stock
        self.main_window.shop_stock_search_lineEdit.textChanged.connect(
            self.stock_filter_model.setFilterFixedString
        )

        # Create the field mapper dictionary for line edits
        # Format: line_edit: (attribute_name, max_value) - max_value=None for string fields
        self.field_mapper = {
            self.main_window.shop_stock_name_lineEdit: ('name', None),
            self.main_window.shop_stock_description_lineEdit: ('description', None),
            self.main_window.shop_stock_price_lineEdit: ('price', 0xFFFF),
        }
        
        # Connect all line edits to the generic update method
        for line_edit, (field, max_val) in self.field_mapper.items():
            line_edit.editingFinished.connect(
                lambda le=line_edit, f=field, m=max_val: self.update_item_field(le, f, m)
            )

    def init_after_rom(self):
        globals.my_shopman = ShopManager()

        self.shop_model.shops = globals.my_shopman.full_shop_list
        self.shop_model.layoutChanged.emit()

        self.main_window.shop_tableView.setHorizontalHeader(self.main_window.shop_tableView.horizontalHeader())

        self.main_window.shop_tableView.resizeColumnsToContents()
        self.main_window.shop_tableView.resizeRowsToContents()

    def setup_shop_table(self):
        """The shop table displays the list of shops by index number."""
        # Hide index column
        self.main_window.shop_tableView.verticalHeader().setVisible(False)

        # Display horizontal header
        self.main_window.shop_tableView.setHorizontalHeader(self.main_window.shop_tableView.horizontalHeader())

        # Row selection properties
        self.main_window.shop_tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.main_window.shop_tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        # Other - use source model directly (no filter)
        self.main_window.shop_tableView.setModel(self.shop_model)
        self.main_window.shop_tableView.verticalHeader().setSectionsMovable(True)
        self.main_window.shop_tableView.verticalHeader().setDragEnabled(True)
        self.main_window.shop_tableView.verticalHeader().setDragDropMode(
            QtWidgets.QAbstractItemView.DragDropMode.InternalMove
            )
        self.main_window.shop_tableView.verticalHeader().setSectionResizeMode(
            3, 
            QtWidgets.QHeaderView.ResizeMode.Interactive
            )

    def setup_shop_stock_table(self):
        """
        The shop stock table displays the various items available for sale at a given store, 
        including empty stock slots.
        """
        # Display horizontal header
        self.main_window.shop_stock_tableView.setHorizontalHeader(
            self.main_window.shop_stock_tableView.horizontalHeader()
            )

        # Row selection properties
        self.main_window.shop_stock_tableView.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )
        self.main_window.shop_stock_tableView.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )

        # Other - use filter model
        self.main_window.shop_stock_tableView.setModel(self.stock_filter_model)
        self.main_window.shop_stock_tableView.verticalHeader().setSectionsMovable(True)
        self.main_window.shop_stock_tableView.verticalHeader().setDragEnabled(True)
        self.main_window.shop_stock_tableView.verticalHeader().setDragDropMode(
            QtWidgets.QAbstractItemView.DragDropMode.InternalMove
            )
        self.main_window.shop_stock_tableView.verticalHeader().setSectionResizeMode(
            3, 
            QtWidgets.QHeaderView.ResizeMode.Interactive)

    # Generic update method for line edits
    def update_item_field(self, line_edit, field, max_val):
        """Generic update method for any item field from line edits."""
        if not self.shop_stock_model.current_shop or self.current_slot_index < 0:
            return
        
        slot_idx = self.current_slot_index
        stock_id = self.shop_stock_model.current_shop.shop_stock[slot_idx]
        
        # Get the appropriate item list based on slot index
        if 20 <= slot_idx < 40:  # Weapons
            items = globals.my_weaponman.full_equip_list
        elif 40 <= slot_idx < 60:  # Armour
            items = globals.my_armourman.full_equip_list
        else:  # Items and Accessories
            items = globals.my_itemman.full_item_list
        
        if 0 <= stock_id < len(items):
            item = items[stock_id]
            text = line_edit.text()
            
            if max_val is None:  # String field (name, description)
                setattr(item, field, text)
                if field == 'name':
                    self.main_window.shop_comboBox.setItemText(stock_id, text)
            else:  # Numeric field (price)
                if text.isdigit():
                    clamped = self.clamp(int(text), max_val)
                    setattr(item, field, clamped)
                    line_edit.setText(str(clamped))
                else:
                    # Reset to current value if invalid
                    line_edit.setText(str(getattr(item, field)))
        
            # Refresh table row in source model
            self.shop_stock_model.refresh_row(slot_idx)

    # Store the stock of shop that was viewed and load next selected shop
    def process_shop_inventory(self, current, previous):
        """Functionally loads/refreshes the tab based on which shop has been selected."""
        if current.row() >= 0:
            self.show_shop_inventory(self.shop_model.shops[current.row()])

    def show_shop_inventory(self, shop):
        """Display the stock of the selected shop."""
        self.shop_stock_model.set_shop(shop)
        
        # Update the filter model to use the new source model
        self.stock_filter_model.setSourceModel(self.shop_stock_model)
        
        self.main_window.shop_stock_tableView.resizeRowsToContents()
        self.current_slot_index = -1  # Reset current slot when switching shops

    def process_item_details(self, current, previous):
        """Functionally loads/refreshes the tab based on which inventory item has been selected."""       
        if current.row() >= 0:
            # Map filtered index to source
            source_index = self.stock_filter_model.mapToSource(current)
            self.show_current_item(source_index.row())
            self.current_slot_index = source_index.row()        

    def show_current_item(self, slot_idx):
        """Display details for the item at the given slot index in the current shop."""
        if not self.shop_stock_model.current_shop:
            return
        
        # Get the stock ID for this slot
        stock_id = self.shop_stock_model.current_shop.shop_stock[slot_idx]
        
        # Determine which item list to use based on slot index
        items = None   
        if 20 <= slot_idx < 40:  # Weapons (slots 20-39)
            items = globals.my_weaponman.full_equip_list 
        elif 40 <= slot_idx < 60:  # Armour (slots 40-59)
            items = globals.my_armourman.full_equip_list   
        else:  # Items and Accessories (slots 0-19, 60-79)
            items = globals.my_itemman.full_item_list
        
        # Block signals while populating the combo box
        self.main_window.shop_comboBox.blockSignals(True)
        
        # Clear the combo box before adding new items
        self.main_window.shop_comboBox.clear()
        
        # Populate the combo box
        self.link_item_combo(items, stock_id)
        
        # Unblock signals
        self.main_window.shop_comboBox.blockSignals(False)
        
        # Update info box fields; fill boxes based what item ID the chosen inventory slot has
        if 1 <= stock_id < len(items):
            selected_item = items[stock_id]
            self.main_window.shop_stock_name_lineEdit.setText(selected_item.name)
            self.main_window.shop_stock_description_lineEdit.setText(selected_item.description)
            self.main_window.shop_stock_price_lineEdit.setText(str(selected_item.price))
        else:
            # Invalid stock_id; if slot == 0 or is somehow greater than the slot limit
            self.main_window.shop_stock_name_lineEdit.setText("")
            self.main_window.shop_stock_description_lineEdit.setText("")
            self.main_window.shop_stock_price_lineEdit.setText("")

    def link_item_combo(self, items, stock_id):
        """Helper function: Sets comboBox items depending on the type of item chosen."""
        # Add "None" as the first item
        self.main_window.shop_comboBox.addItem("None")
        
        # Add all items (starting from index 1 since index 0 is "None")
        for idx, stock in enumerate(items):
            if idx > 0:  # Skip index 0 since we already added "None"
                self.main_window.shop_comboBox.addItem(stock.name)
        
        # Set the current index based on stock_id
        # stock_id 0 = "None", stock_id 1 = first item, etc.
        if 0 <= stock_id < len(items):
            self.main_window.shop_comboBox.setCurrentIndex(stock_id)
        else:
            self.main_window.shop_comboBox.setCurrentIndex(0)  # Default to "None" for invalid IDs

    def refresh_item_selection(self, index):
        """
        Updates the chosen item's details within data entry fields when combo box selection changes.
        THIS IS WHERE THE SHOP STOCK ACTUALLY GETS UPDATED.
        """
        if not self.shop_stock_model.current_shop:
            return
        
        # Get the current slot index from the selected row in the stock table
        current_index = self.main_window.shop_stock_tableView.currentIndex()
        if not current_index.isValid():
            return
        
        # Map filtered index to source
        source_index = self.stock_filter_model.mapToSource(current_index)
        slot_idx = source_index.row()
        
        # Get the current shop
        shop_index = self.main_window.shop_tableView.currentIndex()
        if not shop_index.isValid():
            return
        
        shop = self.shop_model.shops[shop_index.row()]
        
        # Update the shop stock with the new item ID
        if 0 <= slot_idx < len(shop.shop_stock):
            shop.shop_stock[slot_idx] = index
        
        # Determine which item list to use based on slot index                   
        if 20 <= slot_idx < 40:  # Weapons
            items = globals.my_weaponman.full_equip_list
        elif 40 <= slot_idx < 60:  # Armour
            items = globals.my_armourman.full_equip_list
        else:  # Items, Accessories
            items = globals.my_itemman.full_item_list
        
        # Update the display fields
        if 0 <= index < len(items):
            if index == 0:  # "None" selected
                self.main_window.shop_stock_name_lineEdit.setText("")
                self.main_window.shop_stock_description_lineEdit.setText("")
                self.main_window.shop_stock_price_lineEdit.setText("")
            else:
                selected_item = items[index]
                self.main_window.shop_stock_name_lineEdit.setText(selected_item.name)
                self.main_window.shop_stock_description_lineEdit.setText(selected_item.description)
                self.main_window.shop_stock_price_lineEdit.setText(str(selected_item.price))
        
        # Force the stock table to refresh and show the new item
        self.shop_stock_model.refresh_row(slot_idx)
        
        # Also force the specific cell in the filtered view to update
        filter_index = self.stock_filter_model.mapFromSource(source_index)
        if filter_index.isValid():
            self.stock_filter_model.dataChanged.emit(filter_index, filter_index, [Qt.ItemDataRole.DisplayRole])


# Populates the shop_tableView widget with a list of the game's shops
class ShopTableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, shops=None, **kwargs):
        super(ShopTableModel, self).__init__(*args, **kwargs)
        self.shops = shops or []
        self.header = ['Shop #']
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return str(index.row())  # Convert to string for filtering
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        return True

    def rowCount(self, index):
        return len(self.shops)
    
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


# Populates the shop_stock_tableView widget with the actual things the selected shop sells; should produce a table of 
# item names and their corresponding prices 
class ShopStockTableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, shops=None, **kwargs):
        super(ShopStockTableModel, self).__init__(*args, **kwargs)
        self.shops = shops or []
        self.current_shop = None
        self.header = ['Name', 'Price']
    
    def set_shop (self, shop):
        """Resets the model to populate the table using the currently selected shop."""
        self.beginResetModel()
        self.current_shop = shop
        self.endResetModel()

    def refresh_row(self, row):
        """Refresh a specific row in the table."""
        if not self.current_shop:
            return
        
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount(None) - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def get_item_info(self, shop_slot, stock_id):
        """Get item name and price based on slot index and stock ID."""       
        # Slot ranges determine item type            
        if 20 <= shop_slot < 40:  # Weapons (slots 20-39)
            weapon = globals.my_weaponman.get_equip(stock_id)
            if weapon:
                return (weapon.name, str(weapon.price))
            
        elif 40 <= shop_slot < 60:  # Armour (slots 40-59)
            armour = globals.my_armourman.get_equip(stock_id)
            if armour:
                return (armour.name, str(armour.price))
            
        else:  # Items, Accessories (slots 0-19, 60-79)
            item = globals.my_itemman.get_item(stock_id)
            if item:
                return (item.name, str(item.price))
        
        return ("", "")  # Return empty strings if no item found
    
    def data(self, index, role):
        if not self.current_shop or not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            item = index.row()
            stock_id = self.current_shop.shop_stock[item]
            name, price = self.get_item_info(item, stock_id)
           
            if index.column() == 0:
                return name
            elif index.column() == 1:
                return price
        
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        return True

    def rowCount(self, index):
        if self.current_shop:
            return len(self.current_shop.shop_stock)
        return 0
    
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