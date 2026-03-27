"""
The functionality for this was originally contained in a tab in the main window, but it made more 
sense to move it into its own widget.
"""

from PyQt6 import QtWidgets
import globals

class StringToBytesWidget(QtWidgets.QWidget):
    """A widget for string to bytes conversion."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("String to Bytes Converter")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Input section
        input_label = QtWidgets.QLabel("Input Text:")
        input_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(input_label)
        
        self.input_text = QtWidgets.QPlainTextEdit()
        self.input_text.setMinimumHeight(100)
        layout.addWidget(self.input_text)
        
        # Convert button
        self.convert_btn = QtWidgets.QPushButton("Convert to Bytes")
        self.convert_btn.setFixedHeight(30)
        layout.addWidget(self.convert_btn)
        
        # Output section
        output_label = QtWidgets.QLabel("Output (Hex):")
        output_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(output_label)
        
        self.output_text = QtWidgets.QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(100)
        layout.addWidget(self.output_text)
        
        # Status bar
        # self.status_label = QtWidgets.QLabel("Ready")
        # self.status_label.setStyleSheet("color: gray;")
        # layout.addWidget(self.status_label)

    def setup_connections(self):
        """Connect signals to slots."""
        self.convert_btn.clicked.connect(self.convert_string_to_bytes)
    
    def convert_string_to_bytes(self):
        """
        Converts strings into bytes.

        This was originally in mainwindow.py, which was in main.pyw.
        """
        input_text = self.input_text.toPlainText()

        text_bytes = bytearray()
        for char in input_text:
            char_bytes = globals.my_textman.inv_char_dict[char].to_bytes(2, byteorder='big')
            for byte in char_bytes:
                text_bytes.append(byte)
        output_string = ''
        for byte in text_bytes:
            output_string += f'{byte:02X}' + ' '
        self.output_text.setPlainText(output_string)