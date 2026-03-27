"""
While main.pyw may be the main file for actually running this editor, this is the interface through 
which all other functionality happens. The bulk of its design can be found in the ui/gui.ui file. I 
wouldn't mind replacing it with actual code later on, but there is no real need and it serves its 
purpose just fine.

Contains:
class MainWindow                The main UI and functionality is set up here
  init_after_rom                Loads data, etc.
  openFileNameDialog            Open file option
  saveFileDialog                Save file option
  show_credits                  Shows the credits window, with included credits

  To be moved:
    load_dialog
    load_text_table
    dialog_export_json

TODO:
- Text code should be moved into a different file (i.e. textman.py or a related file).
- Some other code in some of these methods should also be moved to more suitable files.
"""

from PyQt6 import QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import zlib
import json

import locations
import globals

from views import monster_view, item_view, equipment_view, shop_view, charsprite_view
from util import string_highlighter

from widgets import string2bytes
import widgets.palette_editor as palette_editor

import textman

# dirname = os.path.dirname(PyQt6.__file__)
# plugin_path = os.path.join(dirname, 'plugins', 'platforms')
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

# Was 0.6 under old management
__version__ = '0.1'

qt_creator_file = "ui/gui.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

rom_info = {
    'AVSJ': {
        'region': 'J',
        'name': 'Japan',
        'clean_crc32': '31B220E5'
    },
    'AVSE': {
        'region': 'E',
        'name': 'USA',
        'clean_crc32': '7F1EAC75'
    },
    'AVSP': {
        'region': 'P',
        'name': 'Europe - En',
        'clean_crc32': '88E64A8A'
    }
}

# --- This is the class that handles the main window and all of the interactions with it  ---
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    This is the class responsible for building the main window.

    TODO: More cleanup, MVC transition.
    """
    def __init__(self):
        """
        Creates the editor window.
        """
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle(f'SeiSaboten v{__version__}')
        self.setWindowIcon(QtGui.QIcon("ui/window_icon.ico"))

       # --- Palette Manager --- #
        self.palette_editor = palette_editor.PaletteEditor()
        palette_tab = self.sprites_tabWidget.findChild(QtWidgets.QWidget, "palette_tab")
        if palette_tab:
            # Create a layout for the tab if it doesn't have one
            if not palette_tab.layout():
                layout = QtWidgets.QVBoxLayout(palette_tab)
                layout.addWidget(self.palette_editor)

        # Load Table Models
        self.monster_list_table = monster_view.MonsterTableModel()
        self.item_list_table = item_view.ItemTableModel()
        self.weapon_list_table = equipment_view.WeaponTableModel()
        self.armour_list_table = equipment_view.ArmourTableModel()
        self.shop_list_table = shop_view.ShopTableModel()

        self.sprite_list_table = charsprite_view.SpriteTableModel()
        self.sprite_anim_list_table = charsprite_view.SpriteAnimSlotModel()
        self.text_table_model = textman.TextTableModel()

        # Initialise Views
        self.monster_view = monster_view.MonsterView(self)
        self.item_view = item_view.ItemView(self)
        self.weapon_view = equipment_view.WeaponView(self)
        self.armour_view = equipment_view.ArmourView(self)
        self.shop_view = shop_view.ShopView(self)
        self.sprite_view = charsprite_view.SpriteView(self)
        self.dialog_view = None

        # Everything from Sprites Tab comment until Other Features should be moved

        # --- Sprites Tab --- #
        # Sprite animation slot table
        self.sprite_anim_slot_tableView.setHorizontalHeader(self.sprite_anim_slot_tableView.horizontalHeader())

        self.sprite_anim_slot_tableView.setModel(self.sprite_anim_list_table)
        self.sprite_anim_slot_tableView.verticalHeader().setSectionsMovable(True)
        self.sprite_anim_slot_tableView.verticalHeader().setDragEnabled(True)
        self.sprite_anim_slot_tableView.verticalHeader().setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.sprite_anim_slot_tableView.verticalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Interactive)

        # --- Random Tab --- #
        # self.shuffle_monsters_btn.pressed.connect(self.shuffle_monsters)
        # self.randomize_weaknesses_btn.pressed.connect(self.randomize_weaknesses)
        # self.export_dialog_btn.pressed.connect(self.dialog_export_json)

        # self.weaknesses_not_all_none_checkbox.stateChanged.connect(self.toggleCombo)

        # --- Dialog, Text tabs, functionality --- #
        self.tabletext_listview.setModel(self.text_table_model)

        self.highlighter = string_highlighter.StringVariableHighlighter(self.textEdit.document())

        # --- Other Features --- #
        self.actionLoad.triggered.connect(self.openFileNameDialog)
        self.actionSave.triggered.connect(self.saveFileDialog)

        self.actionString_to_Bytes_Converter.setEnabled(False)
        self.string_to_bytes_widget = string2bytes.StringToBytesWidget()
        self.actionString_to_Bytes_Converter.triggered.connect(self.string_to_bytes_widget.show)

        self.actionCredits.triggered.connect(self.show_credits)

    def init_after_rom(self):
        """
        Stuff that should only be done after loading a ROM happens here.

        TODO: More cleanup, MVC transition.
        """
        # General views/utilities/controllers/etc.
        # TODO: Create views for this stuff and load those here instead
        globals.my_textman = textman.TextManager()
        globals.my_paletteman = palette_editor.PaletteManager()

        # Tab-focused views; they could be used elsewhere, if needed        # Main Tabs
        self.monster_view.init_after_rom()                                  # [0]
        self.item_view.init_after_rom()                                     # [1][0]
        self.weapon_view.init_after_rom()                                   # [1][1]
        self.armour_view.init_after_rom()                                   # [1][2]
        self.shop_view.init_after_rom()                                     # [1][3]
        self.sprite_view.init_after_rom()                                   # [4]
        



        # --- Dialog Tab ---
        # TODO: Port to View file
        self.dialogpicker_combo.addItems([str(i) for i in range(
            globals.my_textman.get_dialog_entries_count(globals.my_textman.story_table_address))])
        self.dialogpicker_combo.currentIndexChanged.connect(self.load_dialog)
        self.load_dialog(0)

        self.tablepicker_combo.addItems([str(i) for i in range(len(globals.my_textman.master_table_list))])
        self.tablepicker_combo.currentIndexChanged.connect(self.load_text_table)
        self.text_table_model.text_entries = globals.my_textman.master_table_list[0]
        self.text_table_model.layoutChanged.emit()

        # --- Other Stuff ---
        self.main_tabWidget.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.actionString_to_Bytes_Converter.setEnabled(True)


    def openFileNameDialog(self):
        """Responsible for the Open File dialog."""
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose your ROM file", "",
                                                  "GBA ROM Files (*.gba);;All Files (*.*)")
        # Checks ROM version and crc32 hash to determine if ROM is compatible (but... why this way?)
        if fileName:
            with open(fileName, 'rb') as fh:
                globals.my_file = fh.read()
                crc_sum = f'{zlib.crc32(globals.my_file) & 0xffffffff:08X}'
                rom_code = (globals.my_file[0xAC:0xB0]).decode('ansi')
                if rom_code in rom_info:
                    if crc_sum == rom_info[rom_code]['clean_crc32']:
                        Palette = QtGui.QPalette()
                        Palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor('#3BB300'))
                        self.crc_display.setPalette(Palette)
                    else:
                        Palette = QtGui.QPalette()
                        Palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor('#B30000'))
                        self.crc_display.setPalette(Palette)

                    globals.rom_region = rom_info[rom_code]['region']

            self.crc_display.setText(str(crc_sum))
            globals.my_file = bytearray(globals.my_file)

            self.init_after_rom()

    def saveFileDialog(self):
        """Responsible for the Save File dialog, and also for modifying the ROM itself."""
        fileName, _ = QFileDialog.getSaveFileName(self, "Save your ROM file", "",
                                                  "GBA ROM Files (*.gba);;All Files (*.*)")
        if fileName:
            self.text_table_model.layoutChanged.emit()

            # Store current monster data
            globals.my_monsterman.full_enemy_list = self.monster_view.monster_model.monsters
            globals.my_monsterman.set_enemies()

            # Store current item data
            globals.my_itemman.full_item_list = self.item_view.item_model.items
            globals.my_itemman.set_items()

            # Store current weapon data
            globals.my_weaponman.full_equip_list = self.weapon_view.equip_model.equipment
            globals.my_weaponman.set_equips()

            # Store current armour data
            globals.my_armourman.full_equip_list = self.armour_view.equip_model.equipment
            globals.my_armourman.set_equips()

            # Store current shop data
            globals.my_shopman.full_shop_list = self.shop_view.shop_model.shops
            globals.my_shopman.set_shops()

            # Store current sprite data
            if hasattr(self.sprite_view, 'store_current_data'):
                self.sprite_view.store_current_data()
        
            # Then save all sprite data to ROM
            if hasattr(globals, 'my_spriteman'):
                globals.my_spriteman.set_sprites()

            # Salanewt: Everything after this is from "the before-times" except for tweaking "required_rom_size" and changing its comment
            # Extend rom
            required_rom_size = 0x01FFFFFF  #TODO, someday: Filesize calculation algorithm
            current_rom_size = len(globals.my_file)
            
            if current_rom_size < required_rom_size:
                globals.my_file = globals.my_file + (b'\x00' * 0x01000000)
            # if we save twice, this happens twice... not good
            # Subrosian edit - now allows for saving multiple times without adding extra space

            # extend rom
            globals.my_monsterman.write_monster_book(0x01500000)
            monster_book_pointer = int(locations.locations[globals.rom_region]['monster_book_pointer'], base=16)
            globals.my_file[monster_book_pointer:monster_book_pointer + 0x4] = (0x01500000 + 0x08000000).to_bytes(4,
                                                                                                                  byteorder='little')
            with open(fileName, 'wb') as f:
                f.write(globals.my_file)

            # disable loading and saving again, until proper re-init has been added
            self.actionLoad.setEnabled(False)
            self.actionSave.setEnabled(False)

    def show_credits(self):
        """The Credits window."""
        msg = QMessageBox()
        msg.setWindowTitle('Credits')
        msg.setText(
            f'v{__version__}\n'
            'Salanewt: Thank you for checking this out! \n\n'
            'Original and prior work done by:\n'
            '\u2023 Joshua Miller - The original SeiSaboten creator: https://jtm.gg \n'
            '\u2023 Subrosian - Reportedly fixed a handful of bugs.\n'
            '\n'
            'Special thanks to Revier for research assistance!'
        )       
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

# --- Text Stuff Below --- #
    def load_dialog(self, i):        
        """Loads a specific entry from the story string table.

        TODO: textman.py or related files should be solely responsible for text stuff. MVC 
        transition has not been started for it yet.
        """

        this_dialog = globals.my_textman.story_table_list[i]
        self.textEdit.document().setPlainText(this_dialog['string'])
        if this_dialog['actor']:
            self.dialog_sprite_group.setChecked(True)
            if this_dialog['actor']['position'] == 'Left':
                self.dialog_sprite_pos.setCurrentIndex(0)
            else:
                self.dialog_sprite_pos.setCurrentIndex(1)
            self.dialog_sprite_id.setText(str(this_dialog['actor']['id']))

        else:
            self.dialog_sprite_group.setChecked(False)

    def load_text_table(self, i):
        """Loads text from the master string table. 

        TODO: textman.py or related files should be solely responsible for text stuff. MVC 
        transition has not been started for it yet.
        """
        self.text_table_model.text_entries = globals.my_textman.master_table_list[i]
        self.text_table_model.layoutChanged.emit()

    # Note: Currently unused because randomiser stuff is disabled/commented out
    def dialog_export_json(self):
        """Dumps all of the game's story text to a JSON file.

        TODO: textman.py or related files should be solely responsible for text stuff. MVC 
        transition has not been started for it yet.
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Dialog export", "",
                                                  "JSON File (*.json);;All Files (*.*)", options=options)
        if fileName:
            with open(fileName, 'w', encoding='utf-8') as json_file:
                json.dump(globals.my_textman.story_table_list, json_file, ensure_ascii=False, indent=2)