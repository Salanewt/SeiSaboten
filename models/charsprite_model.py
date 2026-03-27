"""
This model specifically refers to the sprites found within the character sprite table, and not the 
various menu icons, etc. that can be found elsewhere.

TODO:
- Finish implementing the rest of this. We still have the animation, frame, and unknown data banks 
to go through. 

Copied from our Google Doc:
Animation Data:
		16-bit x num	= Offsets for specific animations, added to Animation Data address
The number of animations is variable
		8-bit		= Unknown; is often 08, 09, or 0A
		8-bit		= Frame Count
		Frame
		    	8-bit	= Frame Delay
			12-bit	= Sprite ID, presumably defined elsewhere
		      	4-bit	= Unknown, may be unused/buffer space
        - There are a variable number of frames, defined by Frame Count

Frame Data
	16-bit		= Frame Count
	16-bit x num	= Offsets for specific frames, added to Sprite Data address
	Sprite
		8-bit	= Tile Collection Count
		8-bit	= Unknown, but flag 0x08 does something

		Tile Collection
		2-bit	= Orientation
			0x0 = Orientation 0 (Even)
			0x4 = Orientation 1 (Horizontal)
			0x8 = Orientation 2 (Vertical)
			0xC = Invalid? Single Tile only
		2-bit	= ???
0x1 = Unknown
0x2 = Grabs tiles from RAM
		12-bit	= Y Coordinate

		2-bit	= Size
			0x0 = Size 0 (N/A)
			0x4 = Size 1 (x2 primary, x1 secondary)
			0x8 = Size 2 (x4 primary, x2 secondary)
			0xC = Size 3 (x8 primary, x4 secondary)
		2-bit	= Flipping
			0x1 = Horizontal Flip
			0x2 = Vertical Flip
		12-bit	= X Coordinate

		16-bit	= Tile Offset/Increment (i.e. “start from this tile”)
General notes: 
- Tiles exist at fixed points within sprite/tile sheet, likely bit aligned
- The “Shape” value formats the sprite depending on what is set for Orientation; with no 
  horizontal/vertical emphasis (“Orientation” bits unset/0x00), it is an even 64x64
- The RAM tile address is dynamic, but in the Monster Compendium, seems to begin at 0x06015000; it 
  is unknown which sprites, if any, use this feature

??? Data
	32-bit		= Unknown (Hero has it as 0x00000004)
	32-bit		= Unknown (Hero has it as 0x00000010)

TODO (continued):
- Getters and setters are not going to work the same way here they can for static structs (e.g. 
  monsters, items), but having more of these the kinds of functions like those used for the palette 
  data would be an asset.
- Try to identify unknown variables, including the purpose of the unknown data bank (the third of 
  five sections).
"""

import globals

class CharSprite:
    def __init__(self, base_table_addr, charsprite_address, sprite_num):
        # Other data type managers have static data sizes while sprites are variable and have multiple sections, so I 
        # will have to figure out a better solution here
        # self.bytes_ = sprite_data             
        # self.original_bytes = sprite_data

        # Despite being stored in sprite table rather than sprite header, it's more efficient to  store the calculated 
        # absolute address here for easy reference
        self.sprite_header = charsprite_address     
        
        # This gets set in the SpriteManager after the sprite is created, since it's stored in the sprite table rather 
        # than the sprite's header; its name is retained from when I thought it was something else
        self.is_visible = None                  

        # The first sprite index has an absurdly high offset compared to everything else; it is very unlikely to be a 
        # sprite, though what it is, I do not know
        if sprite_num == 0:
            return
        
        # Raw offsets from the sprite header; more useful to keep within Sprite instances because, eventually, we will 
        # want to be able to update these directly
        self.animation_data_offset = int.from_bytes(
            globals.my_file[charsprite_address:charsprite_address + 0x04], 
            'little'
            )
        self.frame_data_offset = int.from_bytes(
            globals.my_file[charsprite_address + 
                            0x04:charsprite_address + 0x08], 
            'little'
            )
        self.unknown_data_offset = int.from_bytes(
            globals.my_file[charsprite_address + 
                            0x08:charsprite_address + 0x0C], 
            'little'
            )
        self.pixel_data_offset = int.from_bytes(
            globals.my_file[charsprite_address + 
                            0x0C:charsprite_address + 0x10], 
            'little'
            )
        self.palette_data_offset = int.from_bytes(
            globals.my_file[charsprite_address + 
                            0x10:charsprite_address + 0x14], 
            'little'
            )
    
        # Section header addresses
        self.animation_data_header = base_table_addr + self.animation_data_offset
        self.frame_data_header = base_table_addr + self.frame_data_offset
        self.unknown_data_header = base_table_addr + self.unknown_data_offset
        self.pixel_data_header = base_table_addr + self.pixel_data_offset
        self.palette_data_header = base_table_addr + self.palette_data_offset

        # Possibly four unknown variables exist between the offsets and the animation slots; uncertain how many; 
        # unknown_var4 is likely unused, but I am uncertain
        self.unknown_var1 = globals.my_file[charsprite_address + 0x14]
        self.unknown_var2 = globals.my_file[charsprite_address + 0x15]
        self.unknown_var3 = globals.my_file[charsprite_address + 0x16]
        self.unknown_var4 = globals.my_file[charsprite_address + 0x17]
        
        # Grab animation slots and fill an array to hold all of the corresponding IDs
        self.anim_slot_total = int.from_bytes(
            globals.my_file[charsprite_address + 0x18:charsprite_address + 0x1A], 
            'little'
            )
        self.anim_slot_array = []

        for i in range(self.anim_slot_total):
            slot_offset = charsprite_address + 0x1A + (i * 0x02)
            slot_value = int.from_bytes(
                globals.my_file[slot_offset:slot_offset + 0x02], 
                'little'
                )
            self.anim_slot_array.append(slot_value)

        # Retrieve palette length and get palette address, including an unmodified copy of the palette, to two arrays
        self.palette_length = int.from_bytes(
            globals.my_file[self.palette_data_header:self.palette_data_header + 0x04], 
            'little'
            ) // 2

        if self.palette_length > 0:
            self.palette_address = self.palette_data_header + 0x04
        else:
            self.palette_address = None
        
        self.palette_rgb = self.load_initial_palette()

        # Load pixel data
        self.pixel_data_length = int.from_bytes(
            globals.my_file[self.pixel_data_header:self.pixel_data_header + 0x02], 
            'little'
            )
        self.pixel_unknown_var1 = int.from_bytes(
            globals.my_file[self.pixel_data_header + 0x02:self.pixel_data_header + 0x04], 
            'little'
            )
        self.pixel_data = int.from_bytes(
            globals.my_file[self.pixel_data_header + 0x04:self.pixel_data_header + self.pixel_data_length], 
            'little')

    # Get palette data as RGB tuples
    def load_initial_palette(self):
        """Load palette from ROM only on sprite object creation."""
        if self.palette_address is None:
            return None
        
        return globals.my_paletteman.load_palette_from_address(
            self.palette_address, 
            self.palette_length
        )
    
    def get_palette(self):
        """Load current palette, if one has previously been loaded."""
        return self.palette_rgb.copy() if self.palette_rgb else None
    
    # Save palette data from RGB tuples
    def set_palette(self, palette_rgb):
        """Save palette data from RGB tuples."""
        self.palette_rgb = palette_rgb.copy()