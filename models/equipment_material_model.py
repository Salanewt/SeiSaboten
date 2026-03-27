"""
TODO:
- Implementation.
- Further research on unknowns.

General notes:
- This information should ideally be presented as if it were part of Item data, since there is so 
  little of it and materials are defined by name/sprite in there.
  - I may look into a patching option that combines the two tables together.
- This model should also be accessible through the Weapon, Armour, and possibly Shop tabs.
  - Could possibly make this into a widget that can be loaded as needed; unsure if necessary.
"""

class EquipmentMaterial:
    def __init__(self):
        pass
    
    # 0xE3532C - Only four bytes each, immediately preceding item data

      # If viewed as a 32-bit word:
      #   0b1111 1111 0000 0000 0000 0000 0000 0000 = Unused?
      #   0b0000 0000 1111 0000 0000 0000 0000 0000 = Element
          # 0x0 = NOT (None)
          # 0x1 = Wisp
          # 0x2 = Shade
          # 0x3 = Luna
          # 0x4 = Salamander
          # 0x5 = Undine
          # 0x6 = Dryad
          # 0x7 = Jinn
          # 0x8 = Gnome
          # 0x9 = ALL
          # Note: Element is overridden to NOT if Elemental Power/Defence = 0
      #   0b0000 0000 0000 1111 1000 0000 0000 0000 = Armour Effect
      #   0b0000 0000 0000 0000 0111 1100 0000 0000 = Weapon Effect
      #   0b0000 0000 0000 0000 0000 0011 1111 1111 = Unknown