"""
The controller file that is responsible for handling character sprite data. Other kinds of 
sprites/GFX should be handled by other files.

Contains:
class SpriteManager
  get_sprite                    Gets sprite data based on table ID
  set_sprites                   Sets all sprite data
  set_sprite                    Sets sprite data based on table ID (currently just palette)

TODO: 
- Creating a sprite viewer is one of my next goals, but I need to take baby steps. As such, I want 
  to at least do the following:
  - Load and render pixel data under the Pixel Data tab.

- Eventually, the base sprite table address should be either be read from the ROM, or read from a 
  file that can be updated whenever the ROM is updated. This is because all of the sprite data will 
  have to be repacked if we allow for the addition or deletion of data (e.g. adding more frames to 
  an animation, or removing unused pixel data, or adding some new sprites and extending the sprite 
  table). 

General notes:
- "Sprite" will refer to each entry within the sprite table (i.e. a sprite file/pack).
- "Frame" will refer to each individual frame within an animation (AKA each sprite).
- "Pixel data" will refer to the raw pixel data that is used in a frame.
- An "animation slot" is associated with a particular action and is filled with an animation ID, 
  while an "animation" doesn't inherently have an association.
- All sprite data appears to be uncompressed.
- The game assumes that palette length (in bytes) must be a multiple of 0x20, even if you set a 
  different number here; haven't looked into why yet.

The overall structure of the sprite data is as follows:
- It starts with an offset table, where each entry has the following format: xxyyyyyy
    xx = unknown_flag (00 or 01); have yet to read relevant code
    yyyyyy = offset to the sprite's animation data (relative to the start of the sprite data)
- The resulting address for a given sprite goes to a sprite's header section, containing the 
  following:
    1. Animation Data Offset
    2. Frame Data Offset
    3. ??? Offset
    4. Pixel Data Offset
    5. Palette Data Offset
    a) Unknown1
    b) Unknown2
    c) Unknown3
    d) Unknown4
    e) anim_slot_total - The number of animation slots available
    {anim_slot_total} slots total, which are filled with 16-bit sprite-specific animation IDs but 
        which tend to correspond with particular actions and directions 
            (e.g. Walking Facing Down, or Attacking with Sword Facing Left)

Personal notes:
- I would like to eventually implement a compression algorithm for sprite data, as everything is 
  uncompressed and it takes up a lot of space.
- It would be also nice if some sprite data, like various weapons, bones/dead enemy frames, etc. 
  could be separated into their own sprite files/packs and borrowed from within a sprite's own 
  table.
"""

import locations
import globals

from models.charsprite_model import CharSprite


class SpriteManager:
    # Load sprite data
    def __init__(self):
        self.sprite_pack_offsets = []       # For info box
        self.sprite_pack_unk_bools = []     # For info box; should be toggleable by the user
        self.sprite_pack_addresses = []     # For quickly locating sprite data
        self.full_sprite_list = []          # For storing sprite instances
        self.total_sprite_filesize = 0      # To be calculated, from start to end of all data

        # Sprite table is a list of 4-byte entries; includes offset and unknown bool
        self.sprite_table = int(
            locations.locations[globals.rom_region]['charsprite_tables'], base=16
            )
        base_table_addr = int(self.sprite_table)

        # Calculate Sprite Count (using index 1 sprite's offset in calculation)
        # Note: For some reason, index 0 sprite's offset is much later than the rest of them; not sure what this means 
        # yet, unless the developers used it to point to the very end of the sprite data (I haven't checked)
        first_entry = globals.my_file[self.sprite_table + 0x04:self.sprite_table + 0x07]
        first_offset = int.from_bytes(first_entry, 'little')
        self.sprite_count = first_offset >> 2

        # Load sprite data
        for i in range(self.sprite_count):
            # Get the 4-byte entry for this sprite
            entry_offset = self.sprite_table + (i * 0x04)
            temp_sprite_offset_bytes = globals.my_file[entry_offset:entry_offset + 0x04]
                     
            # Extract and store the 24-bit offset (ignoring the flag byte)
            sprite_offset = int.from_bytes(temp_sprite_offset_bytes[0:3], 'little')
            self.sprite_pack_offsets.append(sprite_offset)

            # Store the visibility flag (fourth byte of the entry)
            flag = temp_sprite_offset_bytes[3]
            self.sprite_pack_unk_bools.append(flag)

            # Calculate and store the absolute address
            temp_sprite_address = base_table_addr + sprite_offset
            self.sprite_pack_addresses.append(temp_sprite_address)

            # Create sprite instance
            temp_sprite = self.get_sprite(base_table_addr, i)
            temp_sprite.is_visible = self.sprite_pack_unk_bools[i]
            self.full_sprite_list.append(temp_sprite)
        
        # Debug - Initially used to verify that I was getting the right info from the sprite table
        # print(f"Sprite table base: 0x{self.sprite_table:X}")        # 0x77154C
        # print(f"First entry offset: 0x{first_offset:X}")            # 620
        # print(f"Calculated sprite count: {self.sprite_count}")      # 392

    def get_sprite(self, base_table_addr, sprite_num):
        return CharSprite(base_table_addr, self.sprite_pack_addresses[sprite_num], sprite_num)

    def set_sprites(self):
        """Save all sprite data to ROM."""
        for i, sprite in enumerate(self.full_sprite_list):
            self.set_sprite(i, sprite)
    
    def set_sprite(self, num, sprite):
        """Save a single sprite's data to ROM."""
        if num >= len(self.full_sprite_list):
            return False
        
        # Save palette data if it exists
        if hasattr(sprite, 'palette_rgb') and sprite.palette_rgb is not None:
            from widgets.palette_editor import PaletteManager
            palette_manager = PaletteManager()
            palette_manager.save_palette_to_address(
                sprite.palette_address,
                sprite.palette_rgb,
                sprite.palette_length
            )
        
        # TODO: Save other sprite data sections as they're implemented
        # - Animation data
        # - Frame data  
        # - Unknown data
        # - Pixel data
        # - Animation slots
        
        return True
