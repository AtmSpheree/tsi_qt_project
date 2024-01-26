import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ui_py.ui_main import Ui_MainWindow
import sqlite3
from main_constants import DB_PATHS, ICON_PATH


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def sqlite_lower(value_):
    return value_.lower()


def sqlite_upper(value_):
    return value_.upper()


def sqlite_ignore_case_collation(value1_, value2_):
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


class HistoryDataModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(HistoryDataModel, self).__init__()
        self.data = [["", ""]]
        self.horizontal_headers = []

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.horizontal_headers[section]
        return super().headerData(section, orientation, role)

    def set_horizontal_headers(self, headers):
        self.horizontal_headers = headers

    def set_data(self, data):
        self.data = data

    def append_row(self, row):
        if self.data == [["", ""]]:
            self.data = []
            self.data = [row + self.data]
        else:
            self.data = [row] + self.data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(ICON_PATH))

        self.setupUi(self)
        # uic.loadUi("ui_files/main.ui", self)
        self.set_functional_abilities()
        self.setup_special_ui()
        self.connect_to_dbs()

    def connect_to_dbs(self):
        self.db_first_connection = sqlite3.connect(DB_PATHS["tabFirst"])
        self.db_first_connection.create_function("LOWER", 1, sqlite_lower)
        self.db_first_connection.create_function("UPPER", 1, sqlite_upper)
        self.db_first_connection.create_collation("NOCASE", sqlite_ignore_case_collation)

    def set_functional_abilities(self):
        # First Table View
        self.tableViewHistoryFirstModel = HistoryDataModel()
        self.tableViewHistoryFirstModel.set_horizontal_headers(["№", "Термин"])
        self.tableViewHistoryFirst.setTextElideMode(Qt.ElideMiddle)
        self.tableViewHistoryFirst.setModel(self.tableViewHistoryFirstModel)
        self.tableViewHistoryFirst.horizontalHeader().sectionResized.connect(self.tableViewHistoryFirst.resizeRowsToContents)
        self.tableViewHistoryFirst.setWordWrap(True)
        self.tableViewHistoryFirst.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableViewHistoryFirst.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # First Search Button
        self.pushButtonSearchFirst.clicked.connect(self.push_button_search_first_clicked)

    def push_button_search_first_clicked(self):
        cursor = eval(f"self.db_{self.tabWidgetMain.currentWidget().objectName().lower()[3:]}_connection.cursor()")
        value = eval(f"self.lineEditSearch{self.tabWidgetMain.currentWidget().objectName()[3:]}.text()")
        query = f'SELECT terms.id, terms.term FROM abstractions JOIN terms ON abstractions.term_id = terms.id ' \
                f'WHERE LOWER(abstractions.abstraction) = LOWER("{value}")'
        cursor.execute(query)
        data = cursor.fetchone()
        if data is not None:
            exec(f"self.tableViewHistory{self.tabWidgetMain.currentWidget().objectName()[3:]}"
                 f"Model.append_row({list(data)})")
            exec(f"self.tableViewHistory{self.tabWidgetMain.currentWidget().objectName()[3:]}"
                 f".model().layoutChanged.emit()")
            exec(f"self.tableViewHistory{self.tabWidgetMain.currentWidget().objectName()[3:]}"
                 f".resizeRowsToContents()")
            self.textBrowserInfoFirst.setText(data[1])
            self.labelErrorFirst.setText("")
        else:
            self.labelErrorFirst.setText("Термина с таким названием нет в базе.")

    def setup_special_ui(self):
        self.labelSelectCourse.setMargin(10)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
