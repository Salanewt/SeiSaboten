"""
The view file for monster data/UI stuff.

Contains:
class MonsterView(BaseView)     Defines interface behaviour for the Shops tab
  setup_connections             Links different UI elements to corresponding methods (see Note)
  init_after_rom                Refreshes the UI when a ROM is loaded
  setup_table                   Makes the monster table functional
  show_monster_stats            Populates the UI with the selected monster and its details 
  update_monster_field          Updates the currently selected monster's fields
  
  Note: There are individual methods for every comboBox, but I'm not listing them all here

MonsterTableModel               Defines how the monster table displays data
"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from .base_view import BaseView
from controllers.monsterman import MonsterManager

import globals

class MonsterView(BaseView):  
    def __init__(self, main_window):
        super().__init__(main_window)

        self.monster_model = MonsterTableModel()
        self.field_mapper = {}

        # This filter model is used for filtering table entries (i.e. search bar functionality)
        self.filter_model = QtCore.QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.monster_model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(0) # Filter on the name column (column 0)

        self.setup_table()
        self.setup_connections()
    
    def setup_connections(self):
        # Table connection
        self.main_window.monster_tableView.selectionModel().currentRowChanged.connect(
            self.show_monster_stats
        )

        # Search bar connection
        self.main_window.monster_search_lineEdit.textChanged.connect(
            self.filter_model.setFilterFixedString
        )
        
        # Create the field mapper dictionary
        # Format: line_edit: (attribute_name, max_value) - max_value=None for string fields
        self.field_mapper = {
            self.main_window.monster_sprite_lineEdit: ('sprite', 0x1FF),
            self.main_window.monster_name_lineEdit: ('name', None),
            self.main_window.monster_hp_lineEdit: ('hp', 0x1FFF),
            self.main_window.monster_pow_lineEdit: ('pow', 0xFF),
            self.main_window.monster_def_lineEdit: ('def_', 0xFF),
            self.main_window.monster_agi_lineEdit: ('agi', 0xFF),
            self.main_window.monster_int_lineEdit: ('int_', 0xFF),
            self.main_window.monster_mnd_lineEdit: ('mnd', 0xFF),
            self.main_window.monster_exp_lineEdit: ('exp', 0x3FF),
            self.main_window.monster_lucre_lineEdit: ('lucre', 0x3FF),
            self.main_window.monster_trap_lineEdit: ('trap', 0x0F),
        }
        
        # Connect all line edits to the generic update method
        for line_edit, (field, max_val) in self.field_mapper.items():
            line_edit.editingFinished.connect(
                lambda le=line_edit, f=field, m=max_val: self.update_monster_field(le, f, m)
            )
        
        # Combo box connections (still need individual methods since they pass index)
        self.main_window.monster_type_combo.currentIndexChanged.connect(
            self.update_monster_type
        )
        self.main_window.monster_prime_combo.currentIndexChanged.connect(
            self.update_monster_prime_ability
        )
        self.main_window.monster_sub_combo.currentIndexChanged.connect(
            self.update_monster_sub_ability
        )
        self.main_window.monster_item1_combo.currentIndexChanged.connect(
            self.update_monster_item1
        )
        self.main_window.monster_item2_combo.currentIndexChanged.connect(
            self.update_monster_item2
        )
        self.main_window.monster_item3_combo.currentIndexChanged.connect(
            self.update_monster_item3
        )
        
        # Resistance combo box connections
        self.main_window.monster_slash_combo.currentIndexChanged.connect(
            self.update_monster_slash
        )
        self.main_window.monster_bash_combo.currentIndexChanged.connect(
            self.update_monster_bash
        )
        self.main_window.monster_jab_combo.currentIndexChanged.connect(
            self.update_monster_jab
        )
        self.main_window.monster_light_combo.currentIndexChanged.connect(
            self.update_monster_light
        )
        self.main_window.monster_dark_combo.currentIndexChanged.connect(
            self.update_monster_dark
        )
        self.main_window.monster_moon_combo.currentIndexChanged.connect(
            self.update_monster_moon
        )
        self.main_window.monster_fire_combo.currentIndexChanged.connect(
            self.update_monster_fire
        )
        self.main_window.monster_water_combo.currentIndexChanged.connect(
            self.update_monster_water
        )
        self.main_window.monster_wood_combo.currentIndexChanged.connect(
            self.update_monster_wood
        )
        self.main_window.monster_wind_combo.currentIndexChanged.connect(
            self.update_monster_wind
        )
        self.main_window.monster_earth_combo.currentIndexChanged.connect(
            self.update_monster_earth
        )

    def init_after_rom(self):
        globals.my_monsterman = MonsterManager()

        # Add monster info; type, prime, sub senses strings to combo boxes
        self.main_window.monster_type_combo.addItems(
            globals.my_textman.all_entries_text_table(globals.my_textman.master_table_table_addresses[46]))
        self.main_window.monster_prime_combo.addItems(
            globals.my_textman.all_entries_text_table(globals.my_textman.master_table_table_addresses[45]))
        self.main_window.monster_sub_combo.addItems(
            globals.my_textman.all_entries_text_table(globals.my_textman.master_table_table_addresses[45]))
        
        # Add monster item strings to combo boxes
        self.main_window.monster_item1_combo.addItems(
            globals.my_textman.all_entries_text_table(globals.my_textman.master_table_table_addresses[0]))
        self.main_window.monster_item2_combo.addItems(
            globals.my_textman.all_entries_text_table(globals.my_textman.master_table_table_addresses[0]))
        self.main_window.monster_item3_combo.addItems(
            globals.my_textman.all_entries_text_table(globals.my_textman.master_table_table_addresses[0]))

        # Monster table handling
        self.monster_model.monsters = globals.my_monsterman.full_enemy_list
        self.monster_model.layoutChanged.emit()

        self.main_window.monster_tableView.setHorizontalHeader(self.main_window.monster_tableView.horizontalHeader())
        
        # Hide the first row in the source model (row 0)
        self.main_window.monster_tableView.setRowHidden(0, True)

        self.main_window.monster_tableView.resizeColumnsToContents()
        self.main_window.monster_tableView.resizeRowsToContents()
    
    def setup_table(self):
        """
        The monster table displays the list of monsters by index number, as well as their names and 
        monster album/book flag state.
        """
        # Hide index column
        self.main_window.monster_tableView.setHorizontalHeader(self.main_window.monster_tableView.horizontalHeader())

        # Row selection properties
        self.main_window.monster_tableView.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )
        self.main_window.monster_tableView.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )

        # Other
        self.main_window.monster_tableView.setModel(self.filter_model)
        self.main_window.monster_tableView.verticalHeader().setSectionsMovable(True)
        self.main_window.monster_tableView.verticalHeader().setDragEnabled(True)
        self.main_window.monster_tableView.verticalHeader().setDragDropMode(
            QtWidgets.QAbstractItemView.DragDropMode.InternalMove
            )
        self.main_window.monster_tableView.verticalHeader().setSectionResizeMode(
            3, 
            QtWidgets.QHeaderView.ResizeMode.Interactive
            )

    def show_monster_stats(self, current, previous):
        if current.row() >= 0:
            source_index = self.filter_model.mapToSource(current)
            monster = self.monster_model.monsters[source_index.row()]
            # Info
            self.main_window.monster_sprite_lineEdit.setText(str(monster.sprite))
            self.main_window.monster_name_lineEdit.setText(monster.name)
            self.main_window.monster_type_combo.setCurrentIndex(monster.type_)
            self.main_window.monster_prime_combo.setCurrentIndex(monster.ability_prime)
            self.main_window.monster_sub_combo.setCurrentIndex(monster.ability_sub)
            
            # Stats
            self.main_window.monster_hp_lineEdit.setText(str(monster.hp))
            self.main_window.monster_pow_lineEdit.setText(str(monster.pow))
            self.main_window.monster_def_lineEdit.setText(str(monster.def_))
            self.main_window.monster_agi_lineEdit.setText(str(monster.agi))
            self.main_window.monster_int_lineEdit.setText(str(monster.int_))
            self.main_window.monster_mnd_lineEdit.setText(str(monster.mnd))

            # Rewards
            self.main_window.monster_exp_lineEdit.setText(str(monster.exp))
            self.main_window.monster_lucre_lineEdit.setText(str(monster.lucre))
            self.main_window.monster_trap_lineEdit.setText(str(monster.trap))
            self.main_window.monster_item1_combo.setCurrentIndex(monster.item1)
            self.main_window.monster_item2_combo.setCurrentIndex(monster.item2)
            self.main_window.monster_item3_combo.setCurrentIndex(monster.item3)

            # Resistances
            self.main_window.monster_slash_combo.setCurrentIndex(monster.slash)
            self.main_window.monster_bash_combo.setCurrentIndex(monster.bash)
            self.main_window.monster_jab_combo.setCurrentIndex(monster.jab)

            self.main_window.monster_light_combo.setCurrentIndex(monster.light)
            self.main_window.monster_dark_combo.setCurrentIndex(monster.dark)
            self.main_window.monster_moon_combo.setCurrentIndex(monster.moon)
            self.main_window.monster_fire_combo.setCurrentIndex(monster.fire)
            self.main_window.monster_water_combo.setCurrentIndex(monster.water)
            self.main_window.monster_wood_combo.setCurrentIndex(monster.wood)
            self.main_window.monster_wind_combo.setCurrentIndex(monster.wind)
            self.main_window.monster_earth_combo.setCurrentIndex(monster.earth)

    # --- Update Methods --- #
    def update_monster_field(self, line_edit, field, max_val):
        """Generic update method for any monster field from line edits."""
        current_index = self.main_window.monster_tableView.currentIndex()
        if not current_index.isValid():
            return
        
        source_index = self.filter_model.mapToSource(current_index)
        monster = self.monster_model.monsters[source_index.row()]
        text = line_edit.text()
        
        if max_val is None:  # String field (like name)
            setattr(monster, field, text)
        else:  # Numeric field
            if text.isdigit():
                clamped = self.clamp(int(text), max_val)
                setattr(monster, field, clamped)
                line_edit.setText(str(clamped))  # Update with clamped value
            else:
                # Reset to current value if invalid
                line_edit.setText(str(getattr(monster, field)))
        
        # Refresh table row
        self.monster_model.refresh_row(source_index.row())

    def update_monster_type(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].type_ = index

    def update_monster_prime_ability(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].ability_prime = index

    def update_monster_sub_ability(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].ability_sub = index

    def update_monster_item1(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].item1 = index

    def update_monster_item2(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].item2 = index

    def update_monster_item3(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].item3 = index

    # Effectiveness updates
    def update_monster_slash(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].slash = index

    def update_monster_bash(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].bash = index

    def update_monster_jab(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].jab = index

    def update_monster_light(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].light = index

    def update_monster_dark(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].dark = index

    def update_monster_moon(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].moon = index

    def update_monster_fire(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].fire = index

    def update_monster_water(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].water = index

    def update_monster_wood(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].wood = index

    def update_monster_wind(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].wind = index

    def update_monster_earth(self, index):
        current_index = self.main_window.monster_tableView.currentIndex()
        if current_index.isValid():
            source_index = self.filter_model.mapToSource(current_index)
            self.monster_model.monsters[source_index.row()].earth = index


# Defines how monster data is edited and displayed
class MonsterTableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, monsters=None, **kwargs):
        super(MonsterTableModel, self).__init__(*args, **kwargs)
        self.monsters = monsters or []
        self.header = ['Name', 'in Book']

    def refresh_row(self, row):
            """Refresh a specific row in the table to reflect data changes."""
            top_left = self.index(row, 0)
            bottom_right = self.index(row, self.columnCount(None) - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if (index.column() == 0):
                return self.monsters[index.row()].name
        elif role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 1:
                if self.monsters[index.row()].in_book:
                    return Qt.CheckState.Checked
                else:
                    return Qt.CheckState.Unchecked
        return None             

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
                
        if index.column() == 1:
            old_value = self.monsters[index.row()].in_book
            
            # Handle CheckStateRole first (since that's what's actually coming through)
            if role == Qt.ItemDataRole.CheckStateRole:
                if value == 2:
                    self.monsters[index.row()].in_book = True
                else:  # Unchecked or partially checked
                    self.monsters[index.row()].in_book = False
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
                return True
                
            # Handle EditRole as fallback (though it's not being used)
            elif role == Qt.ItemDataRole.EditRole:
                self.monsters[index.row()].in_book = bool(value)
                print(f"  Changed from {old_value} to {bool(value)} via EditRole")
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
                return True
        
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return col
        return None

    def rowCount(self, index):
        return len(self.monsters)

    def columnCount(self, index):
        return len(self.header)

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable