locations = {
    'J':
        {
            'story_text_location': '3EC0',
            'real_master_table_location': '65E8',
            'charmap_start': 'E341EE',
            'enemy_data': 'DFA0F0',
            'encounter_data': 'DF6018',
            'monster_book_pointer': '82F48'

        },
    'E':
        {
            'story_text_location': '3EB0',
            'real_master_table_location': '65D8',   # address contains the address
            'monster_book_pointer': '8302C',

            'charsprite_tables': '77154C',               # Starting with offsets, one for each "sprite" (e.g. Hero, Heroine, Rabite, etc.)

            'material_data': 'E3532C',              # The items that are used to forge equipment, including their stats and effects
            'shop_data': 'E353DC',                  # Basically just a series of item/ID lists, including consumables, weapons, armour, and accessories as separate sections
            'item_data': 'E35FF8',                  # All item data starts here; each item is the same length, regardless of type, but the actual item struct varies based on type
            'encounter_data': 'E3D4D8',             # Presumably, which enemies can appear in which maps (Salanewt's note: I haven't looked into it for myself yet)
            'weapon_data': 'E3FB48',                # Unlike item data, weapon data is consistent, at least
            'armour_data': 'E3FFE0',                # Same goes for armours; not using the US spelling for this one LOL
            'enemy_data': 'E415B0',                 # Exactly what it says on the tin
            'charmap_start': 'E7BB62',              # Area in rom that contains codes for common letters

        }
}