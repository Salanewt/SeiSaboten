"""
For anyone who may want to build on this repo in the future: A view interacts with the 
controller/manager file, which in turn interacts with the model and ROM. It helps define the 
interface the user will experience. A view isn't normally supposed to 

Input validation is generally handled in three ways:
  1. Invalid data types (i.e. strings/chars/floats) are simply ignored and the old data is retained
     - Note: This should be done for each relevant value within each view
  2. Any valid data value (i.e. whole number) that falls outside of the value's valid range is 
     clamped by calling the clamp() method
     - Example: Monster HP is capped at 8,191; trying to set it to 9,000 will store 8,191 instead

Note: I used to also clamp data ranges within the setters, but this felt redundant and 
bloated the code somewhat; this can be reimplemented if it proves to be an issue later.


I want to say that I was able to fully set these up on my own, but I leaned a bit on GenAI to 
improve my subclasses (especially with the use of mappers and lambda) and make them more readable. 
On the plus side, I now have a better understanding of how to handle my views going forward.
"""

class BaseView:
    """
    Following MVC design, this is the base view. Any functionality that should be universal to all 
    views is set up here (not that there is much of that).
    """
    def __init__(self, main_window):
        """Initialise view/UI."""
        self.main_window = main_window 
        pass
    
    def setup_connections(self):
        """This sets up ignal/slot connections to facilitate live updates."""
        pass
    
    def init_after_rom(self):
        """Called after ROM is loaded to initialize view with ROM data."""
        pass
    
    def store_current_data(self):
        """Store any unsaved data from UI back to models."""
        pass

    def clamp(self, value, limit):
        """Clamp a value between a minimum (0) and maximum (defined) limit."""
        return max(0, min(value, limit))