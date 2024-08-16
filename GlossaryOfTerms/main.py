# -*- coding: utf-8 -*-

# The main application script
# When compiling via py2exe or pyinstaller scripts or just run with python3,
# it is necessary to specify exactly it

# Import PyQT5 library components
from PyQt5 import QtCore, QtWidgets, QtGui

# Import interface classes
from ui_py.ui_main import Ui_MainWindow

# Import cryptography variables
from cryptography.fernet import Fernet
from secret_key import SECRET_KEY

# Import built-in libraries
import sys
import sqlite3
import json
import os
from pathlib import Path
from main_constants import ICON_PATH, DIRNAME, EDITOR_ICON_PATH, ADMIN_PANEL_ICON_PATH, create_encrypted_config_file

# Import default config
from default_config import CONFIG

# Import "misc" functions and objects
from misc import except_hook, execute_query, sqlite_decrypt_constructor, SqliteConcatStrings

# Import other widgets separated in other files
from widgets.admin_panel import AdminPanelWidget
from widgets.paths_editor import PathsEditorWidget
import widgets.dialogs
import widgets.table_models
from tab_constructor import SectionTabQWidget


# Main Window of the PyQT5 program
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Initialization of all initial features of the QMainWindow class
        # It's a required setting
        super().__init__()

        # Setting application icon using path
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

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
            dialog = QtWidgets.QMessageBox()
            dialog.setIcon(QtWidgets.QMessageBox.Critical)
            dialog.setWindowTitle("Ошибка.")
            dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
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
            ok_button = dialog.addButton(text["accept_button_text"], QtWidgets.QMessageBox.AcceptRole)
            cancel_button = dialog.addButton("Отмена", QtWidgets.QMessageBox.RejectRole)
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
        self.admin_panel = None
        self.login_dialog = None

        # Uploading various code blocks
        # Their work is described in more detail below
        self.setWindowTitle(self.config["main_window_title"])
        self.setup_functional_abilities()
        self.connect_to_dbs()
        self.setup_special_ui()

    # Connecting to databases using the path specified in the main_constants.py
    # exec allows to automate this process
    def connect_to_dbs(self):
        self.databases.clear()
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
                                                         },
                                                         "secret_key": tab["secret_key"]}
            db_path = self.databases[f"tab{tab['tab_number']}"]["paths"]["basic"]
            try:
                if not os.path.isfile(db_path):
                    raise Exception(f'The database on the path '
                                    f'"{db_path}" does not exist')
                connection = sqlite3.connect(db_path)
                self.databases[f"tab{tab['tab_number']}"]["connections"]["basic"] = connection
                query = f'SELECT DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), CUSTOMCONCAT(DECRYPT(D.document)), DECRYPT(T.term) ' \
                        f'FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                        f'GROUP BY T.term ' \
                        f'ORDER BY S.short ASC'
                cursor = execute_query(connection, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(tab["secret_key"])),),
                                       (('CUSTOMCONCAT', 1, SqliteConcatStrings),))
            except Exception as ex:
                if type(ex) == sqlite3.OperationalError:
                    self.databases[f"tab{tab['tab_number']}"]["exceptions"]["basic"] = (Exception(f'The database on the path '
                                                                                                  f'"{db_path}" is corrupted'), db_path)
                else:
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
        self.set_tabs_errors()

    # Setting error messages for individual tabs
    def set_tabs_errors(self):
        for tab in self.config["tabs"]:
            exception = self.databases[f"tab{tab['tab_number']}"]["exceptions"]["basic"]
            if exception is not None:
                tab_obj = eval(f'self.tab{tab["tab_number"]}')
                if str(exception[0]).endswith("is corrupted"):
                    error_text = f'Exception: "{exception[0].args[0]}"\n' \
                                 f'Ошибка чтения базы данных, путь:\n' \
                                 f'{exception[1]}'
                    exec(f'tab_obj.labelError.setText("Ошибка чтения базы данных!")')
                else:
                    error_text = f'Exception: "{exception[0].args[0]}"\n' \
                                 f'Ошибка подключения к базе данных, путь:\n' \
                                 f'{exception[1]}'
                    exec(f'tab_obj.labelError.setText("Ошибка подключения к базе данных!")')
                exec(f'tab_obj.textBrowserInfo.setText(error_text)')
            else:
                tab_obj = eval(f'self.tab{tab["tab_number"]}')
                exec(f'tab_obj.textBrowserInfo.setText("")')
                exec(f'tab_obj.labelError.setText("")')

    def raise_encryption_exception(self, db_name: str):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Critical)
        dialog.setWindowTitle("Ошибка.")
        dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
        ok_button = dialog.addButton("ОК", QtWidgets.QMessageBox.AcceptRole)
        for tab in self.config["tabs"]:
            if tab["name"] == db_name:
                db_path = (DIRNAME / Path(tab["db_paths"]["basic"]["path"])).resolve()
        text = {"text": "Не удалось расшифровать базу данных.",
                "description_text": f'Вероятно, содержимое дисциплины "{db_name}" '
                                    f'("{db_path}") повреждено.'}
        dialog.setText(text["text"])
        dialog.setInformativeText(text["description_text"])
        dialog.exec_()

    # Reloading databases on paths editor
    def reload_paths_editor(self):
        if self.paths_editor is not None:
            self.paths_editor.create_elements()

    # Reloading databases on admin panel
    def reload_admin_panel(self):
        if self.admin_panel is not None:
            self.admin_panel.create_elements()
            self.admin_panel.reload_widgets()

    # Opening a window for editing database paths
    def exec_paths_editor(self):
        if self.paths_editor is not None:
            self.paths_editor.close()
        self.paths_editor = PathsEditorWidget()
        self.paths_editor.set_data(self.databases, self.config, self.connect_to_dbs, self.reload_admin_panel)
        self.paths_editor.create_elements()

    # Opening a window for editing databases information (admin panel)
    def exec_admin_panel(self):
        if self.login_dialog is not None:
            self.login_dialog.close()
        self.login_dialog = widgets.dialogs.LoginDialog()
        self.login_dialog.set_functional_abilities()
        self.login_dialog.set_additional_padding_to_buttons(1)
        self.login_dialog.set_error_message()
        while True:
            if self.login_dialog.exec():
                username = self.login_dialog.username_lineEdit.text()
                password = self.login_dialog.password_lineEdit.text()
                if any(map(lambda x: x["username"] == username and x["password"] == password, self.config["users"])):
                    self.login_dialog.close()
                    if self.admin_panel is not None:
                        self.admin_panel.close()
                    self.admin_panel = AdminPanelWidget()
                    name = self.tabWidgetMain.tabText(self.tabWidgetMain.indexOf(self.tabWidgetMain.currentWidget()))
                    self.admin_panel.set_data(self.databases, self.config, self.connect_to_dbs,
                                              name, self.raise_encryption_exception,
                                              self.setup_functional_abilities, self.reload_paths_editor,
                                              self.connect_to_dbs)
                    self.admin_panel.create_elements()
                    break
                else:
                    self.login_dialog.set_error_message("Неверное имя пользователя или пароль!")
            else:
                self.login_dialog.close()
                break

    # Functional configuration of PyQt5 components
    # Enabling event handling of button clicks, etc.
    def setup_functional_abilities(self):
        # Creating menu on menubar
        self.menu = QtWidgets.QMenu("Меню", self)
        self.open_paths_editor_action = QtWidgets.QAction(QtGui.QIcon(EDITOR_ICON_PATH),
                                                "&Редактировать пути к БД", self)
        self.open_admin_panel_action = QtWidgets.QAction(QtGui.QIcon(ADMIN_PANEL_ICON_PATH),
                                                "&Панель управления", self)
        self.open_paths_editor_action.triggered.connect(self.exec_paths_editor)
        self.open_admin_panel_action.triggered.connect(self.exec_admin_panel)
        self.menu.addAction(self.open_paths_editor_action)
        self.menu.addAction(self.open_admin_panel_action)
        self.menubar.clear()
        self.menubar.addMenu(self.menu)

        # Creating tabs
        self.tabWidgetMain.clear()
        for tab in self.config["tabs"]:
            exec(f'self.tab{tab["tab_number"]} = SectionTabQWidget()')
            exec(f'self.tab{tab["tab_number"]}.setup_ui("{tab["tab_number"]}")')
            exec(f'self.tabWidgetMain.addTab(self.tab{tab["tab_number"]}, "")')
            exec(f'self.tabWidgetMain.setTabText(self.tabWidgetMain.indexOf(self.tab{tab["tab_number"]}), tab["name"])')

        # Setting up models of the history data tables
        for tab in self.config["tabs"]:
            tab_obj = eval(f'self.tab{tab["tab_number"]}')
            tab_obj.tableViewHistoryModel = widgets.table_models.UniversalTableModel()

            headers = ["Термин", "Синонимы", "Документы", "Определение"]
            section_resize_mods = {
                0: QtWidgets.QHeaderView.ResizeToContents,
                1: QtWidgets.QHeaderView.ResizeToContents,
                2: QtWidgets.QHeaderView.ResizeToContents,
                3: QtWidgets.QHeaderView.Stretch
            }

            tab_obj.tableViewHistoryModel.set_data([[""] * len(headers)])
            tab_obj.tableViewHistoryModel.set_horizontal_headers(headers)
            tab_obj.tableView.setTextElideMode(QtCore.Qt.ElideMiddle)
            tab_obj.tableView.setModel(tab_obj.tableViewHistoryModel)
            tab_obj.tableView.horizontalHeader().sectionResized.connect(tab_obj.tableView.resizeRowsToContents)
            tab_obj.tableView.setWordWrap(True)
            for i in section_resize_mods:
                tab_obj.tableView.horizontalHeader().setSectionResizeMode(i, section_resize_mods[i])

            # Connecting the buttons in its corresponding function
            tab_obj.pushButtonSearch.clicked.connect(self.push_button_search_clicked)

    # The function of searching for data from the first database when pressing connected button
    # It is implemented using eval and exec,
    # which allows it to be used repeatedly for different databases
    def push_button_search_clicked(self):
        order_name = self.tabWidgetMain.currentWidget().objectName()
        if self.databases[order_name]["exceptions"]["basic"] is not None:
            return
        tab_obj = self.tabWidgetMain.currentWidget()
        value = eval(f"tab_obj.lineEditSearch.text()")
        query = f'SELECT * FROM (SELECT DECRYPT(S.short) AS short, CUSTOMCONCAT(DECRYPT(A.abstraction)) AS abstraction, ' \
                f'CUSTOMCONCAT(DECRYPT(D.document)) AS document, DECRYPT(T.term) AS term ' \
                f'FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN terms_to_docs T_T_D ON ' \
                f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN abstractions A ON ' \
                f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN documents D ON ' \
                f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                f'GROUP BY T.term ' \
                f'ORDER BY S.short ASC)' \
                f'WHERE ((LOWER(short) LIKE "%{value.lower()}%" OR "{value.lower()}" LIKE ("%" || LOWER(short) || "%")) ' \
                f'OR (LOWER(abstraction) LIKE "%{value.lower()}%" OR "{value.lower()}" LIKE ("%" || LOWER(abstraction) || "%")))'
        cursor = eval(f"execute_query(self.databases['{order_name}']['connections']['basic'], query, "
                      f"(('DECRYPT', 1, sqlite_decrypt_constructor(self.databases['{order_name}']['secret_key'])),), "
                      f"(('CUSTOMCONCAT', 1, SqliteConcatStrings),))")
        data = cursor.fetchone()
        if data is None:
            exec(f'tab_obj.labelError.setText("Термина с таким названием нет в базе.")')
        else:
            exec(f"tab_obj.tableViewHistoryModel.append_row({list(data)})")
            exec(f"tab_obj.tableViewHistoryModel.layoutChanged.emit()")
            exec(f"tab_obj.tableView.resizeRowsToContents()")
            exec(f'tab_obj.textBrowserInfo.setText(data[3])')
            exec(f'tab_obj.labelError.setText("")')

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
    app = QtWidgets.QApplication(sys.argv)

    # Creating russian translator
    qtrn = QtCore.QTranslator()
    if QtCore.QLocale().name()[0:2] != 'en':
        qtrn.load('qtbase_' + QtCore.QLocale().name()[0:2],
                  QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
        app.installTranslator(qtrn)

    # Creating an instance of the main application window class
    ex = MainWindow()

    # Showing the main window to the user
    ex.show()

    # Completion of the script after the user closes the application
    sys.exit(app.exec_())
