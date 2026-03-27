"""
The controller file that is responsible for handling equipment. Like the models, we have an initial 
super class and then three subclasses; also like the models, I chose to keep them all in one file 
for simplicity's sake and because both weapons and armour are similar in the game's engine.

Contains:
class EquipmentManager
  get_equip                  Fetches equipment by ID, or else creates it if it does not exist
  set_equip                  Updates ROM with equipment's data
  set_equips                 Calls method above to set all equipment in a loop

class WeaponManager(EquipmentManager)
class ArmourManager(EquipmentManager)

Note: Weapons and armour have 255 strings for their names and for their descriptions (like Items). 
However, they do not have that many table entries (unlike Items).
"""

import locations
import globals

from models.equipment_model import Weapon, Armour

class EquipmentManager:
    """
    The actual controller class for handling equipment. Like with the other equipment code files, I 
    implemented a super class with related subclasses.
    """
    # Load item data
    def __init__(self):
        """
        This initialises the controller, which handles a collection of [equipment] objects and 
        associates otherwise disconnected name and description strings with them.
        """
        # Total items
        self.equip_count = None

        # Arrays for storing item data
        self.full_equip_list = []

        # Address for item-specific data in ROM
        self.equip_address = None

        # Grab item names, descriptions
        self.equip_names = None
        self.equip_descriptions = None

        # Grab string table indices
        self.name_table_index = None
        self.desc_table_index = None

    def get_equip(self, equip_num):
        """
        This actually gets one equipment object from its relevant data table. Functionality is 
        handled in the specific sub classes that use this function.
        """
        return None

    def set_equip(self, num, equip):
        """
        This stores data to the correct equipment object in the ROM, not including its name or 
        description.
        """
        globals.my_file[self.equip_address + (num * 0x08):self.equip_address + 0x08 + (num * 0x08)] = equip.bytes_

    # Update ROM
    def set_equips(self):
        """This stores data to all equipment of its type, including names and descriptions."""
        # Write name, description tables
        self.equip_names = [equip.name for equip in self.full_equip_list]
        globals.my_textman.master_table_table_addresses[self.name_table_index] = self.equip_names
        
        self.equip_descriptions = [equip.description for equip in self.full_equip_list]
        globals.my_textman.master_table_table_addresses[self.desc_table_index] = self.equip_descriptions

        # Write item data
        for i in range(self.equip_count):
            self.set_equip(i, self.full_equip_list[i])

class WeaponManager(EquipmentManager):
    """The weapon-specific sub class of the equipment controller."""
    def __init__(self):
        super().__init__()
        self.equip_count = 147

        self.equip_address = int(locations.locations[globals.rom_region]['weapon_data'], base=16)

        # Set Weapon-specific text table indices
        self.name_table_index = 11
        self.desc_table_index = 12

        self.equip_names = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[self.name_table_index]
            )
        self.equip_descriptions = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[self.desc_table_index]
            )

        # Create Weapon list
        for i in range(self.equip_count):
            temp_equip = self.get_equip(i)
            self.full_equip_list.append(temp_equip)

    def get_equip(self, equip_num):
        if hasattr(self, 'full_equip_list') and len(self.full_equip_list) > equip_num:
            return self.full_equip_list[equip_num]

        equip_data = globals.my_file[
                self.equip_address + (equip_num * 0x08):self.equip_address + 0x08 + (equip_num * 0x08)]
        return Weapon(equip_data, self.equip_names[equip_num], description=self.equip_descriptions[equip_num])

class ArmourManager(EquipmentManager):
    """The armour-specific sub class of the equipment controller."""
    def __init__(self):
        super().__init__()
        self.equip_count = 121

        self.equip_address = int(locations.locations[globals.rom_region]['armour_data'], base=16)

        # Set Armour-specific text table indices
        self.name_table_index = 13
        self.desc_table_index = 14

        self.equip_names = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[self.name_table_index]
            )
        self.equip_descriptions = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[self.desc_table_index]
            )

        # Create Armour list
        for i in range(self.equip_count):
            temp_equip = self.get_equip(i)
            self.full_equip_list.append(temp_equip)

    def get_equip(self, equip_num):
        if hasattr(self, 'full_equip_list') and len(self.full_equip_list) > equip_num:
            return self.full_equip_list[equip_num]

        equip_data = globals.my_file[
                self.equip_address + (equip_num * 0x08):self.equip_address + 0x08 + (equip_num * 0x08)]
        return Armour(equip_data, self.equip_names[equip_num], description=self.equip_descriptions[equip_num])
