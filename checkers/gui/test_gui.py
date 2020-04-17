import sys
from PyQt5.QtWidgets import (QLineEdit, QPushButton, QApplication,
                             QVBoxLayout, QDialog)


def greetings():
    print('Hello World!')


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.button = QPushButton("Click me")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.button.clicked.connect(greetings)

    # Greets the user


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
