# -*- coding: utf-8 -*-

# The main application script
# When compiling via py2exe or pyinstaller scripts or just run with python3,
# it is necessary to specify exactly it

# Import PyQT5 library components
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMenu, QAction, QWidget, QHeaderView, QFileDialog, \
    QCheckBox, QMessageBox, QPushButton, QDialogButtonBox
from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Import interface classes
from ui_py.ui_error_dialog import Ui_Dialog as Ui_ErrorDialog
from ui_py.ui_main import Ui_MainWindow
from ui_py.ui_paths_editor import Ui_Form as Ui_PathsEditorDialog
from ui_py.ui_login_dialog import Ui_LoginDialog
from tab_constructor import SectionTabQWidget

# Import cryptography variables
from cryptography.fernet import Fernet
from secret_key import SECRET_KEY

# Import built-in libraries
import sys
import sqlite3
import json
import os
from functools import partial
from pathlib import Path

from main_constants import ICON_PATH, DIRNAME, EDITOR_ICON_PATH, ADMIN_PANEL_ICON_PATH, create_encrypted_config_file
from default_config import CONFIG


# The standard Exception Hook allows you to output possible errors
# to the console when launching an application during development
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Function for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to use the SQL LOWER function without bugs
def sqlite_lower(value_):
    return value_.lower()


# Function for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to use the SQL UPPER function without bugs
def sqlite_upper(value_):
    return value_.upper()


# Function for working with the sqlite3 library
# After connecting to the database connection,
# it allows you to compare data in case-insensitive SQL queries
def sqlite_ignore_case_collation(value1_, value2_):
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


# Default Ok_cancel QDialog class
class DefaultDialog(QDialog):
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


class PathsEditorWidget(Ui_PathsEditorDialog, QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/ui_paths_editor.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_PathsEditorDialog) to this one
        self.setupUi(self)

        self.setup_special_ui()
        self.setWindowIcon(QIcon(EDITOR_ICON_PATH))

        # Showing widget to user
        self.show()

    # Setting specific interface settings that QtDesigner does not allow you to implement
    def setup_special_ui(self):
        self.label.setMargin(10)

    def set_data(self, databases: dict, config: None, reload_dbs: None):
        self.reload_dbs = reload_dbs
        self.databases = databases
        self.config = config

    def on_change_path(self, *args):
        item = args[0]
        is_checked = eval(f'self.{item}_checkbox.isChecked()')
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Базы данных (*.db *.sqlite3 *.sqlite)")
        if dialog.exec_():
            filename = Path(dialog.selectedFiles()[0]).resolve()
            if is_checked:
                filename = os.path.relpath(filename, start=DIRNAME)
            print(self.config)
            for tab in range(len(self.config["tabs"])):
                if self.config["tabs"][tab]["tab_number"] == int(item[3:]):
                    self.config["tabs"][tab]["db_paths"]["basic"]["path"] = str(filename).replace(os.sep, "/")
                    if is_checked:
                        self.config["tabs"][tab]["db_paths"]["basic"]["is_relative"] = True
                    else:
                        self.config["tabs"][tab]["db_paths"]["basic"]["is_relative"] = False
            print(self.config)
            exec(f'self.{item}_lineEdit.setText(filename)')
            create_encrypted_config_file(self.config)
            self.reload_dbs()
            if self.databases[item]["exceptions"]["basic"] is not None:
                exec(f'self.{item}_lineEdit.setStyleSheet("background-color: #ff4747;")')
            else:
                exec(f'self.{item}_lineEdit.setStyleSheet("background-color: #4dff3d;")')

    def on_click_checkbox(self, *args):
        item = args[0]
        is_checked = eval(f'self.{item}_checkbox.isChecked()')
        filename = eval(f"self.{item}_lineEdit.text()")
        if is_checked:
            filename = os.path.relpath(filename, start=DIRNAME)
        else:
            filename = (DIRNAME / filename).resolve()
        for tab in range(len(self.config["tabs"])):
            if self.config["tabs"][tab]["tab_number"] == int(item[3:]):
                self.config["tabs"][tab]["db_paths"]["basic"]["path"] = str(filename).replace(os.sep, "/")
                if is_checked:
                    self.config["tabs"][tab]["db_paths"]["basic"]["is_relative"] = True
                else:
                    self.config["tabs"][tab]["db_paths"]["basic"]["is_relative"] = False
        exec(f'self.{item}_lineEdit.setText(str(filename))')
        create_encrypted_config_file(self.config)
        self.reload_dbs()

    def create_elements(self):
        print(self.config)
        for item in self.databases:
            exec(f'self.{item}_verticalLayout = QtWidgets.QVBoxLayout()')
            exec(f'self.{item}_verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)')
            exec(f'self.{item}_verticalLayout.setObjectName("{item}_verticalLayout")')
            exec(f'self.{item}_label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)')
            font = QtGui.QFont()
            font.setPointSize(10)
            exec(f'self.{item}_label_2.setFont(font)')
            exec(f'self.{item}_label_2.setObjectName("{item}_label_2")')
            exec(f'self.{item}_label_2.setText("{self.databases[item]["name"]}")')
            exec(f'self.{item}_verticalLayout.addWidget(self.{item}_label_2)')
            exec(f'self.{item}_horizontalLayout = QtWidgets.QHBoxLayout()')
            exec(f'self.{item}_horizontalLayout.setObjectName("{item}_horizontalLayout")')
            exec(f'self.{item}_lineEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)')
            if eval(f'self.databases[item]["exceptions"]["basic"] is not None'):
                exec(f'self.{item}_lineEdit.setStyleSheet("background-color: #ff4747;")')
            else:
                exec(f'self.{item}_lineEdit.setStyleSheet("background-color: #4dff3d;")')
            font = QtGui.QFont()
            font.setPointSize(10)
            exec(f'self.{item}_lineEdit.setFont(font)')
            exec(f'self.{item}_lineEdit.setReadOnly(True)')
            exec(f'self.{item}_lineEdit.setObjectName("{item}_lineEdit")')
            exec(f'self.{item}_checkbox = QCheckBox("Относительный путь")')
            exec(f'self.{item}_checkbox.setFont(font)')
            if any(map(lambda x: (x["tab_number"] == int(item[3:]) and x["db_paths"]["basic"]["is_relative"]),
                       self.config["tabs"])):
                exec(f'self.{item}_checkbox.setChecked(True)')
                filename = os.path.relpath(self.databases[item]["paths"]["basic"], start=DIRNAME)
            else:
                filename = self.databases[item]["paths"]["basic"]
            exec(f'self.{item}_lineEdit.setText(r"{filename}")')
            exec(f'self.{item}_lineEdit.setReadOnly(True)')
            exec(f'self.{item}_horizontalLayout.addWidget(self.{item}_lineEdit)')
            exec(f'self.{item}_toolButton = QtWidgets.QToolButton(self.scrollAreaWidgetContents)')
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            exec(f'sizePolicy.setHeightForWidth(self.{item}_toolButton.sizePolicy().hasHeightForWidth())')
            exec(f'self.{item}_toolButton.setSizePolicy(sizePolicy)')
            exec(f'self.{item}_toolButton.setText("...")')
            font = QtGui.QFont()
            font.setPointSize(10)
            exec(f'self.{item}_toolButton.setFont(font)')
            exec(f'self.{item}_toolButton.setObjectName("{item}_toolButton")')
            exec(f'self.{item}_horizontalLayout.addWidget(self.{item}_toolButton)')
            exec(f'self.{item}_verticalLayout.addLayout(self.{item}_horizontalLayout)')
            exec(f'self.{item}_checkbox.clicked.connect(partial(self.on_click_checkbox, item))')
            exec(f'self.{item}_verticalLayout.addWidget(self.{item}_checkbox)')
            exec(f'self.verticalLayout_3.addLayout(self.{item}_verticalLayout)')

            exec(f'self.{item}_toolButton.clicked.connect(partial(self.on_change_path, item))')

        spacerItem = QtWidgets.QSpacerItem(20, 196, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)


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
        self.setWindowIcon(QIcon(ADMIN_PANEL_ICON_PATH))
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
        ok_button = QPushButton("Войти")
        cancel_button = QPushButton("Отмена")
        font = QtGui.QFont()
        font.setPointSize(10)
        ok_button.setFont(font)
        cancel_button.setFont(font)
        self.buttonBox.addButton(ok_button, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(cancel_button, QDialogButtonBox.RejectRole)


# PyQT5 Abstract Table Model to represent search history data
class HistoryDataModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(HistoryDataModel, self).__init__()
        self.data = [["", "", ""]]
        self.horizontal_headers = []
        self.number = 1

    def get_number(self):
        return self.number

    def increment_number(self):
        self.number += 1

    # Setting headers - fields from the database for correct display
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.horizontal_headers[section]
        return super().headerData(section, orientation, role)

    # Setting horizontal headers
    def set_horizontal_headers(self, headers):
        self.horizontal_headers = headers

    # Setting table data
    def set_data(self, data):
        self.data = data

    # Adding row into table model
    def append_row(self, row):
        if self.data == [["", "", ""]]:
            self.data = []
            self.data = [row + self.data]
        else:
            self.data = [row] + self.data

    # Getting different table cell using its index
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    # Getting current table rows count
    def rowCount(self, index):
        return len(self.data)

    # Getting current table columns (db fields) count
    def columnCount(self, index):
        return len(self.data[0])


# Main Window of the PyQT5 program
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Initialization of all initial features of the QMainWindow class
        # It's a required setting
        super().__init__()

        # Setting application icon using path
        self.setWindowIcon(QIcon(ICON_PATH))

        # uic.loadUi("ui_files/main.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_MainWindow) to this one
        self.setupUi(self)

        # Uploading or creating config, if it doesn't exist
        exc = None
        if os.path.isfile((DIRNAME / "config").resolve()):
            try:
                with open((DIRNAME / "config").resolve(), "rb") as file:
                    self.config = json.loads(Fernet(SECRET_KEY.encode()).decrypt(file.read()))
            except Exception:
                exc = "Not valid config."
        else:
            exc = "File doesn't exist."
        if exc is not None:
            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Critical)
            dialog.setWindowTitle("Ошибка.")
            dialog.setWindowIcon(QIcon(ICON_PATH))
            if exc == "Not valid config.":
                text = {"text": "Файл конфигурации повреждён.",
                        "informative_text": "Вы хотите перезаписать файл конфигурации с настройками по умолчанию?",
                        "accept_button_text": "Перезаписать"}
            elif exc == "File doesn't exist.":
                text = {"text": "Отсутствует файл конфигурации.",
                        "informative_text": "Создать файл конфигурации с настройками по умолчанию?",
                        "accept_button_text": "Создать"}
            else:
                text = ("Fatal Error.", "Fatal Error.")
            dialog.setText(text["text"])
            dialog.setInformativeText(text["informative_text"])
            ok_button = dialog.addButton(text["accept_button_text"], QMessageBox.AcceptRole)
            cancel_button = dialog.addButton("Отмена", QMessageBox.RejectRole)
            dialog.exec_()
            if dialog.clickedButton() == ok_button:
                create_encrypted_config_file(CONFIG)
                with open((DIRNAME / "config").resolve(), "rb") as file:
                    self.config = json.loads(Fernet(SECRET_KEY.encode()).decrypt(file.read()))
            elif dialog.clickedButton() == cancel_button:
                sys.exit(0)

        # Setting initial values of mail variables
        self.databases = dict()
        self.paths_editor = None
        self.login_dialog = None

        # Uploading various code blocks
        # Their work is described in more detail below
        self.set_functional_abilities()
        self.connect_to_dbs()
        self.setup_special_ui()

    # Connecting to databases using the path specified in the main_constants.py
    # exec allows to automate this process
    def connect_to_dbs(self):
        for tab in self.config["tabs"]:
            db_paths = tab["db_paths"]
            exception = None
            self.databases[f"tab{tab['tab_number']}"] = {"name": tab["name"],
                                                         "paths": {
                                                             "basic": (DIRNAME / db_paths["basic"]["path"]).resolve()
                                                             if db_paths["basic"]["is_relative"] else db_paths["basic"]["path"],
                                                             "additional": [(DIRNAME / i["path"]).resolve() if i["is_relative"]
                                                                            else i["path"] for i in db_paths["additional"]]
                                                         },
                                                         "connections": {
                                                             "basic": None,
                                                             "additional": []
                                                         },
                                                         "exceptions": {
                                                             "basic": None,
                                                             "additional": []
                                                         }}
            db_path = self.databases[f"tab{tab['tab_number']}"]["paths"]["basic"]
            try:
                if not os.path.isfile(db_path):
                    raise Exception(f'The database on the path '
                                    f'"{db_path}" does not exist')
                connection = sqlite3.connect(db_path)
                self.databases[f"tab{tab['tab_number']}"]["connections"]["basic"] = connection
            except Exception as ex:
                self.databases[f"tab{tab['tab_number']}"]["exceptions"]["basic"] = (ex, db_path)
            for path in self.databases[f"tab{tab['tab_number']}"]["paths"]["additional"]:
                try:
                    connection = sqlite3.connect(path)

                    # The following code block does not work because you need to assign
                    # functions to the database connection immediately before sending the query
                    # connection.create_function("LOWER", 1, sqlite_lower)
                    # connection.create_function("UPPER", 1, sqlite_upper)
                    # connection.create_collation("NOCASE", sqlite_ignore_case_collation)
                    self.databases[f"tab{tab['tab_number']}"]["connections"]["additional"] += [connection]
                except Exception as ex:
                    self.databases[f"tab{tab['tab_number']}"]["exceptions"]["additional"] += [(ex, path)]

        # Setting error messages for individual tabs
        for tab in self.config["tabs"]:
            exception = self.databases[f"tab{tab['tab_number']}"]["exceptions"]["basic"]
            if exception is not None:
                tab_obj = eval(f'self.tab{tab["tab_number"]}')
                error_text = f'Exception: "{exception[0].args[0]}"\n' \
                             f'Ошибка подключения к базе данных, путь:\n' \
                             f'{exception[1]}'
                exec(f'tab_obj.textBrowserInfo_tab{tab["tab_number"]}.setText(error_text)')
                exec(f'tab_obj.labelError_tab{tab["tab_number"]}.setText("Ошибка подключения к базе данных!")')
            else:
                tab_obj = eval(f'self.tab{tab["tab_number"]}')
                exec(f'tab_obj.textBrowserInfo_tab{tab["tab_number"]}.setText("")')
                exec(f'tab_obj.labelError_tab{tab["tab_number"]}.setText("")')

    # Opening a window for editing database paths
    def exec_paths_editor(self):
        if self.paths_editor is not None:
            self.paths_editor.close()
        self.paths_editor = PathsEditorWidget()
        self.paths_editor.set_data(self.databases, self.config, self.connect_to_dbs)
        self.paths_editor.create_elements()

    # Opening a window for editing databases information (admin panel)
    def exec_admin_panel(self):
        if self.login_dialog is not None:
            self.login_dialog.close()
        self.login_dialog = LoginDialog()
        self.login_dialog.set_functional_abilities()
        self.login_dialog.set_additional_padding_to_buttons(1)
        self.login_dialog.set_error_message()
        while True:
            if self.login_dialog.exec():
                username = self.login_dialog.username_lineEdit.text()
                password = self.login_dialog.password_lineEdit.text()
                if any(map(lambda x: x["username"] == username and x["password"] == password, self.config["users"])):
                    self.login_dialog.close()
                else:
                    self.login_dialog.set_error_message("Неверное имя пользователя или пароль!")
            else:
                self.login_dialog.close()
                break

    # Functional configuration of PyQt5 components
    # Enabling event handling of button clicks, etc.
    def set_functional_abilities(self):
        # Creating menu on menubar
        self.menu = QMenu("Меню", self)
        self.open_paths_editor_action = QAction(QIcon(EDITOR_ICON_PATH),
                                                "&Редактировать пути к БД", self)
        self.open_admin_panel_action = QAction(QIcon(ADMIN_PANEL_ICON_PATH),
                                                "&Панель управления", self)
        self.open_paths_editor_action.triggered.connect(self.exec_paths_editor)
        self.open_admin_panel_action.triggered.connect(self.exec_admin_panel)
        self.menu.addAction(self.open_paths_editor_action)
        self.menu.addAction(self.open_admin_panel_action)
        self.menubar.addMenu(self.menu)

        # Creating tabs
        for tab in self.config["tabs"]:
            exec(f'self.tab{tab["tab_number"]} = SectionTabQWidget()')
            exec(f'self.tab{tab["tab_number"]}.set_order_num(tab["tab_number"])')
            exec(f'self.tab{tab["tab_number"]}.setup_ui()')
            exec(f'self.tabWidgetMain.addTab(self.tab{tab["tab_number"]}, "")')
            exec(f'self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(self.tab{tab["tab_number"]}), tab["name"])')

        # Setting up models of the history data tables
        for tab in self.config["tabs"]:
            tab_obj = eval(f'self.tab{tab["tab_number"]}')
            exec(f'tab_obj.tableViewHistoryModel_tab{tab["tab_number"]} = HistoryDataModel()')
            exec(
                f'tab_obj.tableViewHistoryModel_tab{tab["tab_number"]}.set_horizontal_headers(["№", "Термин", "Определение"])')
            exec(f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.setTextElideMode(Qt.ElideMiddle)')
            exec(
                f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.setModel(tab_obj.tableViewHistoryModel_tab{tab["tab_number"]})')
            exec(
                f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.horizontalHeader().sectionResized.connect(tab_obj.tableViewHistory_tab{tab["tab_number"]}.resizeRowsToContents)')
            exec(f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.setWordWrap(True)')
            exec(
                f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)')
            exec(
                f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)')
            exec(
                f'tab_obj.tableViewHistory_tab{tab["tab_number"]}.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)')

            # Connecting the buttons in its corresponding function
            exec(f'tab_obj.pushButtonSearch_tab{tab["tab_number"]}.clicked.connect(self.push_button_search_clicked)')

    # The function of searching for data from the first database when pressing connected button
    # It is implemented using eval and exec,
    # which allows it to be used repeatedly for different databases
    def push_button_search_clicked(self):
        order_name = self.tabWidgetMain.currentWidget().objectName()
        if self.databases[order_name]["exceptions"]["basic"] is not None:
            return
        tab_obj = self.tabWidgetMain.currentWidget()
        exec(f"self.databases['{order_name}']['connections']['basic'].create_function('LOWER', 1, sqlite_lower)")
        exec(f"self.databases['{order_name}']['connections']['basic'].create_function('UPPER', 1, sqlite_upper)")
        exec(
            f"self.databases['{order_name}']['connections']['basic'].create_collation('NOCASE', sqlite_ignore_case_collation)")
        cursor = eval(f"self.databases['{order_name}']['connections']['basic'].cursor()")
        value = eval(f"tab_obj.lineEditSearch_{order_name}.text()")
        query = f'SELECT terms.term AS term, terms.short AS short FROM abstractions JOIN terms ON ' \
                f'abstractions.term_id = terms.id WHERE LOWER(abstractions.abstraction) = LOWER("{value}")'
        cursor.execute(f"SELECT abstractions.abstraction, Final.term FROM ({query}) AS Final "
                       f"JOIN abstractions ON abstractions.id = Final.short")
        data = cursor.fetchone()
        if data is None:
            for connection in eval(f'self.databases["{order_name}"]["connections"]["additional"]'):
                cursor = connection.cursor()
        if data is None:
            exec(f'tab_obj.labelError_{order_name}.setText("Термина с таким названием нет в базе.")')
        else:
            data = (eval(f"tab_obj.tableViewHistoryModel_{order_name}.get_number()"), data[0], data[1])
            exec(f"tab_obj.tableViewHistoryModel_{order_name}.increment_number()")
            exec(f"tab_obj.tableViewHistoryModel_{order_name}.append_row({list(data)})")
            exec(f"tab_obj.tableViewHistory_{order_name}.model().layoutChanged.emit()")
            exec(f"tab_obj.tableViewHistory_{order_name}.resizeRowsToContents()")
            exec(f'tab_obj.textBrowserInfo_{order_name}.setText(data[2])')
            exec(f'tab_obj.labelError_{order_name}.setText("")')

    # Setting specific interface settings that QtDesigner does not allow you to implement
    def setup_special_ui(self):
        self.labelSelectCourse.setMargin(10)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        sys.exit(0)


# The condition is a stub for running the application script,
# when it is a directly executable file
# (the startup is eliminated if it is imported as a module etc.)
if __name__ == '__main__':
    # Setting exception hook
    sys.excepthook = except_hook

    # Creating application variable
    app = QApplication(sys.argv)

    # Creating an instance of the main application window class
    ex = MainWindow()

    # Showing the main window to the user
    ex.show()

    # Completion of the script after the user closes the application
    sys.exit(app.exec_())
