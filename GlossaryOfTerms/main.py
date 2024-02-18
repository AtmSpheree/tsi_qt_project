# -*- coding: utf-8 -*-
# The main application script
# When compiling via py2exe or pyinstaller scripts or just run with python3,
# it is necessary to specify exactly it

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QDialog
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui_py.ui_error_dialog import Ui_Dialog
from ui_py.ui_main import Ui_MainWindow
import sqlite3
from main_constants import CONFIG, ICON_PATH


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


# Error Dialog object class
class ErrorDialog(QDialog, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        # Initialization of all initial features of the QDialog class
        # It's a required setting
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/error_dialog.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_Dialog) to this one
        self.setupUi(self)

        # Uploading various code blocks
        # Their work is described in more detail below
        self.set_functional_abilities()
        self.setup_special_ui()

    # Setting specific interface settings that QtDesigner does not allow you to implement
    def setup_special_ui(self):
        pass

    # Functional configuration of PyQt5 components
    # Enabling event handling of button clicks, etc.
    def set_functional_abilities(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    # Setting error in the window title
    def set_error_window_title(self, text: str = "Error."):
        self.setWindowTitle(text)

    # Setting error in the main label
    def set_error_label_text(self, text: str = "Something went wrong!"):
        self.label.setText(text)

    # Setting text in the ok button
    def set_ok_button_text(self, text: str = "Ok"):
        self.buttonBox.button(self.buttonBox.Ok).setText(text)

    # Setting text in the cancel button
    def set_cancel_button_text(self, text: str = "Cancel"):
        self.buttonBox.button(self.buttonBox.Cancel).setText(text)

    def set_additional_padding_to_buttons(self, padding: int = 5):
        # Setting padding in the ok button
        width = self.buttonBox.button(self.buttonBox.Ok).width()
        self.buttonBox.button(self.buttonBox.Ok).setFixedWidth(width + padding * 2)

        # Setting padding in the cancel button
        width = self.buttonBox.button(self.buttonBox.Cancel).width()
        self.buttonBox.button(self.buttonBox.Cancel).setFixedWidth(width + padding * 2)


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

        # Uploading various code blocks
        # Their work is described in more detail below
        self.set_functional_abilities()
        self.setup_special_ui()
        self.connect_to_dbs()

    # Connecting to databases using the path specified in the main_constants.py
    # exec allows to automate this process
    def connect_to_dbs(self):
        for db in CONFIG["db_paths"]:
            db_paths = CONFIG["db_paths"][db]["basic"]
            order_name = db.split('tab')[1].lower()
            exception = None
            for path in db_paths:
                try:
                    exec(f'self.db_{order_name}_connection = sqlite3.connect(path)')
                    exec(f'self.db_{order_name}_connection.create_function("LOWER", 1, sqlite_lower)')
                    exec(f'self.db_{order_name}_connection.create_function("UPPER", 1, sqlite_upper)')
                    exec(f'self.db_{order_name}_connection.create_collation("NOCASE", sqlite_ignore_case_collation)')
                except Exception as ex:
                    exception = ex
                else:
                    exception = None
                    break
            if exception is not None:
                break
        if exception is not None:
            # Creating error dialog window and configuring it
            dialog = ErrorDialog(self)
            dialog.set_error_window_title("Fatal Error.")
            structure = '{"databases": \n' \
                        '    [\n' \
                        '        "db_first.db",\n' \
                        '        "db_second.db",\n' \
                        '        "db_third.db"\n' \
                        '    ]\n' \
                        '}'
            dialog.set_error_label_text(f"Ошибка доступа к одной из баз данных:\n"
                                        f'"{exception.args[0].capitalize()}"\n'
                                        f"По умолчанию базы данных должны находиться в директории "
                                        f"databases внутри директории приложения, или на уровень выше.\n"
                                        f"Изначальная структура:\n"
                                        f"{structure}\n"
                                        f"Пожалуйста, укажите пути к директориям вручную.")
            dialog.set_ok_button_text("Редактировать")
            dialog.set_cancel_button_text("Выйти")
            dialog.set_additional_padding_to_buttons(0)

            # Getting answer from the user
            result = dialog.exec()
            if result:
                pass
            else:
                sys.exit()

    # Functional configuration of PyQt5 components
    # Enabling event handling of button clicks, etc.
    def set_functional_abilities(self):
        # Setting up the first model of the history data table
        self.tableViewHistoryFirstModel = HistoryDataModel()
        self.tableViewHistoryFirstModel.set_horizontal_headers(["№", "Термин", "Определение"])
        self.tableViewHistoryFirst.setTextElideMode(Qt.ElideMiddle)
        self.tableViewHistoryFirst.setModel(self.tableViewHistoryFirstModel)
        self.tableViewHistoryFirst.horizontalHeader().sectionResized.connect(self.tableViewHistoryFirst.resizeRowsToContents)
        self.tableViewHistoryFirst.setWordWrap(True)
        self.tableViewHistoryFirst.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableViewHistoryFirst.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableViewHistoryFirst.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        # Setting up the second model of the history data table
        self.tableViewHistorySecondModel = HistoryDataModel()
        self.tableViewHistorySecondModel.set_horizontal_headers(["№", "Термин", "Определение"])
        self.tableViewHistorySecond.setTextElideMode(Qt.ElideMiddle)
        self.tableViewHistorySecond.setModel(self.tableViewHistorySecondModel)
        self.tableViewHistorySecond.horizontalHeader().sectionResized.connect(
        self.tableViewHistorySecond.resizeRowsToContents)
        self.tableViewHistorySecond.setWordWrap(True)
        self.tableViewHistorySecond.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableViewHistorySecond.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableViewHistorySecond.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        # Setting up the third model of the history data table
        self.tableViewHistoryThirdModel = HistoryDataModel()
        self.tableViewHistoryThirdModel.set_horizontal_headers(["№", "Термин", "Определение"])
        self.tableViewHistoryThird.setTextElideMode(Qt.ElideMiddle)
        self.tableViewHistoryThird.setModel(self.tableViewHistoryThirdModel)
        self.tableViewHistoryThird.horizontalHeader().sectionResized.connect(
        self.tableViewHistoryThird.resizeRowsToContents)
        self.tableViewHistoryThird.setWordWrap(True)
        self.tableViewHistoryThird.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableViewHistoryThird.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableViewHistoryThird.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        # Connecting the buttons in its corresponding function
        self.pushButtonSearchFirst.clicked.connect(self.push_button_search_clicked)
        self.pushButtonSearchSecond.clicked.connect(self.push_button_search_clicked)
        self.pushButtonSearchThird.clicked.connect(self.push_button_search_clicked)

    # The function of searching for data from the first database when pressing connected button
    # It is implemented using eval and exec,
    # which allows it to be used repeatedly for different databases
    def push_button_search_clicked(self):
        order_name = self.tabWidgetMain.currentWidget().objectName()[3:]
        cursor = eval(f"self.db_{order_name.lower()}_connection.cursor()")
        value = eval(f"self.lineEditSearch{self.tabWidgetMain.currentWidget().objectName()[3:]}.text()")
        query = f'SELECT terms.term AS term, terms.short AS short FROM abstractions JOIN terms ON ' \
                f'abstractions.term_id = terms.id WHERE LOWER(abstractions.abstraction) = LOWER("{value}")'
        cursor.execute(f"SELECT abstractions.abstraction, Final.term FROM ({query}) AS Final "
                       f"JOIN abstractions ON abstractions.id = Final.short")
        data = cursor.fetchone()
        if data is None:
            exec(f'self.labelError{order_name}.setText("Термина с таким названием нет в базе.")')
        else:
            data = (eval(f"self.tableViewHistory{order_name}Model.get_number()"), data[0], data[1])
            exec(f"self.tableViewHistory{order_name}Model.increment_number()")
            exec(f"self.tableViewHistory{order_name}"
                 f"Model.append_row({list(data)})")
            exec(f"self.tableViewHistory{order_name}"
                 f".model().layoutChanged.emit()")
            exec(f"self.tableViewHistory{order_name}"
                 f".resizeRowsToContents()")
            exec(f'self.textBrowserInfo{order_name}.setText(data[2])')
            exec(f'self.labelError{order_name}.setText("")')

    # Setting specific interface settings that QtDesigner does not allow you to implement
    def setup_special_ui(self):
        self.labelSelectCourse.setMargin(10)


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
