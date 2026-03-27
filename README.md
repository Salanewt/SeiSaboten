# SeiSaboten 😇🌵

A ROM editor for the GBA game Sword of Mana/新約 聖剣伝説.

As of v0.1 (new versioning criteria), this tool can edit:
- Monster data (mostly)
- Item data (partially)
- Weapon data
  - Except for one possibly unused variable and/or buffer space, but the getter/setter for it is 
    implemented; functionality can be incorporated pending further research
- Armour data
  - Same
- Shop data
- Sprite data (partially - palettes)

I have also disabled:
- Randomiser stuff, because I am in the process of reorganising the code and cleaning things up
  a bit, and this is lower priority for me until more functionality has been implemented. Most of
  the original code is still intact, albeit in different files.

Only supports editing the Japanese version and the NA version at the moment, and JP support is
behind the NA version. The European versions (the 3 of them!) are not currently supported.


Notes from the original Readme, including new screenshots:

Dialog can be exported to JSON, in order to edit in an external program. It can then be imported back.

Lots of reverse engineering of the game was needed to accomplish this, and without [No$GBA](https://www.nogba.com/) this wouldn't have been possible - a big thank you to that!

To handle the Japanese text, each of the 1247 kanji in the game had to be documented individually...! I didn't trust OCR with something like this, due to the low pixel density. Some kanji were hard to deduce (they were viewed all together, not in context) - so they were skipped. View the 'kanji_table.xlsx' file in the 'kanji' folder in the repo to see which kanji are missing. Screenshots of each kanji are included in case anyone wants to fill in the missing ones before I get around to it myself! Again, check the 'kanji' folder.

Text Editing:

![Text Editing](https://jtm.gg/files/dudbear-message3x.png)

Palette Editing:

![Palette_Editing](https://www.dropbox.com/scl/fi/lbscw1sld8rdpit2u6f0s/Sword_of_Mana_Heroine_Palette.png?rlkey=b074qihih1awizv1gff59dmqs&st=udll1ck3&dl=0)

SeiSaboten GUI 1:

![Editor GUI_Monsters](https://www.dropbox.com/scl/fi/p3zct8glujxugqfambe15/SeiSaboten_monsters.png?rlkey=3mfflxcby8kk0wlvm9hta540i&st=eu16qb49&dl=0)

SeiSaboten GUI 2:

![Editor GUI_Shops](https://www.dropbox.com/scl/fi/hihjgj6gkggeig7hvi54q/SeiSaboten_itemsShop.png?rlkey=bri2pu3xy28tl87lgbvp8h9a2&st=v2aidqfs&dl=0)

SeiSaboten GUI 3:

![Editor GUI_Sprites](https://www.dropbox.com/scl/fi/m10wyzpkma5f1kf06ggsg/SeiSaboten_spritePalette.png?rlkey=vpmn06crm48pydxaw53m4m0xu&st=69evtsrd&dl=0)

Edit of Rabite:

![Monster Editing](https://jtm.gg/files/rabite_edit3x.png)

Replacing Rabites with Chocobos:

![Encounter Editing](https://jtm.gg/files/chocobo3x.png)
