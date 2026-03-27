"""
The controller file that is responsible for handling monster data.

Contains:
class MonsterManager
  get_monsters_in_book          Gets bestiary flags
  write_monster_book            Sets bestiary flags
  get_enemy                     Fetches monster object by ID, or else creates it
  set_enemy                     Updates ROM with monster's data
  set_enemies                   Calls method above to set all monsters in a loop

TODO: 
- Split the code into view and controller (some Main.pyw code would also move to the view).

General notes:
- Some data is still unknown/undocumented, while a couple of things are *likely* related to events 
  or scripting (e.g. an "Event ID" that triggers on last kill).
  - The original creator of this program possibly identified a "movement speed" variable for enemies 
    that warrants further research.
- The bulk of this code was inherited from the old project, including the bestiary stuff (which I
  haven't tried to understand as a system yet).
"""

import locations
import globals

from models.monster_model import Monster

class MonsterManager:
    # Total monsters
    ENEMY_COUNT = 180

    def __init__(self):

        # Array for storing enemy data and names
        self.full_enemy_list = []

        # Key:Value == Monster_ID:Bool, depending in monster book or not; 
        self.monster_in_book_dict = {}
        
        self.enemy_address = int(locations.locations[globals.rom_region]['enemy_data'], base=16)

        monster_book_pointer = int(locations.locations[globals.rom_region]['monster_book_pointer'], base=16)
        self.monster_book_address = int.from_bytes(globals.my_file[monster_book_pointer:monster_book_pointer + 0x4],
                                                   byteorder='little') - 0x08000000

        self.get_monsters_in_book(self.monster_book_address)

        # 3rd table in master table contains the monster names
        self.enemy_names = globals.my_textman.all_entries_text_table(
            globals.my_textman.master_table_table_addresses[2]
            )

        # Load enemy data
        for i in range(self.ENEMY_COUNT):
            temp_enemy = self.get_enemy(i)
            self.full_enemy_list.append(temp_enemy)

        # Salanewt's note: This variable seems to have been used for the randomiser, 
        # which I have disabled right now; the old comments are still here

        # this is a shallow(?) copy, any changes to main will be reflected in full... good in a way
        # but if i shuffle main list, the order is full not changed
        # so I think I will need to make a real deep copy of this
        # or, just assign main list back to full... not a big problem i think
        self.main_enemy_list = self.full_enemy_list[1:123]

    def get_monsters_in_book(self, address):
        """
        Hold list of monster IDs corresponding with monsters that can be found in the monster 
        album/bestiary
        """
        self.monster_in_book_dict = {}
        for i in range(self.ENEMY_COUNT):
            self.monster_in_book_dict[i] = False

        # 0xFFFF = The terminator for end of list
        it = iter(globals.my_file[address:address + (0x02 * 180)])
        for x in it:
            y = next(it)
            char = (y << 8) | x
            if char == 0xFFFF:
                return True
            self.monster_in_book_dict[char] = True
        return False

    def write_monster_book(self, address):
        """Update the monster album."""
        monster_bytes = bytearray()
        for i, monster in enumerate(self.full_enemy_list):
            if monster.in_book:
                b1, b2 = i.to_bytes(2, byteorder='little')
                monster_bytes.append(b1)
                monster_bytes.append(b2)
        monster_bytes.append(0xFF)
        monster_bytes.append(0xFF)
        monster_bytes.append(0xFF)
        monster_bytes.append(0xFF)
        globals.my_file[address:address + len(monster_bytes)] = monster_bytes

    def get_enemy(self, enemy_num):
        """Fetch one enemy's data."""
        if hasattr(self, 'full_enemy_list') and len(self.full_enemy_list) > enemy_num:
            return self.full_enemy_list[enemy_num]

        enemy_data = globals.my_file[
                     self.enemy_address + (enemy_num * 0x20):self.enemy_address + 0x20 + (enemy_num * 0x20)]
        return Monster(enemy_data, self.enemy_names[enemy_num], self.monster_in_book_dict[enemy_num])

    def set_enemy(self, num, enemy):
        """Update one enemy's data."""
        globals.my_file[self.enemy_address + (num * 0x20):self.enemy_address + 0x20 + (num * 0x20)] = enemy.bytes_

    # Update ROM
    def set_enemies(self):
        """Update all enemy data."""
        # Write name table
        self.enemy_names = [enemy.name for enemy in self.full_enemy_list]
        globals.my_textman.master_table_table_addresses[2] = self.enemy_names

        # Write enemy data
        for i in range(self.ENEMY_COUNT):
            self.set_enemy(i, self.full_enemy_list[i])