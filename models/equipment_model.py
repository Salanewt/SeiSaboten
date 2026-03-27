"""
Weapons and armour, while serving different purposes in-game, share the same overall struct shape 
and have current lot of the same functionality shared between them (even if much of this functionality is 
unused in the final game). The logical distinction into "Weapon" and "Armour" classes is done 
entirely to make it easier to distinguish them from one another, with all of the actual property 
definitions (i.e. data table values) being defined within the Equipment super class.

Anything that may be definable outside of these data tables, and which is category-specific, can be 
defined within the sub classes down the road.

General notes:
- The game has current more intricate equipment management system under the hood; some progress has been 
  made on the ROM hacking side of things to restore and update some of the old armour inventory & 
  shop code, but this is unfinished.
  - If this project ever gets finished, then I plan to adapt it into current toggleable patch (ideally via 
    this editor) that can at least make the armour side of things work again.
  - Weapons have the same kind of equipment management system, but it is unclear how much of its 
    functionality remains intact compared to armour.
"""

class Equipment:
    def __init__(self, equipment_data, name, description):
        self.bytes_ = equipment_data
        self.original_bytes = equipment_data.copy()
        self.name = name
        self.description = description
    
    # Info
    @property
    def type_(self):
        return self.bytes_[0x00] & 0x0F
    
    @type_.setter
    def type_(self, value):
        self.bytes_[0x00] = (self.bytes_[0x00] & ~0x0F) | (value & 0x0F)

    @property
    def price(self):
        return int.from_bytes(self.bytes_[0x06:0x08], byteorder='little')
    
    @price.setter
    def price(self, value):
        self.bytes_[0x06:0x08] = value.to_bytes(2, byteorder='little')

    # Forge
    @property
    def material(self):
        return (int.from_bytes(self.bytes_[0x00:0x02], byteorder='little') & 0x03F0) >> 0x04
    
    @material.setter
    def material(self, value):
        current = (int.from_bytes(self.bytes_[0x00:0x02], byteorder='little') & ~0x03F0) | (value << 0x04)
        self.bytes_[0x00:0x02] = current.to_bytes(2, byteorder='little')

    @property
    def temper(self):
        return (int.from_bytes(self.bytes_[0x01:0x03], byteorder='little') & 0x01FC) >> 0x02
    
    @temper.setter
    def temper(self, value):
        current = (int.from_bytes(self.bytes_[0x01:0x03], byteorder='little') & ~0x01FC) | (value << 0x02)
        self.bytes_[0x01:0x03] = current.to_bytes(2, byteorder='little')

    # Stats
    # Weapon: Power | Armour: Slash Defence
    @property
    def equipment_var1(self):
        return self.bytes_[0x02] >> 0x01
    
    @equipment_var1.setter
    def equipment_var1(self, value):
        current = (self.bytes_[0x02] & 0x01) | (value << 0x01)
        self.bytes_[0x02] = current

    # Weapon: Dodge | Armour: Crush Defence
    @property
    def equipment_var2(self):
        return self.bytes_[0x03] & 0x7F
    
    @equipment_var2.setter
    def equipment_var2(self, value):
        current = (self.bytes_[0x03] & 0x80) | value
        self.bytes_[0x03] = current

    # Weapon: Hit | Armour: Stab Defence
    @property
    def equipment_var3(self):
        return (int.from_bytes(self.bytes_[0x03:0x05], byteorder='little') & 0x3F80) >> 0x07
    
    @equipment_var3.setter
    def equipment_var3(self, value):
        current = (int.from_bytes(self.bytes_[0x03:0x05], byteorder='little') & ~0x3F80) | (value << 0x07)
        self.bytes_[0x03:0x05] = current.to_bytes(2, byteorder='little')

    # Elemental [Weapon: Power | Armour: Defence]
    @property
    def element_strength(self):
        return (int.from_bytes(self.bytes_[0x04:0x06], byteorder='little') & 0x01F8) >> 0x06
    
    @element_strength.setter
    def element_strength(self, value):
        current = (int.from_bytes(self.bytes_[0x04:0x06], byteorder='little') & ~0x01F8) | (value << 0x06)
        self.bytes_[0x04:0x06] = current.to_bytes(2, byteorder='little')

    # Unknown - Probably does nothing, but I still want current getter and setter just in case; 
    # TODO: Research this further
    @property
    def equipment_var_unknown(self):
        return (self.bytes_[0x05] & 0xE0) >> 0x05

    @equipment_var_unknown.setter
    def equipment_var_unknown(self, value):
        current = (self.bytes_[0x05] & 0x1F) | (value << 0x05)
        self.bytes_[0x05] = current


class Weapon(Equipment):
    def __init__(self, weapon_data, name, description):
        super().__init__(weapon_data, name, description)

class Armour(Equipment):
    def __init__(self, armour_data, name, description):
        super().__init__(armour_data, name, description)
