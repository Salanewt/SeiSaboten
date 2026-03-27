"""
This view handles connectivity between the UI and the ROM's character sprite data (i.e. players, 
NPCs, monsters, etc.); other kinds of sprites will likely be handled elsewhere in the future.

Contains:
class SpriteView(BaseView)          Defines interface behaviour for the Sprites tab
  setup_connections                 Links different UI elements to corresponding methods
  init_after_rom                    Refreshes the UI when a ROM is loaded
  setup_table                       Makes the sprite table functional
  update_sprite_palette             Updates the chosen palette with new palette data
  store_current_data                Stores current palette to selected sprite
  process_sprite_data               Refreshes sprite details, calling following method to do so
  show_sprite_data                  Shows sprite data from whatever sprite object is selected
  store_sprite_data                 Placeholder: Will store updated (pixel?) data

SpriteTableModel                    Defines how the full sprite table displays data
SpriteAnimSlotModel                 Defines how the anim_slot table displays data

TODO:
- Need to figure out where to put a "palette length" variable in the UI (being built with Qt Widgets 
  Designer as of writing).
- Goals: The tab should have the widget, a lineEdit field for viewing the palette's length (or maybe 
  a spinbox), and some way of viewing a sprite/animation to preview any palette changes.
"""

from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from .base_view import BaseView
from controllers.spriteman import SpriteManager

import globals

class SpriteView(BaseView):  
    def __init__(self, main_window):
        super().__init__(main_window)
 
        self.sprite_model = SpriteTableModel()
        self.palette_editor = main_window.palette_editor
        
        self.current_sprite = None
        self.current_row = -1

        self.setup_table()
        self.setup_connections()
    
    def setup_connections(self):
        self.main_window.sprite_tableView.selectionModel().currentRowChanged.connect(
            self.process_sprite_data
        )

        if self.palette_editor:
            self.palette_editor.apply_btn.clicked.connect(self.update_sprite_palette)
    
    def init_after_rom(self):
        globals.my_spriteman = SpriteManager()

        self.sprite_model.sprites = globals.my_spriteman.full_sprite_list
        self.sprite_model.layoutChanged.emit()

        # Horizontal header
        self.main_window.sprite_tableView.setHorizontalHeader(self.main_window.sprite_tableView.horizontalHeader())

        # Hide first row
        self.main_window.sprite_tableView.setRowHidden(0, True)

        # Row selection properties
        self.main_window.sprite_tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.main_window.sprite_tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        # Other
        self.main_window.sprite_tableView.resizeColumnsToContents()
        self.main_window.sprite_tableView.resizeRowsToContents()


        # Horizontal header
        self.main_window.sprite_anim_slot_tableView.setHorizontalHeader(
            self.main_window.sprite_anim_slot_tableView.horizontalHeader()
            )

        # Row selection properties
        self.main_window.sprite_anim_slot_tableView.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
            )
        self.main_window.sprite_anim_slot_tableView.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )

        # Other
        self.main_window.sprite_anim_slot_tableView.resizeColumnsToContents()
        self.main_window.sprite_anim_slot_tableView.resizeRowsToContents()

    def setup_table(self):
        self.main_window.sprite_tableView.setHorizontalHeader(
            self.main_window.sprite_tableView.horizontalHeader()
            )

        # Row selection properties
        self.main_window.sprite_tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.main_window.sprite_tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        self.main_window.sprite_tableView.setModel(self.sprite_model)
        self.main_window.sprite_tableView.verticalHeader().setSectionsMovable(True)
        self.main_window.sprite_tableView.verticalHeader().setDragEnabled(True)
        self.main_window.sprite_tableView.verticalHeader().setDragDropMode(
            QtWidgets.QAbstractItemView.DragDropMode.InternalMove
            )
        self.main_window.sprite_tableView.verticalHeader().setSectionResizeMode(
            3, 
            QtWidgets.QHeaderView.ResizeMode.Interactive
            )

        self.main_window.sprite_tableView.selectionModel().currentRowChanged.connect(self.process_sprite_data)

        if len(self.sprite_model.sprites) > 1:
            self.main_window.sprite_tableView.selectRow(1)

    def update_sprite_palette(self):
        """Called when apply button is clicked - updates the current sprite's palette."""
        if self.current_sprite and self.palette_editor:
            modified_palette = self.palette_editor.get_current_palette()
            if modified_palette:
                # print(f"Apply clicked - updating sprite at 0x{self.current_sprite.sprite_header:08X}")
                # print(f"Palette length: {len(modified_palette)}")
                # print(f"First few colors: {modified_palette[:3]}")
                
                # Store the palette in the sprite object (NOT ROM)
                self.current_sprite.set_palette(modified_palette)

    def store_current_data(self):
        """Store current sprite's data before switching."""
        self.update_sprite_palette()

    # Deal with sprite data
    def process_sprite_data(self, current, previous):
        """
        Updates view based on which sprite has been selected, while storing the previously selected 
        sprite's data.
        """
        if previous.row() >= 0 and self.current_sprite:
            self.store_current_data()
        
        if current.row() >= 0:
            self.current_row = current.row()
            self.show_sprite_data(self.sprite_model.sprites[current.row()])

    def show_sprite_data(self, sprite):
        """Loads the currently selected sprite's data."""
        self.current_sprite = sprite
        
        # Info
        self.main_window.sprite_header_lineEdit.setText(f"0x{sprite.sprite_header:08X}")
        self.main_window.sprite_visibility_checkbox.setChecked(sprite.is_visible == 1)
        self.main_window.animation_data_lineEdit.setText(f"0x{sprite.animation_data_header:08X}")
        self.main_window.frame_data_lineEdit.setText(f"0x{sprite.frame_data_header:08X}")
        self.main_window.unknown_sprite_data_lineEdit.setText(f"0x{sprite.unknown_data_header:08X}")
        self.main_window.pixel_data_lineEdit.setText(f"0x{sprite.pixel_data_header:08X}")
        self.main_window.palette_data_lineEdit.setText(f"0x{sprite.palette_data_header:08X}")

        # Sprite Properties
        self.main_window.sprite_unknown1_lineEdit.setText(str(sprite.unknown_var1))
        self.main_window.sprite_unknown2_lineEdit.setText(str(sprite.unknown_var2))
        self.main_window.sprite_unknown3_lineEdit.setText(str(sprite.unknown_var3))
        self.main_window.sprite_unknown4_lineEdit.setText(str(sprite.unknown_var4))
        self.main_window.sprite_anim_slot_total_lineEdit.setText(str(sprite.anim_slot_total))

        # Animation Slots
        anim_slot_model = self.main_window.sprite_anim_slot_tableView.model()
        if anim_slot_model:
            anim_slot_model.anim_slots = sprite.anim_slot_array
            anim_slot_model.layoutChanged.emit()

        # Palette
        if sprite.palette_address and sprite.palette_length > 0:
            palette_rgb = sprite.get_palette()
            # print(f"Loading sprite at 0x{sprite.sprite_header:08X}")
            # print(f"Loaded palette length: {len(palette_rgb) if palette_rgb else 0}")
            # print(f"First few colors: {palette_rgb[:3] if palette_rgb else 'None'}")
            
            if palette_rgb and self.palette_editor:
                self.palette_editor.set_palette_data(
                    sprite.palette_address,
                    sprite.palette_length,
                    palette_rgb
                )

    def store_sprite_data(self, sprite):
        # sprite.anim_slot_array = self.sprite_anim_slot_model.anim_slots
        pass

# --- Table Models --- #
# Defines how sprite data is displayed
class SpriteTableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, sprites=None, **kwargs):
        super(SpriteTableModel, self).__init__(*args, **kwargs)
        self.sprites = sprites or []
        self.header = ['Address']
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return f"0x{self.sprites[index.row()].sprite_header:08X}"
        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        return True

    def rowCount(self, index):
        return len(self.sprites)
    
    def columnCount(self, index):
        return len(self.header)
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            # Subtraction is done because the game does its sprite indexing strangely; 
            # index 0 = Hero, not "nothing", despite Hero's sprite being the second table entry
            return str(col - 1)     
        return None
    
    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

# Used to display the animation slots for a sprite; made into a model in case we want to do something special with it 
# (e.g. select animations for map scripting) down the road
class SpriteAnimSlotModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, anim_slots=None, **kwargs):
        super(SpriteAnimSlotModel, self).__init__(*args, **kwargs)
        self.anim_slots = anim_slots or []
        self.header = ['Animation ID']
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return str(self.anim_slots[index.row()])
        return None
    
    def rowCount(self, index):
        return len(self.anim_slots)
    
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