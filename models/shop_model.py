"""
All shops are constructed the same way and have the same number of slots, even if a particular shop 
might not sell certain kinds of items.

Almost surprisingly, there is no bit-packing here (that we have been able to find, at least).
"""

class Shop:
    def __init__(self, shop_data):
        """
        Shop stocks are just halfword arrays of item/weapon/armour IDs, with what the ID corresponds 
        to depending on the chosen item's index.
        """
        self.bytes_ = shop_data
        self.original_bytes_ = shop_data.copy()

        # To store individual item IDs, to be translated by manager or view
        self.shop_stock = []

    def get_stock(self, index):
        """
        Just gets the item's ID; the manager is responsible for translating that to its 
        corresponding item (three different data tables to draw from).
        """
        return int.from_bytes(self.bytes_[index * 2: index * 2 + 2], byteorder='little')
    
    def set_stock(self, index, value):
        """Sets the item ID in the correct spot."""
        if index * 2 + 1 < len(self.bytes_):
            self.bytes_[index * 2:index * 2 + 2] = value.to_bytes(2, byteorder='little')
    
    def update_bytes_from_stock(self):
        """Update the bytes_ array from the shop_stock list."""
        for i, stock_id in enumerate(self.shop_stock):
            if i < len(self.bytes_) // 2:
                self.set_stock(i, stock_id)