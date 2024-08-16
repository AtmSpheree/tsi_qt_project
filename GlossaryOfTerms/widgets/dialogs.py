# -*- coding: utf-8 -*-

import sys

# Setting packages path
sys.path.append('..')

# Import interface classes
from ui_py.ui_error_dialog import Ui_Dialog as Ui_ErrorDialog
from ui_py.ui_login_dialog import Ui_LoginDialog
from ui_py.ui_enter_value_dialog import Ui_EnterValueDialog
from ui_py.ui_info_dialog import Ui_Dialog as Ui_InfoDialog

# Import PyQT5 library components
from PyQt5 import QtWidgets, QtGui

# Import main constants
from main_constants import ADMIN_PANEL_ICON_PATH


# Default Ok_cancel QDialog class
class DefaultDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Setting specific interface settings that QtDesigner does not allow you to implement
    def setup_special_ui(self):
        pass

    # Setting error in the window title
    def set_window_title(self, text):
        self.setWindowTitle(text)

    def set_additional_padding_to_buttons(self, padding: int = 5, width: int = None, height: int = None):
        if not hasattr(self, "buttonBox"):
            raise Exception("You must init interface and set buttonBox attribute.")

        if width is not None:
            self_width = width
        else:
            self_width = padding
        if height is not None:
            self_height = height
        else:
            self_height = padding

        # Setting padding to the buttons
        for button in self.buttonBox.buttons():
            button.adjustSize()
            width = button.width()
            button.setFixedWidth(width + self_width * 2)
            height = button.height()
            button.setFixedHeight(height + self_height * 2)


# Error Dialog object class
class ErrorDialog(Ui_ErrorDialog, DefaultDialog):
    def __init__(self, *args, **kwargs):
        # Initialization of all initial features of the QDialog class
        # It's a required setting
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/error_dialog.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_ErrorDialog) to this one
        self.setupUi(self)

        # Uploading various code blocks
        # Their work is described in more detail below
        self.set_functional_abilities()
        self.setup_special_ui()

    # Setting text in the ok button
    def set_ok_button_text(self, text: str = "Ok"):
        self.buttonBox.button(self.buttonBox.Ok).setText(text)

    # Setting text in the cancel button
    def set_cancel_button_text(self, text: str = "Cancel"):
        self.buttonBox.button(self.buttonBox.Cancel).setText(text)

    # Setting error in the main label
    def set_error_label_text(self, text: str = "Something went wrong!"):
        self.label.setText(text)


# Info Dialog object class
class InfoDialog(Ui_InfoDialog, DefaultDialog):
    def __init__(self, *args, **kwargs):
        # Initialization of all initial features of the QDialog class
        # It's a required setting
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/info_dialog.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_InfoDialog) to this one
        self.setupUi(self)

        # Uploading various code blocks
        # Their work is described in more detail below
        self.set_functional_abilities()
        self.setup_special_ui()

    # Setting text in the ok button
    def set_ok_button_text(self, text: str = "Ok"):
        self.buttonBox.button(self.buttonBox.Ok).setText(text)

    # Setting error in the main label
    def set_error_label_text(self, text: str = "Something went wrong!"):
        self.label.setText(text)


class LoginDialog(Ui_LoginDialog, DefaultDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/ui_login_dialog.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_PathsEditorDialog) to this one
        self.setupUi(self)

        self.setup_special_ui()
        self.setWindowIcon(QtGui.QIcon(ADMIN_PANEL_ICON_PATH))
        self.is_close = False

    def set_data(self, config: None):
        self.config = config

    def set_error_message(self, message: str = ""):
        self.error_label.setText(message)

    def set_additional_padding_to_buttons(self, *args, **kwargs):
        super().set_additional_padding_to_buttons(*args, **kwargs)
        self.setFixedWidth(self.width())
        self.setFixedHeight(self.height())

    def set_functional_abilities(self):
        self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.buttonBox.clear()
        ok_button = QtWidgets.QPushButton("Войти")
        cancel_button = QtWidgets.QPushButton("Отмена")
        font = QtGui.QFont()
        font.setPointSize(10)
        ok_button.setFont(font)
        cancel_button.setFont(font)
        self.buttonBox.addButton(ok_button, QtWidgets.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(cancel_button, QtWidgets.QDialogButtonBox.RejectRole)


class EnterValueDialog(Ui_EnterValueDialog, DefaultDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/ui_enter_value_dialog.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_PathsEditorDialog) to this one
        self.setupUi(self)

        self.setup_special_ui()
        self.setWindowIcon(QtGui.QIcon(ADMIN_PANEL_ICON_PATH))
        self.is_close = False

    def set_data(self, config: None):
        self.config = config

    def set_error_message(self, message: str = ""):
        self.error_label.setText(message)

    def set_text_label(self, text: str = ""):
        self.text_label.setText(text)

    def set_line_edit_value(self, value: str = ""):
        self.value_lineEdit.setText(value)

    def set_additional_padding_to_buttons(self, *args, **kwargs):
        super().set_additional_padding_to_buttons(*args, **kwargs)
        self.setFixedWidth(self.width())
        self.setFixedHeight(self.height())

    def set_functional_abilities(self):
        self.buttonBox.clear()
        ok_button = QtWidgets.QPushButton("ОК")
        cancel_button = QtWidgets.QPushButton("Отмена")
        font = QtGui.QFont()
        font.setPointSize(10)
        ok_button.setFont(font)
        cancel_button.setFont(font)
        self.buttonBox.addButton(ok_button, QtWidgets.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(cancel_button, QtWidgets.QDialogButtonBox.RejectRole)