"""
A tile is an x-by-x collection of pixels, which can be stored as an array. This model is designed so 
that tiles of variable sizes can be made by passing the value of x as an argument on creation, but 
in practice for GBA games, you're typically looking at 8x8 tiles that can be assembled into larger 
tile collections. There are exceptions to this, as some games have graphics where tiles are larger 
(e.g. Golden Sun has summon graphics that are made up of collections of 32x32 sprite tiles).

This model has applications for sprite and map/tilesheet design.

Notes:
- Tiles should be loaded into an image viewer/editor widget (that I haven't made yet).
- Tile sheets can be assembled with tiles using set dimensions (TODO: Make a tilesheet model).

TODO:
- MAYBE: Make some basic functions that make tiles with preset sizes (e.g. a make_8x8_tile function 
  that calls make_tile(8) or something).
- I could also make Tile into a super class, with different kinds of tile classes as base classes; 
  the only problem is that I don't yet know if SoM would benefit from that or not. Maybe other 
  games, if I ever reuse this file elsewhere.
"""
class Tile:
    def __init__(self, dimension):
        self.dimension = dimension
        self.tile_size = dimension * dimension
        self.tile = [0] * self.tile_size
        self.tile_original = self.tile.copy()

    def make_tile(self, data):
        """
        This creates a tile with the data that is passed to it, packing only enough data to fit the 
        tile.
        """
        for i in range(min(len(data), self.tile_size)):
            self.tile[i] = data[i]
        return self.tile

    def copy_tile(self, source_tile):
        """
        This creates a copy of a pre-existing tile as a wholly new tile.
        """
        new_tile = Tile(self.dimension)
        for i in len(source_tile):
            new_tile.tile[i] = source_tile.tile[i]
        return new_tile
    
    def replace_tile(self, new_tile_data):
        """
        This replaces the data contained within a pre-existing tile with new data.
        """
        self.tile = [0] * self.tile_size
        for i in range(min(len(new_tile_data), self.tile_size)):
            self.tile[i] = new_tile_data[i]

    def make_super_tile(tiles):
        """
        This makes a tile that is four times (2x2) the size of a base tile, using the four base 
        tiles passed to it.

        TODO: Implementation.
        """
        pass
