# -*- coding: utf-8 -*-

import sys

# Setting packages path
sys.path.append('..')

# Import PyQT5 library components
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtGui import QIcon

# Import interface classes
from ui_py.ui_paths_editor import Ui_Form as Ui_PathsEditorDialog

# Import built-in libraries
from functools import partial
import os
from pathlib import Path

# Import main constants
from main_constants import DIRNAME, EDITOR_ICON_PATH, create_encrypted_config_file

# Import "misc" functions and objects
from misc import delete_items_of_layout


class PathsEditorWidget(Ui_PathsEditorDialog, QtWidgets.QWidget):
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

    def set_data(self, databases: dict, config: dict, reload_dbs: None, reload_admin_panel: None):
        self.reload_dbs = reload_dbs
        self.reload_admin_panel = reload_admin_panel
        self.databases = databases
        self.config = config

    def on_change_path(self, *args):
        item = args[0]
        is_checked = eval(f'self.{item}_checkbox.isChecked()')
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setNameFilter("Базы данных (*.db *.sqlite3 *.sqlite)")
        if dialog.exec_():
            filename = Path(dialog.selectedFiles()[0]).resolve()
            if is_checked:
                filename = os.path.relpath(filename, start=DIRNAME)
            for tab in range(len(self.config["tabs"])):
                if self.config["tabs"][tab]["tab_number"] == int(item[3:]):
                    self.config["tabs"][tab]["db_paths"]["basic"]["path"] = str(filename).replace(os.sep, "/")
                    if is_checked:
                        self.config["tabs"][tab]["db_paths"]["basic"]["is_relative"] = True
                    else:
                        self.config["tabs"][tab]["db_paths"]["basic"]["is_relative"] = False
            exec(f'self.{item}_lineEdit.setText(filename)')
            create_encrypted_config_file(self.config)
            self.reload_dbs()
            self.reload_admin_panel()
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
        delete_items_of_layout(self.verticalLayout_3)
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
            exec(f'self.{item}_checkbox = QtWidgets.QCheckBox("Относительный путь")')
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