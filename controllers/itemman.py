"""
The controller file that is responsible for handling item data.

Contains:
class ItemManager
  get_item              Fetches item object by ID, or else creates it if it does not exist
  set_item              Updates ROM with item's data
  set_items             Calls method above to set all items in a loop
"""

import locations
import globals

from models.item_model import Item

class ItemManager:
    # Total items
    ITEM_COUNT = 256

    # Load item data
    def __init__(self):
        # Arrays for storing item data
        self.full_item_list = []

        # Address for item-specific data in ROM
        self.item_address = int(locations.locations[globals.rom_region]['item_data'], base=16)

        # Grab Item names, descriptions
        self.item_names = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[0]
            )
        self.item_descriptions = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[7]
            )

        # Create Item list
        for i in range(self.ITEM_COUNT):
            temp_item = self.get_item(i)
            self.full_item_list.append(temp_item)

    # Create Item
    def get_item(self, item_num):
        # Check if we have already loaded this item into our master list
        # If we do, return THAT specific object so changes are shared
        if hasattr(self, 'full_item_list') and len(self.full_item_list) > item_num:
            return self.full_item_list[item_num]
        
        # This part only runs during the very first boot-up
        item_data = globals.my_file[
                    self.item_address + (item_num * 0x0C):self.item_address + 0x0C + (item_num * 0x0C)]
        return Item(item_data, self.item_names[item_num], description=self.item_descriptions[item_num])

    def set_item(self, num, item):
        globals.my_file[self.item_address + (num * 0x0C):self.item_address + 0x0C + (num * 0x0C)] = item.bytes_

    # Update ROM
    def set_items(self):
        # Write name, description tables
        self.item_names = [item.name for item in self.full_item_list]
        globals.my_textman.master_table_table_addresses[0] = self.item_names
        self.item_descriptions = [item.description for item in self.full_item_list]
        globals.my_textman.master_table_table_addresses[7] = self.item_descriptions

        # Write item data
        for i in range(self.ITEM_COUNT):
            self.set_item(i, self.full_item_list[i])