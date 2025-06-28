from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox
from Updater import update_files_from_github

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PySide6 App")
        self.setGeometry(100, 100, 400, 300)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # GUI elements
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter some text")
        self.layout.addWidget(self.input_field)
        
        self.display_label = QLabel("Hello, PySide6!")
        self.layout.addWidget(self.display_label)
        
        self.toggle_button = QPushButton("Toggle Label")
        self.toggle_button.clicked.connect(self.toggle_label)
        self.layout.addWidget(self.toggle_button)
        
        self.update_button = QPushButton("Check for Updates")
        self.update_button.clicked.connect(self.check_updates)
        self.layout.addWidget(self.update_button)
        
        # State for toggle
        self.label_state = True
        
    def toggle_label(self):
        """Toggles the label text between two states."""
        self.label_state = not self.label_state
        if self.label_state:
            self.display_label.setText("Hello, PySide6!")
        else:
            self.display_label.setText(self.input_field.text() or "No input provided")
    
    def check_updates(self):
        """Calls the GitHub update function and displays the result."""
        result = update_files_from_github(
            repo_url='https://api.github.com/repos/Kurkkumopo250/RemoteUpdateTesting',
            manifest_path='manifest.json',
            local_dir='.',
            branch='main'
        )
        
        message = f"Update Status: {result['status']}\n"
        if result['updated_files']:
            message += f"Updated Files: {', '.join(result['updated_files'])}\n"
        if result['errors']:
            message += f"Errors: {', '.join(result['errors'])}"
        else:
            message += "No errors"
        
        QMessageBox.information(self, "Update Result", message)