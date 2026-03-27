"""
# SeiSaboten - A Sword of Mana editor

Overview:
  This is the main file for actually running the project. This editor was originally made with 
  PyQt5, but has been updated to PyQt6; be mindful of that if you try to run this project and get 
  any errors about PyQt5 not being found, etc. A lot of the original code was not commented or 
  commented well enough to explain what was going on, so I have been trying to add comments where I 
  can to explain what I understand about the old code while adding them to mine. Note that I also 
  organised things a little differently; I am trying to implement MVC Design patterns where 
  applicable, and I set up two rulers at line lengths 80 (for docstrings) and 120 (for code).

As of v0.1, this tool can edit:
- Monster data (mostly)
- Item data (partially)
- Weapon data
  - Except for one possibly unused variable and/or buffer space, but the getter/setter for it is 
    implemented; functionality can be incorporated pending further research
- Armour data
  - Same
- Shop data
- Sprite data (partially - palettes)

It can also view:
- Sprite data (partially)
  - Mostly addresses and a few other properties, including a sprite's animation slot list

It has [temporarily] disabled:
- Randomiser stuff

BUG: Editor crash: See textman.py for details.
BUG: Tooltips for certain UI elements will also display for some other elements; not sure why.
BUG: In the charsprite/Sprites table, the last sprite entry doesn't have a palette, yet the editor
     will simply keep the last loaded palette in place when selecting this one. This shouldn't be 
     the case, and I am unsure what would happen if someone tries to save the ROM after having 
     edited it.

TODO: Overall
- Better documentation in general; pretty much every function should have some kind of a docstring 
  that explains what it does and what its different parameters are.
- Continue implementing MVC Design patterns and/or better organisation standards in general.
  - textman.py is of particular concern in this regard.
  
TODO: DoD - v0.2
Required:
- Update all file header docstrings so they contain an itemised list of all included
  functions/methods/classes
  - Various functions and methods should describe parameters/arguments, as well
- Item editing, including materials, has to be fully implemented
  - See the equipment_material_model.py file for my thoughts on this
- More charsprite viewing functionality has to be implemented, including:
  - Pixel/GFX data viewing
  - Frame viewing
  - Animation viewing (in real time)
- Encounter table editing has to be implemented
Hopeful (whatever isn't done for v0.2 will be pushed to v0.3):
- Map viewing functionality
- Party member starting stats editing
- Some randomiser functionality

Salanewt's personal statement:
  I "inherited" this project from its original creator by downloading a forked version off of 
  GitHub, in which another person fixed a couple of bugs; both are credited as contributors.

  This is something of a side project for me, since I'm primarily a Golden Sun hacker who is also a 
  novice programmer, and I figured that continuing an editor for another game I am familiar with 
  would be good practice while not being as overwhelming as starting one from scratch. I am 
  uncertain how much of this I will actually be developing on my own, as I would like to continue to
  focus my efforts on Golden Sun and, potentially, my own games in the future. Still, I am open to 
  providing some minor assistance or answering any questions that I can about the codebase or 
  contents within Sword of Mana itself.

  As an aside, I am not used to seeing games do bit-packing to the extent that SoM does. I am quite 
  confused about how that came to pass while sprites and text are just wholly uncompressed in the 
  ROM. If anyone knows anything about the development of this game and why that might be, I would be 
  interested to hear about it. Or, really, about any kind of development history; it doesn't need to 
  be about that specifically.

  As of March 2026, I can be found on Discord (@Salanewt).

Credits:
- Salanewt: Thank you for checking this out! 
- Joshua Miller - The original SeiSaboten creator: https://jtm.gg
- Subrosian - Reportedly fixed bugs.

Special thanks:
- Fellow Discord user and hacking hobbyist Revier, for contributing to research efforts.

Source of inherited repo: https://github.com/thesubrosian/SeiSaboten/tree/master    
"""

from PyQt6 import QtWidgets

import os
import sys

import mainwindow

# --- Runs the program --- #
if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    window = mainwindow.MainWindow()
    window.show()
    app.exec()