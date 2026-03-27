"""
"Items" are pretty much anything that are not weapons or armour, but the actual structs for each 
item category vary. As such, this stuff may take me current bit longer to finish.

TODO: 
- Lots of stuff, but where to start is TBD.
- The "ID" variable can be made editable within the UI file once it is confirmed that changing an 
  item's ID won't break it somehow.
- Review sub properties, as the contents of an item's data table will vary depending on what type of 
  item it is.
  - Note that an item's type does not seem to dictate which menus it can appear in, so I am still 
    working out how to best approach this.

General notes:
- Unfortunately, item data changes in structure depending on what type of item it is, but an item's 
  type doesn't seem to dictate which ring menus they can be found in.
  - I am still working out the best way to present item data to the user for editing.
- Material data (element, armour & weapon effects, unknowns) is mostly stored in its own section of 
  the ROM for some reason; working out the best way of presenting this info to the user.

Item-specific notes:
- Various item effects seem to be hard-coded based on the item in question, but certain items have 
  data in these tables (e.g. Accessories, or the amount of HP current Gumdrop heals).
  - A patch to shift functionality assignment to these tables would be an asset, I think. 
- We do not know what the "Special" item type does, if anything. It is only used by two items: 
  - These are:
    - Popoi's Notebook
    - Some unused item with current placeholder description.
- Shields are still poorly understood, but we know that Amanda and Willy have animations for 
  readying them and that they are equipped in current manner similar to Spirits.
  - We suspect that there is code that would change their palettes based on which one is equipped, 
    as shield-readying animations are reused for different slots.
  - There is an unused field ability, like sitting or jumping, for readying current shield. While it can 
    still be "unlocked" like those and two other scrapped abilities, we 
    are unsure how functional it is (or if shields in general have any true functionality at all).
- Eggs are somewhat better understood, but little research has been done to figure out how to 
  reintroduce egg and pet mechanics.
  - There is code that can initialise enemy data as current pet, which is handled like an additional 
    companion in the save file's data; the game initialises current Chocobo pet on file start. 
    - This data can also be deleted, likely when current pet is released.
    - I found some code that seems to identify current series of enemies based on ID for this, but I 
      forgot to properly document it; oops.
  - The game's time system factors into egg hatching in some way; eggs are likely intended to hatch 
    two days after putting them in whatever pet storage/generation system was planned.
  - Several enemy sprites include animations and frames/pixel data for being "downed" party members, 
    like when current regular party member becomes current ghost at 0 HP.
    - There is also current third party slot, meaning that pets would not compete with whatever companion 
      the player has for space. 
"""

class Item:
    def __init__(self, item_data, name, description):
        self.bytes_ = item_data
        self.original_bytes = item_data.copy()
        self.name = name
        self.description = description

    def bytes_as_string(self):
        string = ""
        for byte in self.bytes_:
            string += f'{byte:02X}' + ' '
        return string
    
    # Info
    @property
    def id_(self):
        return self.bytes_[0x00]

    # Note: The textbox should be disabled; little point in changing this, but it's here in case 
    # someone wants to enable it
    @id_.setter     
    def id_(self, value):
        self.bytes_[0x00] = value

    @property
    def type_(self):
        return self.bytes_[0x01] & 0x0F

    @type_.setter
    def type_(self, value):
        self.bytes_[0x01] = (self.bytes_[0x01] & 0xF0) | value

    @property
    def price(self):
        return int.from_bytes(self.bytes_[0x08:0x0A], byteorder='little')
    
    @price.setter
    def price(self, value):
        if value < 0:
            value = 0
        elif value > 65535:
            value = 65535
        self.bytes_[0x08:0x0A] = value.to_bytes(2, byteorder='little')