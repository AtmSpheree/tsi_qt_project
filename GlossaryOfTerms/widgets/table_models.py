# -*- coding: utf-8 -*-

# Import PyQT5 library components
from PyQt5 import QtCore


# PyQT5 Universal Abstract Table Model to represent data about short values
class UniversalTableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(UniversalTableModel, self).__init__()
        self._data = []
        self.horizontal_headers = []

    # Setting headers - fields from the database for correct display
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.horizontal_headers[section]
        return super().headerData(section, orientation, role)

    # Setting horizontal headers
    def set_horizontal_headers(self, headers):
        self.horizontal_headers = headers

    # Setting table data
    def set_data(self, data):
        self._data = data

    # Getting table data
    def get_data(self):
        return self._data

    # Adding row into table model
    def append_row(self, row):
        if not any(map(lambda x: any(map(lambda y: y, x)), self._data)):
            self._data = [row]
        else:
            self._data = [row] + self._data

    # Getting different table cell using its index
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    # Getting current table rows count
    def rowCount(self, index):
        return len(self._data)

    # Getting current table columns (db fields) count
    def columnCount(self, index):
        return len(self._data[0])