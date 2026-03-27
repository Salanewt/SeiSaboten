"""
This widget is responsible for displaying a palette from hex and providing a basic interface for 
editing colours, one at a time.

Contains:
class PaletteGridModel              Handles how the palette table/grid is defined

class PaletteManager
  load_palette_from_address         Loads a palette from a supplied address for x colours
  save_palette_to_address           Stores x colours of a palette to a supplied address

class PaletteGridDelegate           Used to override PyQt's table selection highlight  behaviour
  paint                             Applies style/bg colour to selected cell

PaletteEditor                       Defines the shape and functionality of the palette editor
  get_current_palette
  set_palette_data
  on_palette_selected
  update_colour_preview
  apply_colour_to_selected          
  refresh_display                   
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

import globals

class PaletteGridModel(QtCore.QAbstractTableModel):
    """This class is what governs the shape and style of the palette grid."""
    def __init__(self, *args, palette_rgb=None, **kwargs):
        super(PaletteGridModel, self).__init__(*args, **kwargs)
        self.palette_rgb = palette_rgb or []
        self.cols = 16  # Number of columns in the grid
    
    def rowCount(self, index):
        if not self.palette_rgb:
            return 0
        # Return number of rows needed to display all colours
        return (len(self.palette_rgb) + self.cols - 1) // self.cols
    
    def columnCount(self, index):
        return self.cols
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        # Calculate flat index from grid coordinates
        flat_idx = index.row() * self.cols + index.column()
        
        if flat_idx >= len(self.palette_rgb):
            return None

        r, g, b = self.palette_rgb[flat_idx]

        # Scale 5-bit to other formats for tooltip
        r8, g8, b8 = min(248, r * 8), min(248, g * 8), min(248, b * 8)
        rgbH = (r | (g << 5 )| (b << 10))
        rgbHTML = ((r8 << 0x10) | (g8 << 0x08) | b8)

        if role == Qt.ItemDataRole.BackgroundRole:
            return QtGui.QColor(r8, g8, b8)

        if role == Qt.ItemDataRole.ToolTipRole:
            return (f"Index: {flat_idx}\n" + 
                    "GBA: ({r}, {g}, {b})\n" + 
                    "RGB: ({r8}, {g8}, {b8})\n" + 
                    "15-bit: 0x{rgbH:03X}\nHTML: #{rgbHTML:06X}"
                    )

        if role == Qt.ItemDataRole.DisplayRole:
            return ""  # No text inside the swatch

        return None
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            flat_idx = index.row() * self.cols + index.column()
            if flat_idx < len(self.palette_rgb):
                try:
                    r, g, b = value
                    if 0 <= r <= 31 and 0 <= g <= 31 and 0 <= b <= 31:
                        self.palette_rgb[flat_idx] = (r, g, b)
                        self.dataChanged.emit(index, index)
                        return True
                except (TypeError, ValueError):
                    pass
        return False
    
    def headerData(self, col, orientation, role):
        return None
    
    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class PaletteManager:
    """This class is responsible for loading and saving palettes from/to a given address."""
    def load_palette_from_address(self, address, num_colours):
        """Read num_colours 16-bit GBA colours from address, convert to RGB tuples"""
        palette_rgb = []
        for i in range(num_colours):
            colour_offset = address + (i * 0x02)
            colour_val = int.from_bytes(
                globals.my_file[colour_offset:colour_offset + 0x02], 
                'little'
                )
            
            # Convert GBA 5-5-5 to RGB tuples
            r, g, b = (colour_val >> 0) & 0x1F, (colour_val >> 5) & 0x1F, (colour_val >> 10) & 0x1F
            palette_rgb.append((r, g, b))
        
        return palette_rgb
    
    def save_palette_to_address(self, address, palette_rgb, num_colours):
        """Convert RGB tuples to GBA 16-bit colours and save."""
        for i in range(min(num_colours, len(palette_rgb))):
            r, g, b = palette_rgb[i]
            colour_val = (r & 0x1F) | ((g & 0x1F) << 5) | ((b & 0x1F) << 10)
            colour_offset = address + (i * 0x02)
            globals.my_file[colour_offset:colour_offset + 0x02] = colour_val.to_bytes(2, 'little')
        return True

class PaletteGridDelegate(QtWidgets.QStyledItemDelegate):
    """This class allows the selected cell to retain its base colour when selected."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
    
    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
            # Get the color from the model
            color_data = index.data(Qt.ItemDataRole.BackgroundRole)
            if color_data:
                # Save the painter state
                painter.save()
                
                # Fill the background with the actual color
                painter.fillRect(option.rect, color_data)
                
                # Draw a white border around selected items
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white, 2))
                painter.drawRect(option.rect.adjusted(1, 1, -2, -2))
                
                # Restore painter state
                painter.restore()
            else:
                # Fall back to default painting
                super().paint(painter, option, index)
        else:
            # Not selected - use default painting (which will show the color)
            super().paint(painter, option, index)

class PaletteEditor(QtWidgets.QWidget):
    """
    This class defines the actual editor widget itself, including its methods for loading and 
    manipulating palette data.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_address = None
        self.current_num_colours = 0
        self.palette_manager = PaletteManager()
        
        # Main vertical layout - grid on top, editor below
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)
        
        # Top: Palette Grid
        self.palette_model = PaletteGridModel()
        self.palette_view = QtWidgets.QTableView()
        self.palette_view.setModel(self.palette_model)

        # Add selection outline
        self.delegate = PaletteGridDelegate(self)
        self.palette_view.setItemDelegate(self.delegate)
        
        # How large each square in the colour grid should be
        self.cell_size = 25

        # Configure the grid to override QT's minimum column/row dimensions
        header = self.palette_view.horizontalHeader()
        header.setMinimumSectionSize(1)
        header.setDefaultSectionSize(self.cell_size)
        header.setMaximumSectionSize(self.cell_size)
        
        vheader = self.palette_view.verticalHeader()
        vheader.setMinimumSectionSize(1)
        vheader.setDefaultSectionSize(self.cell_size)
        vheader.setMaximumSectionSize(self.cell_size)
        
        # Disable stretching
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        vheader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        # Format the grid to look like swatches
        self.palette_view.horizontalHeader().setVisible(False)
        self.palette_view.verticalHeader().setVisible(False)
        
        # Set fixed cell sizes
        for i in range(16):
            self.palette_view.setColumnWidth(i, self.cell_size)
            self.palette_view.setRowHeight(i, self.cell_size)
        
        # Set grid selection behaviour
        self.palette_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )
        self.palette_view.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems
            )

        # Set grid dimensions
        self.palette_view.setFixedWidth(self.cell_size * 16 + 2)
        self.palette_view.setFixedHeight(max(100, self.current_num_colours * self.cell_size + 102))
        
        # Add grid and align it in the centre of the widget
        main_layout.addWidget(self.palette_view, alignment=Qt.AlignmentFlag.AlignCenter)  
        
        # Bottom: Colour editor controls
        editor_group = QtWidgets.QGroupBox("Edit Selected Colour")
        editor_layout = QtWidgets.QFormLayout(editor_group)
        
        self.colour_preview = QtWidgets.QLabel()
        self.colour_preview.setFixedSize(50, 50)
        self.colour_preview.setStyleSheet("background-color: black; border: 2px solid gray;")
        editor_layout.addRow("Preview:", self.colour_preview)
        
        self.index_label = QtWidgets.QLabel("None")
        editor_layout.addRow("Index:", self.index_label)
        
        # RGB colour spinners
        self.red_spin = QtWidgets.QSpinBox()
        self.red_spin.setRange(0, 31)
        self.red_spin.valueChanged.connect(self.update_colour_preview)
        editor_layout.addRow("Red (0-31):", self.red_spin)
        
        self.green_spin = QtWidgets.QSpinBox()
        self.green_spin.setRange(0, 31)
        self.green_spin.valueChanged.connect(self.update_colour_preview)
        editor_layout.addRow("Green (0-31):", self.green_spin)
        
        self.blue_spin = QtWidgets.QSpinBox()
        self.blue_spin.setRange(0, 31)
        self.blue_spin.valueChanged.connect(self.update_colour_preview)
        editor_layout.addRow("Blue (0-31):", self.blue_spin)
        
        # Apply change button
        self.apply_btn = QtWidgets.QPushButton("Apply to Selected")
        self.apply_btn.clicked.connect(self.apply_colour_to_selected)
        editor_layout.addRow(self.apply_btn)
        
        main_layout.addWidget(editor_group)
        
        # Connect selection change
        self.palette_view.selectionModel().selectionChanged.connect(self.on_palette_selected)
    
    def get_current_palette(self):
        """Return the current palette data."""
        if hasattr(self, 'palette_model') and self.palette_model:
            return self.palette_model.palette_rgb.copy()
        return None

    def set_palette_data(self, address, num_colours, palette_rgb):
        """Set palette data from RGB tuples."""
        self.current_address = address
        self.current_num_colours = num_colours
        self.palette_model.palette_rgb = palette_rgb.copy()
        self.palette_model.layoutChanged.emit()

        # Update the grid display
        self.refresh_display()
    
    def on_palette_selected(self, selected, deselected):
        """Load selected colour into editor."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            flat_idx = index.row() * 16 + index.column()
            
            if flat_idx < len(self.palette_model.palette_rgb):
                r, g, b = self.palette_model.palette_rgb[flat_idx]
                self.red_spin.setValue(r)
                self.green_spin.setValue(g)
                self.blue_spin.setValue(b)
                self.index_label.setText(str(flat_idx))
                self.update_colour_preview()
    
    def update_colour_preview(self):
        """Update the colour preview."""
        r, g, b = self.red_spin.value(), self.green_spin.value(), self.blue_spin.value()
        # Scale 5-bit to 8-bit for display
        # r8, g8, b8 = (r << 3 | r >> 2), (g << 3 | g >> 2), (b << 3 | b >> 2)
        r8, g8, b8 = r * 8, g * 8, b * 8
        self.colour_preview.setStyleSheet(
            f"background-color: rgb({r8}, {g8}, {b8}); border: 2px solid gray;"
            )
    
    def apply_colour_to_selected(self):
        """Apply edited colour to selected palette entry."""
        indexes = self.palette_view.selectionModel().selectedIndexes()
        if not indexes:
            return
            
        index = indexes[0]  # Single selection mode
        flat_idx = index.row() * 16 + index.column()
        
        if flat_idx < len(self.palette_model.palette_rgb):
            r, g, b = self.red_spin.value(), self.green_spin.value(), self.blue_spin.value()
            self.palette_model.palette_rgb[flat_idx] = (r, g, b)
            
            # Refresh just this cell
            self.palette_model.dataChanged.emit(index, index)
    
    def refresh_display(self):
        """Force the palette grid to refresh its display."""
        if hasattr(self, 'palette_model') and self.palette_model:
            self.palette_model.layoutChanged.emit()