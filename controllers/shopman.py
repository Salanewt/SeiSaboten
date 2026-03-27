"""
The controller file that is responsible for handling shop data (i.e. shop contents, not the data of 
the items they sell).

Contains:
class ShopManager
  get_shop                  Fetches shop object by ID, or else creates it if it does not exist
  set_shop                  Updates ROM with shop's data
  set_shops                 Calls method above to set all shops in a loop

General notes:
- Shops are just lists of stock IDs, meaning that there is no need to have a model file.
- Shops have a fixed size stock that is actually really generous, with 20 slots for each of: 
  - Items
  - Weapons
  - Armour
  - Accessories
- Some shops seem to be dedicated to just weapons and armour, despite no such shop appearing in the 
  final game.
  - It is likely that, for each town post-Topple, there was going to be a General Store and an 
    Equipment Store.
    - Seven (of 14 total) shops are unused.
- Note that, as mentioned in equipment_model.py, weapons and armour have a more intricate, though 
  unfinished system in the game's engine.
  - As such, shops are capable of taking your money when you try to buy weapons or armour from them, 
    but they will not actually give you product.
"""

import locations
import globals

from models.shop_model import Shop

class ShopManager:
    SHOP_COUNT = 14
    ITEM_LIMIT = 80

    # Load shop data
    def __init__(self):
        """
        Create a list of shops, with each shop having its stock saved; no discrimination between 
        item types takes place here.
        """
        # Array and addressing
        self.full_shop_list = []
        self.shop_address = int(locations.locations[globals.rom_region]['shop_data'], base=16)

        # Create Shop list, with each shop containing its array of stock IDs
        for i in range(self.SHOP_COUNT):
            temp_shop = self.get_shop(i)
            for j in range(self.ITEM_LIMIT):
                temp_stock = temp_shop.get_stock(j)
                temp_shop.shop_stock.append(temp_stock)
            self.full_shop_list.append(temp_shop)
    
    def get_shop(self, shop_num):
        """Gets the shop's stock (as raw hex)."""
        # Check if we have already loaded this shop into our master list
        # If we do, return THAT specific object so changes are shared
        if hasattr(self, 'full_shop_list') and len(self.full_shop_list) > shop_num:
            return self.full_shop_list[shop_num]

        start = self.shop_address + (shop_num * self.ITEM_LIMIT * 2)
        end = start + (self.ITEM_LIMIT * 2)
        shop_data = globals.my_file[start:end]
        return Shop(shop_data)
    
    def set_shop(self, shop_num, shop):
        """Stores the shop's stock (as raw hex) back to the ROM."""
        # Update the shop's bytes from its shop_stock list
        shop.update_bytes_from_stock()
        start = self.shop_address + (shop_num * self.ITEM_LIMIT * 2)
        end = start + (self.ITEM_LIMIT * 2)
        globals.my_file[start:end] = shop.bytes_
    
    def set_shops(self):
        """Store all shop data back to the ROM."""
        for i in range(self.SHOP_COUNT):
            self.set_shop(i, self.full_shop_list[i])

