"""
Monsters include everthing you can fight, including bosses and some kinds of obstacles.

Note: Bits are heavily packed in these tables, so there is a lot of shifting and masking going on
      in here. 

TODO: 
- 26-03-26: I have revised all getters/setters for things displayed in the UI, ending at the 
  Event ID getter. I will eventually resume working on those when the time comes to add more stuff 
  to the editor, but it almost feels pointless before then.
"""

class Monster:
    def __init__(self, enemy_data, name, in_book):
        self.bytes_ = enemy_data
        self.original_bytes = enemy_data
        self.name = name
        self.in_book = in_book

    def bytes_as_string(self):
        string = ""
        for byte in self.bytes_:
            string += f'{byte:02X}' + ' '
        return string

    # Info
    @property
    def sprite(self):
        return (int.from_bytes(self.bytes_[0x00:0x02], byteorder='little')) & 0x1FF

    @sprite.setter
    def sprite(self, value):
        current = (int.from_bytes(self.bytes_[0x00:0x02], byteorder='little') & ~0x1FF) | (value & 0x1FF)
        self.bytes_[0x00:0x02] = current.to_bytes(2, byteorder='little')

    @property
    def type_(self):
        return (self.bytes_[0x01] >> 1) & 0x0F

    @type_.setter
    def type_(self, value):
        current = (self.bytes_[0x1] & ~0x1E) | (value << 0x01)
        self.bytes_[0x01] = current

    @property
    def ability_prime(self):
        return self.bytes_[0x01] >> 0x05

    @ability_prime.setter
    def ability_prime(self, value):
        current = (self.bytes_[0x1] & ~0xE0) | ((value & 0x7) << 5)
        self.bytes_[0x01] = current

    @property
    def ability_sub(self):
        return self.bytes_[0x02] & 0x07

    @ability_sub.setter
    def ability_sub(self, value):
        current = (self.bytes_[0x2] & ~0x07) | (value & 0x07)
        self.bytes_[0x02] = current


    # Stats
    @property
    def hp(self):
        return (int.from_bytes(self.bytes_[0x07:0x0A], byteorder='little') >> 0x07) & 0x3FFF

    @hp.setter
    def hp(self, value):
        current = (int.from_bytes(self.bytes_[0x07:0x0A], byteorder='little') & ~0x3FFF) | (value << 0x07)
        self.bytes_[0x07:0x0A] = current.to_bytes(3, byteorder='little')
    
    @property
    def pow(self):
        return (int.from_bytes(self.bytes_[0x09:0x0B], byteorder='little') >> 0x05) & 0xFF
    
    @pow.setter
    def pow(self, value):
        current = (int.from_bytes(self.bytes_[0x09:0x0B], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x09:0x0B] = current.to_bytes(2, byteorder='little')

    @property
    def def_(self):
        return (int.from_bytes(self.bytes_[0x0A:0x0C], byteorder='little') >> 0x05) & 0xFF 

    @def_.setter
    def def_(self, value):
        current = (int.from_bytes(self.bytes_[0x0A:0x0C], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x0A:0x0C] = current.to_bytes(2, byteorder='little')

    @property
    def int_(self):
        return (int.from_bytes(self.bytes_[0x0B:0x0D], byteorder='little') >> 0x05) & 0xFF 

    @int_.setter
    def int_(self, value):
        current = (int.from_bytes(self.bytes_[0x0B:0x0D], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x0B:0x0D] = current.to_bytes(2, byteorder='little')

    @property
    def mnd(self):
        return (int.from_bytes(self.bytes_[0x0C:0x0E], byteorder='little') >> 0x05) & 0xFF 

    @mnd.setter
    def mnd(self, value):
        current = (int.from_bytes(self.bytes_[0x0C:0x0E], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x0C:0x0E] = current.to_bytes(2, byteorder='little')

    @property
    def agi(self):
        return (int.from_bytes(self.bytes_[0x0D:0x0F], byteorder='little') >> 0x05) & 0xFF 

    @agi.setter
    def agi(self, value):
        current = (int.from_bytes(self.bytes_[0x0D:0x0F], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x0D:0x0F] = current.to_bytes(2, byteorder='little')


    # Effectiveness
    # Covers Sword, Scythe, Axe, and Sword of Mana
    @property
    def slash(self):
        return (self.bytes_[0x03] >> 0x03) & 0x03

    @slash.setter
    def slash(self, value):
        self.bytes_[0x3] = (self.bytes_[0x03] & ~0x18) | (value << 0x03)

    # Covers Staff, Knucks, Mace     
    @property
    def bash(self):
        return (self.bytes_[0x03] >> 0x05) & 0x03

    @bash.setter
    def bash(self, value):
        self.bytes_[0x03] = (self.bytes_[0x03] & ~0x60) | (value << 0x05)

    # Covers Bow, Flail, Lance
    @property
    def jab(self):
        return (int.from_bytes(self.bytes_[0x03:0x05], byteorder='little') >> 0x07) & 0x03

    @jab.setter
    def jab(self, value):
        current = (int.from_bytes(self.bytes_[0x03:0x05], byteorder='little') & ~0x180) | (value << 0x07)
        self.bytes_[0x03:0x05] = current.to_bytes(2, byteorder='little')

    # Elementals
    @property
    def light(self):
        return (self.bytes_[0x0E] >> 0x05) & 0x03

    @light.setter
    def light(self, value):
        self.bytes_[0x0E] = (self.bytes_[0x0E] & ~0x60) | (value << 0x05)

    @property
    def dark(self):
        return (int.from_bytes(self.bytes_[0x0E:0x10], byteorder='little') >> 0x07) & 0x03

    @dark.setter
    def dark(self, value):
        current = (int.from_bytes(self.bytes_[0x0E:0x10], byteorder='little') & ~0x180) | (value << 0x07)
        self.bytes_[0x0E:0x10] = current.to_bytes(2, byteorder='little')

    @property
    def moon(self):
        return (self.bytes_[0x0F] >> 0x01) & 0x03

    @moon.setter
    def moon(self, value):
        self.bytes_[0x0F] = (self.bytes_[0x0F] & ~0x06) | (value << 0x01)

    @property
    def fire(self):
        return (self.bytes_[0x0F] >> 0x03) & 0x03

    @fire.setter
    def fire(self, value):
        self.bytes_[0x0F] = (self.bytes_[0x0F] & ~0x18) | (value << 0x03)

    @property
    def water(self):
        return (self.bytes_[0x0F] >> 0x05) & 0x03

    @water.setter
    def water(self, value):
        self.bytes_[0x0F] = (self.bytes_[0x0F] & ~0x60) | (value << 0x05)

    @property
    def wood(self):
        return (int.from_bytes(self.bytes_[0x0F:0x11], byteorder='little') >> 0x07) & 0x03

    @wood.setter
    def wood(self, value):
        current = (int.from_bytes(self.bytes_[0x0F:0x11], byteorder='little') & ~0x180) | (value << 0x07)
        self.bytes_[0x0F:0x11] = current.to_bytes(2, byteorder='little')

    @property
    def wind(self):
        return (self.bytes_[0x10] >> 0x01) & 0x03

    @wind.setter
    def wind(self, value):
        self.bytes_[0x10] = (self.bytes_[0x10] & ~0x06) | (value << 0x01)

    @property
    def earth(self):
        return (self.bytes_[0x10] >> 0x03) & 0x03

    @earth.setter
    def earth(self, value):
        self.bytes_[0x10] = (self.bytes_[0x10] & ~0x18) | (value << 0x03)


    # Rewards
    @property
    def exp(self):
        return (int.from_bytes(self.bytes_[0x17:0x19], byteorder='little') >> 0x04) & 0x3FF

    @exp.setter
    def exp(self, value):
        current = (int.from_bytes(self.bytes_[0x17:0x19], byteorder='little') & ~0x3FF0) | (value << 0x04)
        self.bytes_[0x17:0x19] = current.to_bytes(2, byteorder='little')

    @property
    def lucre(self):
        # @080500BE
        return (int.from_bytes(self.bytes_[0x18:0x1A], byteorder='little')) >> 0x06
    
    @lucre.setter
    def lucre(self, value):
        current = (int.from_bytes(self.bytes_[0x18:0x1A], byteorder='little') & ~0xFF80) | (value << 0x06)
        self.bytes_[0x18:0x1A] = current.to_bytes(2, byteorder='little')

    # Trap 
    @property
    def trap(self):
        return self.bytes_[0x1A] & 0x0F
    
    @trap.setter
    def trap(self, value):
        self.bytes_[0x1A] = (self.bytes_[0x1A] & ~0x0F) | (value & 0x0F)

    # Items
    @property
    def item1(self):
        return (int.from_bytes(self.bytes_[0x10:0x12], byteorder='little') >> 0x05) & 0xFF
    
    @item1.setter
    def item1(self, value):
        current = (int.from_bytes(self.bytes_[0x10:0x12], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x10:0x12] = current.to_bytes(2, byteorder='little')

    @property
    def item2(self):
        return (int.from_bytes(self.bytes_[0x11:0x13], byteorder='little') >> 0x05) & 0xFF
    
    @item2.setter
    def item2(self, value):
        current = (int.from_bytes(self.bytes_[0x11:0x13], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x11:0x13] = current.to_bytes(2, byteorder='little')

    @property
    def item3(self):
        return (int.from_bytes(self.bytes_[0x12:0x14], byteorder='little') >> 0x05) & 0xFF

    @item3.setter
    def item3(self, value):
        current = (int.from_bytes(self.bytes_[0x12:0x14], byteorder='little') & ~0x1FE0) | (value << 0x05)
        self.bytes_[0x12:0x14] = current.to_bytes(2, byteorder='little')

    # TODO: Remaining getters/setters, including implementation for all other variables

    # Other
    @property
    def event(self):
        # @080500CE
        current = int.from_bytes(self.bytes_[0x1A:0x1C], byteorder='little')
        return ((current << 0x14) & 0xFFFFFFFF) >> 0x18

    # These properties are unknown to me as well; my documentation groups these two as one unknown 
    # variable, but they seem to be distinct
    @property
    def unknown1(self):
        # reved
        # @080500AE
        current = int.from_bytes(self.bytes_[0x2:0x4], byteorder='little')
        return ((current << 0x15) & 0xFFFFFFFF) >> 0x18

    @property
    def unknown2(self):
        # reved
        # @08023C62
        current = self.bytes_[0x17]
        return ((current << 0x1C) & 0xFFFFFFFF) >> 0x1D

    @property
    def unknown3(self):
        # @0801Fe84
        current = int.from_bytes(self.bytes_[0x4:0x6], byteorder='little')
        return (current << 0x16) & 0xFFFFFFFF

    @property
    def unknown4(self):
        # @0801FEC0
        current = int.from_bytes(self.bytes_[0x4:0x8], byteorder='little')
        return (current << 0x0D) & 0xFFFFFFFF

    # Old comments below:
    # is this speed? I changed to 6 and rabite and bebe seemed a bit slow...?
    # and when a high value, enemies were crazy, flickering back and forth.
    # although I'm not sure I'm setting/getting properly
    @property
    def q1(self):
        # @0805009A
        current = int.from_bytes(self.bytes_[0x16:0x18], byteorder='little')
        return ((current << 0x17) & 0xFFFFFFFF) >> 0x1C

    @q1.setter
    def q1(self, value):
        current = int.from_bytes(self.bytes_[0x16:0x16 + 0x2], byteorder='little')
        current &= ~(self.q1 << 0x1C) >> 0x17
        current |= (value << 0x1C) >> 0x17
        self.bytes_[0x16:0x16 + 0x2] = current.to_bytes(2, byteorder='little')