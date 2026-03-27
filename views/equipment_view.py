"""
The view file for weapons and armour. Contains both the super classes for equipment as well as the
derived classes, since both data structs are defined and handled extremely similarly to one another.

Contains:
class EquipmentView(BaseView)   Defines interface behaviour for the Shops tab
  setup_connections             Links different UI elements to corresponding methods
  init_after_rom                Refreshes the UI when a ROM is loaded
  setup_table                   Makes the equip table functional
  update_equip_field            Updates the currently selected equipment's fields
  store_current_data            
  show_equip_stats              Populates the UI with the selected item and its details 
  update_equip_type             Updates UI when selecting a new comboBox item
  update_equip_material         Updates UI when selecting a new comboBox item

class WeaponView(EquipmentView)
class ArmourView(EquipmentView)

EquipTableModel                 Defines how the equipment table displays data

WeaponTableModel(EquipTableModel)
ArmourTableModel(EquipTableModel)

"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from .base_view import BaseView
from controllers.equipmentman import WeaponManager, ArmourManager

import globals

# --- Equipment Views --- #
class EquipmentView(BaseView):
    """
    This is the super class from which the Weapon and Armour views are derived.
    """
    def __init__(self, main_window):
        """Initialise the view/UI."""
        super().__init__(main_window)

        # UI widgets and data model/management
        self.manager_class = None
        self.model = None
        self.equip_model = None
        self.filter_model = None
        self.search_lineEdit = None  # Will be set in subclasses
        self.field_mapper = {}  # Will be populated in setup_connections

        # Interactable UI elements
        self.equip_tableView = None
        self.name_lineEdit = None
        self.description_lineEdit = None
        self.price_lineEdit = None
        self.type_combo = None
        self.temper_lineEdit = None
        self.material_combo = None
        self.var1_lineEdit = None
        self.var2_lineEdit = None
        self.var3_lineEdit = None
        self.element_lineEdit = None
        # self.unk_lineEdit = None

    def setup_connections(self):
        """Connect to the actual equipment controller."""
        # Real-time connection for the table
        if self.equip_tableView:
            self.equip_tableView.selectionModel().currentRowChanged.connect(
                self.show_equip_stats
            )
        
        # Search bar connection
        if self.search_lineEdit:
            self.search_lineEdit.textChanged.connect(
                self.filter_model.setFilterFixedString
            )

        # Create the field mapper dictionary for line edits
        # Format: line_edit: (attribute_name, max_value) - max_value=None for string fields
        self.field_mapper = {
            self.name_lineEdit: ('name', None),
            self.description_lineEdit: ('description', None),
            self.price_lineEdit: ('price', 0xFFFF),
            self.temper_lineEdit: ('temper', 0x7F),
            self.var1_lineEdit: ('equipment_var1', 0x7F),
            self.var2_lineEdit: ('equipment_var2', 0x7F),
            self.var3_lineEdit: ('equipment_var3', 0x7F),
            self.element_lineEdit: ('element_strength', 0x7F),
        }
        
        # Connect all line edits to the generic update method
        for line_edit, (field, max_val) in self.field_mapper.items():
            line_edit.editingFinished.connect(
                lambda le=line_edit, f=field, m=max_val: self.update_equip_field(le, f, m)
            )

        # Combo box connections (still need individual methods since they pass index)
        self.type_combo.currentIndexChanged.connect(
            self.update_equip_type
        )
        self.material_combo.currentIndexChanged.connect(
            self.update_equip_material
        )

    # Equip table handling
    def init_after_rom(self):
        """ Do everything here only after loading a ROM."""
        self.manager = self.manager_class()

        self.equip_model.equipment = self.manager.full_equip_list
        self.equip_model.layoutChanged.emit()

        self.equip_tableView.setHorizontalHeader(self.equip_tableView.horizontalHeader())
        
        # Hide the first row in the source model (index 0)
        self.equip_tableView.setRowHidden(0, True)

        self.equip_tableView.resizeColumnsToContents()
        self.equip_tableView.resizeRowsToContents()
    
    def setup_table(self):
        """Sets up the table that lists all members of the chosen equipment class."""
        # Display horizontal header
        self.equip_tableView.setHorizontalHeader(self.equip_tableView.horizontalHeader())
        # Row selection properties
        self.equip_tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.equip_tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        # Other - use filter model instead of source model
        self.equip_tableView.setModel(self.filter_model)
        self.equip_tableView.verticalHeader().setSectionsMovable(True)
        self.equip_tableView.verticalHeader().setDragEnabled(True)
        self.equip_tableView.verticalHeader().setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.equip_tableView.verticalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Interactive)

    # Generic update method for line edits
    def update_equip_field(self, line_edit, field, max_val):
        """Generic update method for any equipment field from line edits."""
        current_index = self.equip_tableView.currentIndex()
        if not current_index.isValid():
            return
        
        # Map to source model to get the actual equipment
        source_index = self.filter_model.mapToSource(current_index)
        equip = self.equip_model.equipment[source_index.row()]
        text = line_edit.text()
        
        if max_val is None:  # String field (like name, description)
            setattr(equip, field, text)
        else:  # Numeric field
            if text.isdigit():
                clamped = self.clamp(int(text), max_val)
                setattr(equip, field, clamped)
                line_edit.setText(str(clamped))  # Update with clamped value
            else:
                # Reset to current value if invalid
                line_edit.setText(str(getattr(equip, field)))
        
        # Refresh table row in source model
        self.equip_model.refresh_row(source_index.row())

    def store_current_data(self, current, previous):
        """Enabled storing/updating data."""
        current_index = self.equip_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.store_equip_stats(self.equip_model.equipment[source_index.row()])

    def show_equip_stats(self, current, previous):
        """
        Store stats of equipment to the currently selected row, as well as storing the stats of the 
        previously viewed object before it is lost.
        """
        if current.row() >= 0:
            # Map the filtered row back to the source model row
            source_index = self.filter_model.mapToSource(current)
            equip = self.equip_model.equipment[source_index.row()]
            # Info
            self.name_lineEdit.setText(equip.name)
            self.description_lineEdit.setText(equip.description)
            self.price_lineEdit.setText(str(equip.price))
            self.type_combo.setCurrentIndex(equip.type_)
            # Forge
            self.temper_lineEdit.setText(str(equip.temper))
            self.material_combo.setCurrentIndex(equip.material)
            # Stats
            self.var1_lineEdit.setText(str(equip.equipment_var1))
            self.var2_lineEdit.setText(str(equip.equipment_var2))
            self.var3_lineEdit.setText(str(equip.equipment_var3))
            self.element_lineEdit.setText(str(equip.element_strength))
            # self.unk_lineEdit.setText(str(equip.equipment_var_unknown))

    # --- Update Methods --- #
    def update_equip_type(self, index):
        """Real-time update when type combo changes."""
        current_index = self.equip_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.equip_model.equipment[source_index.row()].type_ = index

    def update_equip_material(self, index):
        """Real-time update when material combo changes."""
        current_index = self.equip_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.equip_model.equipment[source_index.row()].material = index


class WeaponView(EquipmentView):
    """
    The weapon-specific version of the EquipmentView class. Its methods have the same functionality 
    as its super class, just with explicit instance assignments so that the code contained in the 
    super class can be shared.
    """
    def __init__(self, main_window):
        super().__init__(main_window)

        # UI widgets and data model/management
        self.equip_model = WeaponTableModel()
        self.manager_class = WeaponManager
        
        # This filter model is used for filtering table entries (i.e. search bar functionality)
        self.filter_model = QtCore.QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.equip_model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(0)  # Filter on the name column (column 0)
        
        # Interactable UI elements
        self.equip_tableView = main_window.weapon_tableView
        self.search_lineEdit = main_window.weapon_search_lineEdit
        
        self.name_lineEdit = main_window.weapon_name_lineEdit
        self.description_lineEdit = main_window.weapon_description_lineEdit
        self.price_lineEdit = main_window.weapon_price_lineEdit
        self.type_combo = main_window.weapon_type_combo
        self.temper_lineEdit = main_window.weapon_temper_lineEdit
        self.material_combo = main_window.weapon_material_combo
        self.var1_lineEdit = main_window.weapon_power_lineEdit
        self.var2_lineEdit = main_window.weapon_dodge_lineEdit
        self.var3_lineEdit = main_window.weapon_hit_lineEdit
        self.element_lineEdit = main_window.weapon_ele_lineEdit
        # self.unk_lineEdit = main_window.weapon_name_lineEdit

        # Table, connection
        self.setup_table()
        self.setup_connections()

    # Weapon table handling
    def init_after_rom(self):
        super().init_after_rom()
        globals.my_weaponman = self.manager


class ArmourView(EquipmentView):
    """
    The armour-specific version of the EquipmentView class. Its methods have the same functionality 
    as its super class, just with explicit instance assignments so that the code contained in the 
    super class can be shared.   
    """
    def __init__(self, main_window):
        super().__init__(main_window)

        # UI widgets and data model/management
        self.equip_model = ArmourTableModel()
        self.manager_class = ArmourManager
        
        # This filter model is used for filtering table entries (i.e. search bar functionality)
        self.filter_model = QtCore.QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.equip_model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(0)  # Filter on the name column (column 0)
        
        # Interactable UI elements
        self.equip_tableView = main_window.armour_tableView
        self.search_lineEdit = main_window.armour_search_lineEdit

        self.name_lineEdit = main_window.armour_name_lineEdit
        self.description_lineEdit = main_window.armour_description_lineEdit
        self.price_lineEdit = main_window.armour_price_lineEdit
        self.type_combo = main_window.armour_type_combo
        self.temper_lineEdit = main_window.armour_temper_lineEdit
        self.material_combo = main_window.armour_material_combo
        self.var1_lineEdit = main_window.armour_slash_lineEdit
        self.var2_lineEdit = main_window.armour_crush_lineEdit
        self.var3_lineEdit = main_window.armour_stab_lineEdit
        self.element_lineEdit = main_window.armour_ele_lineEdit
        # self.unk_lineEdit = main_window.armour_name_lineEdit

        # Table, connection
        self.setup_table()
        self.setup_connections()

    # Armour table handling
    def init_after_rom(self):
        super().init_after_rom()
        globals.my_armourman = self.manager
        

# --- Table Models --- #
class EquipTableModel(QtCore.QAbstractTableModel):
    """
    This defines how this specific variant of the QAnstractTableModel UI element/widget will behave. 
    Shared for weapons and armour.
    """
    def __init__(self, *args, equipment=None, **kwargs):
        super(EquipTableModel, self).__init__(*args, **kwargs)
        self.equipment = equipment or []
        self.header = ['Name']

    def refresh_row(self, row):
            """Refresh a specific row in the table to reflect data changes."""
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount(None) - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.equipment[index.row()].name
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        return True

    def rowCount(self, index):
        return len(self.equipment)
    
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


class WeaponTableModel(EquipTableModel):
    """See the docstring for EquipTableModel above; weapon-specific."""
    def __init__(self, *args, equipment=None, **kwargs):
        super().__init__(*args, equipment=equipment, **kwargs)


class ArmourTableModel(EquipTableModel):
    """See the docstring for EquipTableModel above; armour-specific."""
    def __init__(self, *args, equipment=None, **kwargs):
        super().__init__(*args, equipment=equipment, **kwargs)