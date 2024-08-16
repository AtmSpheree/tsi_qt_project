# -*- coding: utf-8 -*-
import sqlite3
import sys

# Setting packages path
sys.path.append('..')

# Import PyQT5 library components
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# Import interface classes
from ui_py.ui_admin_panel import Ui_MainWindow as Ui_AdminPanel
from ui_py.ui_record import Ui_Form as Ui_Record
from ui_py.ui_add_db import Ui_Form as Ui_AddDb
from ui_py.ui_change_db import Ui_Form as Ui_ChangeDb
from ui_py.ui_delete_db import Ui_Form as Ui_DeleteDb

# Import custom objects
from widgets import table_models
from widgets import dialogs

# Import built-in libraries
from functools import partial
from cryptography.fernet import Fernet
from pathlib import Path
import os
import json

# Import main constants
from main_constants import ADMIN_PANEL_ICON_PATH, DB_ICON_PATH, ICON_PATH, DIRNAME

# Import "misc" functions and objects
from misc import execute_query, delete_items_of_layout, encrypt_data, decrypt_data, get_max_table_id, \
    sqlite_decrypt_constructor, SqliteConcatStrings

# Import schema of the database
from db_schema import SCHEMA

# Import secret key of the config
from secret_key import SECRET_KEY


class RecordWidgetButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.string_value = ""

    def set_string_value(self, value: str):
        self.string_value = value

    def get_string_value(self):
        return self.string_value


class RecordWidgetCheckbox(QtWidgets.QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.string_value = ""

    def set_string_value(self, value: str):
        self.string_value = value

    def get_string_value(self):
        return self.string_value


# Record Widget for working with records from databases
class RecordWidget(Ui_Record, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/add_record.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_AddRedord) to this one
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(ADMIN_PANEL_ICON_PATH))

        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.lineEdit_abstractions = None
        self.lineEdit_shorts = None
        self.lineEdit_documents = None
        self.change_dialog = None
        self.is_closed = False

        # Showing widget to user
        self.show()

    def closeEvent(self, event):
        self.is_closed = True

    # Getting all synonyms, terms, abbreviations and documents
    # from the previously specified database
    def get_data_from_db(self):
        self.selected_data = {"abstractions": {"all": [], "selected": []},
                              "shorts": {"all": [], "selected": None},
                              "documents": {"all": [], "selected": []}}

        try:
            query = f'SELECT term FROM terms'
            self.selected_data["terms"] = sorted([decrypt_data(i[0].encode(), self.selected_db_key).decode()
                                                  for i in execute_query(self.db, query).fetchall()])

            query = f'SELECT abstraction FROM abstractions'
            self.selected_data["abstractions"]["all"] = sorted(
                [decrypt_data(i[0].encode(), self.selected_db_key).decode()
                 for i in execute_query(self.db, query).fetchall()])

            query = f'SELECT short FROM shorts'
            self.selected_data["shorts"]["all"] = sorted([decrypt_data(i[0].encode(), self.selected_db_key).decode()
                                                          for i in execute_query(self.db, query).fetchall()])

            query = f'SELECT document FROM documents'
            self.selected_data["documents"]["all"] = sorted([decrypt_data(i[0].encode(), self.selected_db_key).decode()
                                                             for i in execute_query(self.db, query).fetchall()])

            if self.is_changing:
                query = f'SELECT DECRYPT(term), DECRYPT(id) FROM terms WHERE DECRYPT(term) = "{self.record_data_term}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                term, term_id = cursor.fetchone()
                self.textBrowser_term.setText(term)

                query = f'SELECT DECRYPT(A.abstraction) FROM terms_to_abstractions T_T_A JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) WHERE DECRYPT(T_T_A.term_id) = "{term_id}"'
                self.selected_data["abstractions"]["selected"] = [i[0]
                                                                  for i in execute_query(self.db, query,
                                                                                         (('DECRYPT', 1,
                                                                                           sqlite_decrypt_constructor(
                                                                                               self.selected_db_key)),)).fetchall()]

                query = f'SELECT DECRYPT(S.short) FROM terms T JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                        f'WHERE DECRYPT(T.id) = "{term_id}"'
                self.selected_data["shorts"]["selected"] = execute_query(self.db, query,
                                                                         (('DECRYPT', 1, sqlite_decrypt_constructor(
                                                                             self.selected_db_key)),)).fetchone()[0]

                query = f'SELECT DECRYPT(D.document) FROM terms_to_docs T_T_D JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) WHERE DECRYPT(T_T_D.term_id) = "{term_id}"'
                self.selected_data["documents"]["selected"] = [i[0]
                                                               for i in execute_query(self.db, query,
                                                                                      (('DECRYPT', 1,
                                                                                        sqlite_decrypt_constructor(
                                                                                            self.selected_db_key)),)).fetchall()]
        except Exception as ex:
            self.raise_encryption_exception(self.selected_db_name)
            self.close()

    # Setting up the initial data
    def set_data(self, databases: dict, config: dict, reload_dbs, selected_db_name, raise_encryption_exception,
                 change_model, record_data_term=None, is_changing: bool = False):
        self.reload_dbs = reload_dbs
        self.databases = databases
        self.config = config
        self.selected_db_name = selected_db_name
        for tab in self.config["tabs"]:
            if tab["name"] == self.selected_db_name:
                self.selected_db_key = tab["secret_key"]
        self.record_data_term = record_data_term
        self.is_changing = is_changing
        if is_changing:
            self.pushButton_add.clicked.connect(self.change_record)
            self.setWindowTitle("Изменить запись")
            self.pushButton_add.setText("Изменить запись")
        else:
            self.pushButton_add.clicked.connect(self.add_record)
        self.raise_encryption_exception = raise_encryption_exception
        self.change_model = change_model
        self.selected_data = dict()

    def comboBox_changed(self):
        self.selected_db_name = self.comboBox_category.currentText()

        for tab in self.config["tabs"]:
            if tab["name"] == self.selected_db_name:
                self.selected_db_key = tab["secret_key"]

        for i in self.databases:
            if self.databases[i]["name"] == self.selected_db_name:
                self.db = self.databases[i]["connections"]["basic"]

        self.get_data_from_db()
        self.create_elements_abstractions()
        self.create_elements_shorts()
        self.create_elements_documents()

    def add_abstraction(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.setWindowTitle("Ошибка.")
        dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
        ok_button = dialog.addButton("ОК", QtWidgets.QMessageBox.AcceptRole)
        if self.lineEdit_abstractions.text() in self.selected_data["abstractions"]["all"]:
            text = {"text": "Синоним с таким названием уже существует."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        if ";" in self.lineEdit_abstractions.text():
            text = {"text": "Вы не можете использовать спецсимвол ';'."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        elif not self.lineEdit_abstractions.text():
            text = {"text": "Нельзя добавить пустую строку."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        try:
            value = encrypt_data(self.lineEdit_abstractions.text().encode(), self.selected_db_key)
            ident = encrypt_data(str(get_max_table_id(self.db, "abstractions", self.selected_db_key) + 1).encode(),
                                 self.selected_db_key)
            query = f'INSERT INTO abstractions(id, abstraction) VALUES ("{ident.decode()}", "{value.decode()}")'
            execute_query(self.db, query)
            self.db.commit()
            self.selected_data["abstractions"]["all"].append(self.lineEdit_abstractions.text())
            self.create_elements_abstractions()
        except Exception as ex:
            self.raise_encryption_exception(self.selected_db_name)
            self.close()

    def delete_abstraction(self):
        query = f'SELECT DECRYPT(T.term) FROM abstractions A JOIN terms_to_abstractions T_T_A ON ' \
                f'DECRYPT(A.id) = DECRYPT(T_T_A.abstraction_id) JOIN terms T ON ' \
                f'DECRYPT(T_T_A.term_id) = DECRYPT(T.id) WHERE DECRYPT(A.abstraction) = "{self.sender().get_string_value()}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        terms = [item[0] for item in cursor.fetchall()]
        if terms:
            if self.raise_delete_exception("abstraction", self.sender().get_string_value(), terms):
                return
            query = f'DELETE FROM terms_to_abstractions WHERE DECRYPT(abstraction_id) = ' \
                    f'(SELECT DECRYPT(id) FROM abstractions WHERE DECRYPT(abstraction) = "{self.sender().get_string_value()}")'
            execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        query = f'DELETE FROM abstractions WHERE DECRYPT(abstraction) = "{self.sender().get_string_value()}"'
        execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        self.db.commit()
        self.selected_data["abstractions"]["all"].remove(self.sender().get_string_value())
        if self.sender().get_string_value() in self.selected_data["abstractions"]["selected"]:
            self.selected_data["abstractions"]["selected"].remove(self.sender().get_string_value())
        self.create_elements_abstractions()

    def add_short(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.setWindowTitle("Ошибка.")
        dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
        ok_button = dialog.addButton("ОК", QtWidgets.QMessageBox.AcceptRole)
        if self.lineEdit_shorts.text() in self.selected_data["shorts"]["all"]:
            text = {"text": "Термин с таким названием уже существует."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        if ";" in self.lineEdit_shorts.text():
            text = {"text": "Вы не можете использовать спецсимвол ';'."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        elif not self.lineEdit_shorts.text():
            text = {"text": "Нельзя добавить пустую строку."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        try:
            value = encrypt_data(self.lineEdit_shorts.text().encode(), self.selected_db_key)
            ident = encrypt_data(str(get_max_table_id(self.db, "shorts", self.selected_db_key) + 1).encode(),
                                 self.selected_db_key)
            query = f'INSERT INTO shorts(id, short) VALUES ("{ident.decode()}", "{value.decode()}")'
            execute_query(self.db, query)
            self.db.commit()
            self.selected_data["shorts"]["all"].append(self.lineEdit_shorts.text())
            self.create_elements_shorts()
        except Exception as ex:
            self.raise_encryption_exception(self.selected_db_name)
            self.close()

    def delete_short(self):
        query = f'SELECT DECRYPT(term) FROM terms WHERE DECRYPT(short_id) = ' \
                f'(SELECT DECRYPT(id) FROM shorts WHERE DECRYPT(short) = "{self.sender().get_string_value()}")'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        terms = [item[0] for item in cursor.fetchall()]
        if terms:
            if self.raise_delete_exception("short", self.sender().get_string_value(), terms):
                return
            query = f'SELECT DECRYPT(id) FROM terms WHERE DECRYPT(short_id) = ' \
                    f'(SELECT DECRYPT(id) FROM shorts WHERE DECRYPT(short) = "{self.sender().get_string_value()}")'
            cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
            term_ids = [item[0] for item in cursor.fetchall()]
            for ident in term_ids:
                query = f'SELECT DECRYPT(term) FROM terms WHERE DECRYPT(id) = "{ident}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                term = cursor.fetchone()[0]
                if term in self.selected_data["terms"]:
                    self.selected_data["terms"].remove(term)

                query = f'DELETE FROM terms_to_abstractions WHERE DECRYPT(term_id) = "{ident}"'
                execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))

                query = f'DELETE FROM terms_to_docs WHERE DECRYPT(term_id) = "{ident}"'
                execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))

            query = f'DELETE FROM terms WHERE DECRYPT(short_id) = ' \
                    f'(SELECT DECRYPT(id) FROM shorts WHERE DECRYPT(short) = "{self.sender().get_string_value()}")'
            execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        query = f'DELETE FROM shorts WHERE DECRYPT(short) = "{self.sender().get_string_value()}"'
        execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        self.db.commit()
        self.selected_data["shorts"]["all"].remove(self.sender().get_string_value())
        if self.sender().get_string_value() == self.selected_data["shorts"]["selected"]:
            self.selected_data["shorts"]["selected"] = None
        self.create_elements_shorts()

    def add_document(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.setWindowTitle("Ошибка.")
        dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
        ok_button = dialog.addButton("ОК", QtWidgets.QMessageBox.AcceptRole)
        if self.lineEdit_documents.text() in self.selected_data["documents"]["all"]:
            text = {"text": "Документ с таким названием уже существует."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        if ";" in self.lineEdit_documents.text():
            text = {"text": "Вы не можете использовать спецсимвол ';'."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        elif not self.lineEdit_documents.text():
            text = {"text": "Нельзя добавить пустую строку."}
            dialog.setText(text["text"])
            dialog.exec_()
            return
        try:
            value = encrypt_data(self.lineEdit_documents.text().encode(), self.selected_db_key)
            ident = encrypt_data(str(get_max_table_id(self.db, "documents", self.selected_db_key) + 1).encode(),
                                 self.selected_db_key)
            query = f'INSERT INTO documents(id, document) VALUES ("{ident.decode()}", "{value.decode()}")'
            execute_query(self.db, query)
            self.db.commit()
            self.selected_data["documents"]["all"].append(self.lineEdit_documents.text())
            self.create_elements_documents()
        except Exception as ex:
            self.raise_encryption_exception(self.selected_db_name)
            self.close()

    def delete_document(self):
        query = f'SELECT DECRYPT(T.term) FROM documents D JOIN terms_to_docs T_T_D ON ' \
                f'DECRYPT(D.id) = DECRYPT(T_T_D.document_id) JOIN terms T ON ' \
                f'DECRYPT(T_T_D.term_id) = DECRYPT(T.id) WHERE DECRYPT(D.document) = "{self.sender().get_string_value()}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        terms = [item[0] for item in cursor.fetchall()]
        if terms:
            if self.raise_delete_exception("document", self.sender().get_string_value(), terms):
                return

            query = f'SELECT DECRYPT(term_id) FROM terms_to_docs WHERE DECRYPT(document_id) = ' \
                    f'(SELECT DECRYPT(id) FROM documents WHERE DECRYPT(document) = "{self.sender().get_string_value()}")'
            cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
            term_ids = [item[0] for item in cursor.fetchall()]

            for ident in term_ids:
                query = f'SELECT id FROM terms_to_docs WHERE DECRYPT(term_id) = "{ident}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                docs = [item[0] for item in cursor.fetchall()]
                if len(docs) == 1:
                    query = f'SELECT DECRYPT(term) FROM terms WHERE DECRYPT(id) = "{ident}"'
                    cursor = execute_query(self.db, query,
                                           (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                    term = cursor.fetchone()[0]
                    if term in self.selected_data["terms"]:
                        self.selected_data["terms"].remove(term)

                    query = f'DELETE FROM terms WHERE DECRYPT(id) = "{ident}"'
                    execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))

                    query = f'DELETE FROM terms_to_abstractions WHERE DECRYPT(term_id) = "{ident}"'
                    execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))

            query = f'DELETE FROM terms_to_docs WHERE DECRYPT(document_id) = ' \
                    f'(SELECT DECRYPT(id) FROM documents WHERE DECRYPT(document) = "{self.sender().get_string_value()}")'
            execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        query = f'DELETE FROM documents WHERE DECRYPT(document) = "{self.sender().get_string_value()}"'
        execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        self.db.commit()
        self.selected_data["documents"]["all"].remove(self.sender().get_string_value())
        if self.sender().get_string_value() in self.selected_data["documents"]["selected"]:
            self.selected_data["documents"]["selected"].remove(self.sender().get_string_value())
        self.create_elements_documents()

    def change_abstraction(self):
        if self.change_dialog is not None:
            self.change_dialog.close()
        self.change_dialog = dialogs.EnterValueDialog()
        self.change_dialog.set_functional_abilities()
        self.change_dialog.set_additional_padding_to_buttons(1)
        self.change_dialog.set_error_message()
        self.change_dialog.set_text_label("Введите новое значение синонима:")
        self.change_dialog.set_line_edit_value(self.sender().get_string_value())
        while True:
            if self.change_dialog.exec():
                value = self.change_dialog.value_lineEdit.text()
                if not value:
                    self.change_dialog.set_error_message("Введите непустое значение.")
                    continue
                if ";" in value:
                    self.change_dialog.set_error_message("Вы не можете использовать спецсимвол ';'.")
                    continue
                if value == self.sender().get_string_value():
                    self.change_dialog.set_error_message("Введите значение, отличное от исходного.")
                    continue
                query = f'SELECT id FROM abstractions WHERE DECRYPT(abstraction) = "{value}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                if cursor.fetchall():
                    self.change_dialog.set_error_message("Такой синоним уже существует.")
                    continue
                query = f'UPDATE abstractions SET abstraction = ' \
                        f'"{encrypt_data(value.encode(), self.selected_db_key).decode()}" WHERE DECRYPT(abstraction) = ' \
                        f'"{self.sender().get_string_value()}"'
                execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                self.db.commit()
                self.change_dialog.set_error_message("Успешно.")
                self.selected_data["abstractions"]["all"][
                    self.selected_data["abstractions"]["all"].index(self.sender().get_string_value())] = value
                if self.sender().get_string_value() in self.selected_data["abstractions"]["selected"]:
                    self.selected_data["abstractions"]["selected"][
                        self.selected_data["abstractions"]["selected"].index(self.sender().get_string_value())] = value
                self.change_model()
                self.create_elements_abstractions()
                break
            else:
                self.change_dialog.close()
                self.change_dialog = None
                break

    def change_abstraction_text(self):
        self.create_elements_abstractions()

    def change_abstraction_checkbox(self):
        if self.sender().get_string_value() in self.selected_data["abstractions"]["selected"]:
            self.selected_data["abstractions"]["selected"].remove(self.sender().get_string_value())
        else:
            self.selected_data["abstractions"]["selected"].append(self.sender().get_string_value())
        self.selected_data["abstractions"]["selected"].sort()

    def change_short(self):
        if self.change_dialog is not None:
            self.change_dialog.close()
        self.change_dialog = dialogs.EnterValueDialog()
        self.change_dialog.set_functional_abilities()
        self.change_dialog.set_additional_padding_to_buttons(1)
        self.change_dialog.set_error_message()
        self.change_dialog.set_text_label("Введите новое значение термина:")
        self.change_dialog.set_line_edit_value(self.sender().get_string_value())
        while True:
            if self.change_dialog.exec():
                value = self.change_dialog.value_lineEdit.text()
                if not value:
                    self.change_dialog.set_error_message("Введите непустое значение.")
                    continue
                if ";" in value:
                    self.change_dialog.set_error_message("Вы не можете использовать спецсимвол ';'.")
                    continue
                if value == self.sender().get_string_value():
                    self.change_dialog.set_error_message("Введите значение, отличное от исходного.")
                    continue
                query = f'SELECT id FROM shorts WHERE DECRYPT(short) = "{value}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                if cursor.fetchall():
                    self.change_dialog.set_error_message("Такой термин уже существует.")
                    continue
                query = f'UPDATE shorts SET short = ' \
                        f'"{encrypt_data(value.encode(), self.selected_db_key).decode()}" WHERE DECRYPT(short) = ' \
                        f'"{self.sender().get_string_value()}"'
                execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                self.db.commit()
                self.change_dialog.set_error_message("Успешно.")
                self.selected_data["shorts"]["all"][
                    self.selected_data["shorts"]["all"].index(self.sender().get_string_value())] = value
                if self.sender().get_string_value() == self.selected_data["shorts"]["selected"]:
                    self.selected_data["shorts"]["selected"] = value
                self.change_model()
                self.create_elements_shorts()
                break
            else:
                self.change_dialog.close()
                self.change_dialog = None
                break

    def change_short_text(self):
        self.create_elements_shorts()

    def change_short_checkbox(self):
        if self.sender().get_string_value() == self.selected_data["shorts"]["selected"]:
            self.selected_data["shorts"]["selected"] = None
        else:
            self.selected_data["shorts"]["selected"] = self.sender().get_string_value()
        self.create_elements_shorts()

    def change_document(self):
        if self.change_dialog is not None:
            self.change_dialog.close()
        self.change_dialog = dialogs.EnterValueDialog()
        self.change_dialog.set_functional_abilities()
        self.change_dialog.set_additional_padding_to_buttons(1)
        self.change_dialog.set_error_message()
        self.change_dialog.set_text_label("Введите новое значение документа:")
        self.change_dialog.set_line_edit_value(self.sender().get_string_value())
        while True:
            if self.change_dialog.exec():
                value = self.change_dialog.value_lineEdit.text()
                if not value:
                    self.change_dialog.set_error_message("Введите непустое значение.")
                    continue
                if ";" in value:
                    self.change_dialog.set_error_message("Вы не можете использовать спецсимвол ';'.")
                    continue
                if value == self.sender().get_string_value():
                    self.change_dialog.set_error_message("Введите значение, отличное от исходного.")
                    continue
                query = f'SELECT id FROM documents WHERE DECRYPT(document) = "{value}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                if cursor.fetchall():
                    self.change_dialog.set_error_message("Такой документ уже существует.")
                    continue
                query = f'UPDATE documents SET document = ' \
                        f'"{encrypt_data(value.encode(), self.selected_db_key).decode()}" WHERE DECRYPT(document) = ' \
                        f'"{self.sender().get_string_value()}"'
                execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                self.db.commit()
                self.change_dialog.set_error_message("Успешно.")
                self.selected_data["documents"]["all"][
                    self.selected_data["documents"]["all"].index(self.sender().get_string_value())] = value
                if self.sender().get_string_value() in self.selected_data["documents"]["selected"]:
                    self.selected_data["documents"]["selected"][
                        self.selected_data["documents"]["selected"].index(self.sender().get_string_value())] = value
                self.change_model()
                self.create_elements_documents()
                break
            else:
                self.change_dialog.close()
                self.change_dialog = None
                break

    def change_document_text(self):
        self.create_elements_documents()

    def change_document_checkbox(self):
        if self.sender().get_string_value() in self.selected_data["documents"]["selected"]:
            self.selected_data["documents"]["selected"].remove(self.sender().get_string_value())
        else:
            self.selected_data["documents"]["selected"].append(self.sender().get_string_value())
        self.selected_data["documents"]["selected"].sort()

    def create_category_combobox(self):
        # Adding databases names in combobox widget
        self.comboBox_category.clear()
        combobox_list = list(map(lambda x: x["name"],
                                 filter(lambda x: x["exceptions"]["basic"] is None, self.databases.values())))
        if self.selected_db_name is not None:
            if self.selected_db_name in combobox_list:
                self.comboBox_category.addItem(self.selected_db_name)
        for db in combobox_list:
            if self.selected_db_name is not None:
                if db == self.selected_db_name:
                    continue
            self.comboBox_category.addItem(db)

        if self.is_changing:
            self.comboBox_category.setEnabled(False)

        self.comboBox_category.currentTextChanged.connect(self.comboBox_changed)

        self.comboBox_changed()

    def create_elements_abstractions(self):
        # Abstractions
        # Creating search layout
        if self.lineEdit_abstractions is None:
            verticalLayout = QtWidgets.QVBoxLayout(self.scrollArea_abstractions_contents)

            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

            self.lineEdit_abstractions = QtWidgets.QLineEdit()
            self.lineEdit_abstractions.setPlaceholderText("Введите текст для поиска")
            self.lineEdit_abstractions.setFont(self.font)
            self.lineEdit_abstractions.textChanged.connect(self.change_abstraction_text)
            horizontalLayout.addWidget(self.lineEdit_abstractions)

            self.pushButton_abstractions = QtWidgets.QPushButton()
            self.pushButton_abstractions.setFixedWidth(25)
            self.pushButton_abstractions.setFixedHeight(25)
            self.pushButton_abstractions.setText("+")
            self.pushButton_abstractions.setFont(self.font)
            self.pushButton_abstractions.clicked.connect(self.add_abstraction)
            horizontalLayout.addWidget(self.pushButton_abstractions)

            verticalLayout.addLayout(horizontalLayout)

            # Creating abstractions layout
            self.abstractions_layout = QtWidgets.QVBoxLayout()
            verticalLayout.addLayout(self.abstractions_layout)
        else:
            # Cleaning abstractions layout
            delete_items_of_layout(self.abstractions_layout)

        # Creating items
        data = self.selected_data["abstractions"]["all"]
        if self.lineEdit_abstractions.text():
            text = self.lineEdit_abstractions.text()
            data = [i for i in data if text in i or i in text]

        for abstraction in data:
            horizontalLayout = QtWidgets.QHBoxLayout()

            checkbox = RecordWidgetCheckbox()
            checkbox.set_string_value(abstraction)
            checkbox.clicked.connect(self.change_abstraction_checkbox)
            if abstraction in self.selected_data["abstractions"]["selected"]:
                checkbox.setChecked(True)
            horizontalLayout.addWidget(checkbox)

            label = QtWidgets.QLabel(abstraction)
            label.setFont(self.font)
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            horizontalLayout.addWidget(label)

            pushButton = RecordWidgetButton()
            pushButton.set_string_value(abstraction)
            pushButton.setFixedWidth(25)
            pushButton.setFixedHeight(25)
            pushButton.setText("/")
            pushButton.setFont(self.font)
            pushButton.clicked.connect(self.change_abstraction)
            horizontalLayout.addWidget(pushButton)

            pushButton = RecordWidgetButton()
            pushButton.set_string_value(abstraction)
            pushButton.setFixedWidth(25)
            pushButton.setFixedHeight(25)
            pushButton.setText("-")
            pushButton.setFont(self.font)
            pushButton.clicked.connect(self.delete_abstraction)
            horizontalLayout.addWidget(pushButton)

            self.abstractions_layout.addLayout(horizontalLayout)

        # Spacer item for top alignment
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.abstractions_layout.addItem(spacerItem)

    def create_elements_shorts(self):
        # Shorts
        # Creating search layout
        if self.lineEdit_shorts is None:
            verticalLayout = QtWidgets.QVBoxLayout(self.scrollArea_short_contents)

            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

            self.lineEdit_shorts = QtWidgets.QLineEdit()
            self.lineEdit_shorts.setPlaceholderText("Введите текст для поиска")
            self.lineEdit_shorts.setFont(self.font)
            self.lineEdit_shorts.textChanged.connect(self.change_short_text)
            horizontalLayout.addWidget(self.lineEdit_shorts)

            self.pushButton_shorts = QtWidgets.QPushButton()
            self.pushButton_shorts.setFixedWidth(25)
            self.pushButton_shorts.setFixedHeight(25)
            self.pushButton_shorts.setText("+")
            self.pushButton_shorts.setFont(self.font)
            self.pushButton_shorts.clicked.connect(self.add_short)
            horizontalLayout.addWidget(self.pushButton_shorts)

            verticalLayout.addLayout(horizontalLayout)

            # Creating shorts layout
            self.shorts_layout = QtWidgets.QVBoxLayout()
            verticalLayout.addLayout(self.shorts_layout)
        else:
            # Cleaning shorts layout
            delete_items_of_layout(self.shorts_layout)

        # Creating items
        data = self.selected_data["shorts"]["all"]
        if self.lineEdit_shorts.text():
            text = self.lineEdit_shorts.text()
            data = [i for i in data if text in i or i in text]

        for short in data:
            horizontalLayout = QtWidgets.QHBoxLayout()

            checkbox = RecordWidgetCheckbox()
            checkbox.set_string_value(short)
            checkbox.clicked.connect(self.change_short_checkbox)
            if short == self.selected_data["shorts"]["selected"]:
                checkbox.setChecked(True)
            horizontalLayout.addWidget(checkbox)

            label = QtWidgets.QLabel(short)
            label.setFont(self.font)
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            horizontalLayout.addWidget(label)

            pushButton = RecordWidgetButton()
            pushButton.set_string_value(short)
            pushButton.setFixedWidth(25)
            pushButton.setFixedHeight(25)
            pushButton.setText("/")
            pushButton.setFont(self.font)
            pushButton.clicked.connect(self.change_short)
            horizontalLayout.addWidget(pushButton)

            pushButton = RecordWidgetButton()
            pushButton.set_string_value(short)
            pushButton.setFixedWidth(25)
            pushButton.setFixedHeight(25)
            pushButton.setText("-")
            pushButton.setFont(self.font)
            pushButton.clicked.connect(self.delete_short)
            horizontalLayout.addWidget(pushButton)

            self.shorts_layout.addLayout(horizontalLayout)

        # Spacer item for top alignment
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.shorts_layout.addItem(spacerItem)

    def create_elements_documents(self):
        # Documents
        # Creating search layout
        if self.lineEdit_documents is None:
            verticalLayout = QtWidgets.QVBoxLayout(self.scrollArea_documents_contents)

            horizontalLayout = QtWidgets.QHBoxLayout()
            horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

            self.lineEdit_documents = QtWidgets.QLineEdit()
            self.lineEdit_documents.setPlaceholderText("Введите текст для поиска")
            self.lineEdit_documents.setFont(self.font)
            self.lineEdit_documents.textChanged.connect(self.change_document_text)
            horizontalLayout.addWidget(self.lineEdit_documents)

            self.pushButton_documents = QtWidgets.QPushButton()
            self.pushButton_documents.setFixedWidth(25)
            self.pushButton_documents.setFixedHeight(25)
            self.pushButton_documents.setText("+")
            self.pushButton_documents.setFont(self.font)
            self.pushButton_documents.clicked.connect(self.add_document)
            horizontalLayout.addWidget(self.pushButton_documents)

            verticalLayout.addLayout(horizontalLayout)

            # Creating documents layout
            self.documents_layout = QtWidgets.QVBoxLayout()
            verticalLayout.addLayout(self.documents_layout)
        else:
            # Cleaning documents layout
            delete_items_of_layout(self.documents_layout)

        # Creating items
        data = self.selected_data["documents"]["all"]
        if self.lineEdit_documents.text():
            text = self.lineEdit_documents.text()
            data = [i for i in data if text in i or i in text]

        for document in data:
            horizontalLayout = QtWidgets.QHBoxLayout()

            checkbox = RecordWidgetCheckbox()
            checkbox.set_string_value(document)
            checkbox.clicked.connect(self.change_document_checkbox)
            if document in self.selected_data["documents"]["selected"]:
                checkbox.setChecked(True)
            horizontalLayout.addWidget(checkbox)

            label = QtWidgets.QLabel(document)
            label.setFont(self.font)
            label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            horizontalLayout.addWidget(label)

            pushButton = RecordWidgetButton()
            pushButton.set_string_value(document)
            pushButton.setFixedWidth(25)
            pushButton.setFixedHeight(25)
            pushButton.setText("/")
            pushButton.setFont(self.font)
            pushButton.clicked.connect(self.change_document)
            horizontalLayout.addWidget(pushButton)

            pushButton = RecordWidgetButton()
            pushButton.set_string_value(document)
            pushButton.setFixedWidth(25)
            pushButton.setFixedHeight(25)
            pushButton.setText("-")
            pushButton.setFont(self.font)
            pushButton.clicked.connect(self.delete_document)
            horizontalLayout.addWidget(pushButton)

            self.documents_layout.addLayout(horizontalLayout)

        # Spacer item for top alignment
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.documents_layout.addItem(spacerItem)

    def change_record(self):
        term = self.textBrowser_term.toPlainText().replace("\n", " ")
        if not term:
            self.label_error.setText("Введите определение.")
            return
        elif term in self.selected_data["terms"] and term != self.record_data_term:
            self.label_error.setText("Такое определение уже существует.")
            return
        elif not self.selected_data["shorts"]["selected"]:
            self.label_error.setText("Выберите один термин.")
            return
        elif not self.selected_data["documents"]["selected"]:
            self.label_error.setText("Выберите хотя бы один документ.")
            return
        query = f'SELECT DECRYPT(S.short) FROM terms T JOIN shorts S ON ' \
                f'DECRYPT(T.short_id) = DECRYPT(S.id) WHERE DECRYPT(T.term) = "{self.record_data_term}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        short = cursor.fetchone()[0]
        query = f'SELECT DECRYPT(D.document) FROM shorts S JOIN terms T ON ' \
                f'DECRYPT(S.id) = DECRYPT(T.short_id) JOIN terms_to_docs T_T_D ON ' \
                f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN documents D ON ' \
                f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id)' \
                f'WHERE DECRYPT(short) = "{self.selected_data["shorts"]["selected"]}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        if (set([i[0] for i in cursor.fetchall()]) & set(self.selected_data["documents"]["selected"]) and
                short != self.selected_data["shorts"]["selected"]):
            self.label_error.setText("Выбранный термин уже содержится в выбранных документах.")
            return
        query = f'SELECT DECRYPT(id) FROM shorts WHERE DECRYPT(short) = "{self.selected_data["shorts"]["selected"]}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        short_id = encrypt_data(cursor.fetchone()[0].encode(), self.selected_db_key).decode()
        value = encrypt_data(term.encode(), self.selected_db_key)
        query = f'UPDATE terms SET term = "{encrypt_data(term.encode(), self.selected_db_key).decode()}", ' \
                f'short_id = "{short_id}" WHERE DECRYPT(term) = "{self.record_data_term}"'
        execute_query(self.db, query,
                      (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        query = f'SELECT DECRYPT(id) FROM terms WHERE DECRYPT(term) = "{term}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        term_id = cursor.fetchone()[0]
        query = f'SELECT DECRYPT(A.abstraction) FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN abstractions A ON ' \
                f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) WHERE DECRYPT(T.term) = "{term}"'
        cursor = execute_query(self.db, query,
                               (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        abstractions = [i[0] for i in cursor.fetchall()]
        ident = get_max_table_id(self.db, "terms_to_abstractions", self.selected_db_key) + 1
        for abstraction in self.selected_data["abstractions"]["selected"]:
            if abstraction not in abstractions:
                query = f'SELECT DECRYPT(id) FROM abstractions WHERE DECRYPT(abstraction) = "{abstraction}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                abstraction_ident = encrypt_data(cursor.fetchone()[0].encode(), self.selected_db_key).decode()
                query = f'INSERT INTO terms_to_abstractions(id, term_id, abstraction_id) VALUES ' \
                        f'("{encrypt_data(str(ident).encode(), self.selected_db_key).decode()}", ' \
                        f'"{encrypt_data(str(term_id).encode(), self.selected_db_key).decode()}", "{abstraction_ident}")'
                execute_query(self.db, query)
                ident += 1
        for abstraction in abstractions:
            if abstraction not in self.selected_data["abstractions"]["selected"]:
                query = f'SELECT DECRYPT(id) FROM abstractions WHERE DECRYPT(abstraction) = "{abstraction}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                abstraction_ident = cursor.fetchone()[0]
                query = f'DELETE FROM terms_to_abstractions WHERE ' \
                        f'(DECRYPT(abstraction_id) = "{abstraction_ident}" AND DECRYPT(term_id) = "{term_id}")'
                execute_query(self.db, query)
        query = f'SELECT DECRYPT(D.document) FROM terms T JOIN terms_to_docs T_T_D ON ' \
                f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN documents D ON ' \
                f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) WHERE DECRYPT(T.term) = "{term}"'
        cursor = execute_query(self.db, query,
                               (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        documents = [i[0] for i in cursor.fetchall()]
        ident = get_max_table_id(self.db, "terms_to_docs", self.selected_db_key) + 1
        for document in self.selected_data["documents"]["selected"]:
            if document not in documents:
                query = f'SELECT DECRYPT(id) FROM documents WHERE DECRYPT(document) = "{document}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                document_ident = encrypt_data(cursor.fetchone()[0].encode(), self.selected_db_key).decode()
                query = f'INSERT INTO terms_to_docs(id, term_id, document_id) VALUES ' \
                        f'("{encrypt_data(str(ident).encode(), self.selected_db_key).decode()}", ' \
                        f'"{encrypt_data(str(term_id).encode(), self.selected_db_key).decode()}", "{document_ident}")'
                execute_query(self.db, query)
                ident += 1
        for document in documents:
            if document not in self.selected_data["documents"]["selected"]:
                query = f'SELECT DECRYPT(id) FROM documents WHERE DECRYPT(document) = "{document}"'
                cursor = execute_query(self.db, query,
                                       (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
                document_ident = cursor.fetchone()[0]
                query = f'DELETE FROM terms_to_docs WHERE ' \
                        f'(DECRYPT(document_id) = "{document_ident}" AND DECRYPT(term_id) = "{term_id}")'
                execute_query(self.db, query)
        self.db.commit()
        self.record_data_term = term
        self.selected_data["terms"][self.selected_data["terms"].index(self.record_data_term)] = term
        self.change_model()
        self.label_error.setText("Успешно.")

    def add_record(self):
        term = self.textBrowser_term.toPlainText().replace("\n", " ")
        if not term:
            self.label_error.setText("Введите определение.")
            return
        elif term in self.selected_data["terms"]:
            self.label_error.setText("Такое определение уже существует.")
            return
        elif not self.selected_data["shorts"]["selected"]:
            self.label_error.setText("Выберите один термин.")
            return
        elif not self.selected_data["documents"]["selected"]:
            self.label_error.setText("Выберите хотя бы один документ.")
            return
        query = f'SELECT DECRYPT(D.document) FROM shorts S JOIN terms T ON ' \
                f'DECRYPT(S.id) = DECRYPT(T.short_id) JOIN terms_to_docs T_T_D ON ' \
                f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN documents D ON ' \
                f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id)' \
                f'WHERE DECRYPT(short) = "{self.selected_data["shorts"]["selected"]}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        if set([i[0] for i in cursor.fetchall()]) & set(self.selected_data["documents"]["selected"]):
            self.label_error.setText("Выбранный термин уже содержится в выбранных документах.")
            return
        query = f'SELECT DECRYPT(id) FROM shorts WHERE DECRYPT(short) = "{self.selected_data["shorts"]["selected"]}"'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        short_id = encrypt_data(cursor.fetchone()[0].encode(), self.selected_db_key).decode()
        value = encrypt_data(term.encode(), self.selected_db_key)
        term_ident = get_max_table_id(self.db, "terms", self.selected_db_key) + 1
        query = f'INSERT INTO terms(id, term, short_id) VALUES ' \
                f'("{encrypt_data(str(term_ident).encode(), self.selected_db_key).decode()}", "{value.decode()}", "{short_id}")'
        execute_query(self.db, query)
        ident = get_max_table_id(self.db, "terms_to_abstractions", self.selected_db_key) + 1
        for abstraction in self.selected_data["abstractions"]["selected"]:
            query = f'SELECT DECRYPT(id) FROM abstractions WHERE DECRYPT(abstraction) = "{abstraction}"'
            cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
            abstraction_ident = encrypt_data(cursor.fetchone()[0].encode(), self.selected_db_key).decode()
            query = f'INSERT INTO terms_to_abstractions(id, term_id, abstraction_id) VALUES ' \
                    f'("{encrypt_data(str(ident).encode(), self.selected_db_key).decode()}", ' \
                    f'"{encrypt_data(str(term_ident).encode(), self.selected_db_key).decode()}", "{abstraction_ident}")'
            execute_query(self.db, query)
            ident += 1
        ident = get_max_table_id(self.db, "terms_to_docs", self.selected_db_key) + 1
        for document in self.selected_data["documents"]["selected"]:
            query = f'SELECT DECRYPT(id) FROM documents WHERE DECRYPT(document) = "{document}"'
            cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
            document_ident = encrypt_data(cursor.fetchone()[0].encode(), self.selected_db_key).decode()
            query = f'INSERT INTO terms_to_docs(id, term_id, document_id) VALUES ' \
                    f'("{encrypt_data(str(ident).encode(), self.selected_db_key).decode()}", ' \
                    f'"{encrypt_data(str(term_ident).encode(), self.selected_db_key).decode()}", "{document_ident}")'
            execute_query(self.db, query)
            ident += 1
        self.db.commit()
        self.selected_data["terms"].append(term)
        self.change_model()
        self.label_error.setText("Успешно.")

    def raise_delete_exception(self, type: str, name, error_items):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.setWindowTitle("Предупреждение.")
        dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
        ok_button = dialog.addButton("ОK", QtWidgets.QMessageBox.AcceptRole)
        cancel_button = dialog.addButton("Отмена", QtWidgets.QMessageBox.RejectRole)
        if type == "document":
            text = {"text": "Удаление документа.",
                    "description_text": f'Документ "{name}" подкреплён к одному или нескольким определениям. '
                                        f'Удалив его, вы собираетесь удалить все вхождения этого документа в '
                                        f'привязанные к нему определения (см. ниже).\n'
                                        f'!!! А ТАКЖЕ САМИ ПРИВЯЗАННЫЕ ОПРЕДЕЛЕНИЯ, В СЛУЧАЕ, '
                                        f'ЕСЛИ ПРИВЯЗАННЫЙ ДОКУМЕНТ БЫЛ ЕДИНСТВЕННЫМ !!!\n'
                                        f'Вы хотите продолжить?'}
        elif type == "short":
            text = {"text": "Удаление термина.",
                    "description_text": f'Термин "{name}" подкреплён к одному или нескольким определениям. '
                                        f'Удалив его, вы собираетесь удалить все вхождения этого термина в '
                                        f'привязанные к нему определения (см. ниже).\n'
                                        f'!!! А ТАКЖЕ САМИ ПРИВЯЗАННЫЕ ОПРЕДЕЛЕНИЯ !!!\n'
                                        f'Вы хотите продолжить?'}
        elif type == "abstraction":
            text = {"text": "Удаление синонима.",
                    "description_text": f'Синоним "{name}" подкреплён к одному или нескольким определениям. '
                                        f'Удалив его, вы собираетесь удалить все вхождения этого синонима в '
                                        f'привязанные к нему определения (см. ниже). Вы хотите продолжить?'}
        else:
            raise Exception(f'"type" parameter of "raise_delete_exception" method is not specified.')
        dialog.setText(text["text"])
        dialog.setInformativeText(text["description_text"])
        dialog.setDetailedText("\n".join(error_items))
        return dialog.exec_()


# Add db Widget for working with adding new databases
class AddDbWidget(Ui_AddDb, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/add_db.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_AddDb) to this one
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(DB_ICON_PATH))

        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.is_closed = False
        self.existing_bd_con = None

        # Showing widget to user
        self.show()

    def closeEvent(self, event):
        self.is_closed = True

    def set_data(self, config, databases, reload_app_for_new_bd):
        self.config = config
        self.databases = databases
        self.reload_app_for_new_bd = reload_app_for_new_bd

    def setup_functional_abilities(self):
        self.pushButton_generate_key.clicked.connect(self.generate_new_key)
        self.buttonGroup_is_create.buttonClicked.connect(self.change_db_path_type)
        self.pushButton_submit.clicked.connect(self.add_db)
        self.pushButton_select_new_bd.clicked.connect(self.point_out_db_path)
        self.pushButton_select_existing_bd.clicked.connect(self.point_out_db_path)
        self.checkBox_is_relative.clicked.connect(self.on_click_checkbox)

    def generate_new_key(self):
        self.lineEdit_key.setText(Fernet.generate_key().decode())

    def change_db_path_type(self, button):
        btn_type = button.objectName()
        if btn_type == "radioButton_create_new_bd":
            self.lineEdit_new_bd_path.setEnabled(True)
            self.pushButton_select_new_bd.setEnabled(True)
            self.lineEdit_existing_bd_path.setEnabled(False)
            self.pushButton_select_existing_bd.setEnabled(False)
        elif btn_type == "radioButton_select_existing_bd":
            self.lineEdit_new_bd_path.setEnabled(False)
            self.pushButton_select_new_bd.setEnabled(False)
            self.lineEdit_existing_bd_path.setEnabled(True)
            self.pushButton_select_existing_bd.setEnabled(True)

    def add_db(self):
        if not self.lineEdit_title.text():
            self.label_error.setText("Ошибка. Введите название дисциплины.")
            return
        elif self.lineEdit_title.text() in map(lambda x: x["name"], self.config["tabs"]):
            self.label_error.setText("Ошибка. Дисциплина с таким названием уже существует.")
            return
        if not self.lineEdit_key.text():
            self.label_error.setText("Ошибка. Сгенерируйте ключ шифрования или введите его вручную.")
            return
        else:
            try:
                Fernet(self.lineEdit_key.text().encode()).encrypt(b"123")
            except Exception:
                self.label_error.setText("Ошибка. Ключ шифрования не является действительным.")
                return
        if not self.config["tabs"]:
            number = 1
        else:
            number = max(map(lambda x: x["tab_number"], self.config["tabs"])) + 1
        if self.radioButton_create_new_bd.isChecked():
            if not self.lineEdit_new_bd_path.text():
                self.label_error.setText("Ошибка. Укажите путь к базе данных.")
                return
            filename = self.lineEdit_new_bd_path.text()
            if self.checkBox_is_relative.isChecked():
                filename = str((DIRNAME / filename).resolve())
            connection = sqlite3.connect(filename)
            cursor = connection.cursor()
            for query in SCHEMA:
                cursor.execute(query)
            connection.commit()
            self.config["tabs"].append({"name": self.lineEdit_title.text(),
                                        "tab_number": number,
                                        "db_paths": {
                                            "basic": {"path": self.lineEdit_new_bd_path.text(),
                                                      "is_relative": self.checkBox_is_relative.isChecked()},
                                            "additional": []
                                        },
                                        "secret_key": self.lineEdit_key.text()})
        elif self.radioButton_select_existing_bd.isChecked():
            if not self.lineEdit_existing_bd_path.text():
                self.label_error.setText("Ошибка. Укажите путь к базе данных.")
                return
            filename = self.lineEdit_existing_bd_path.text()
            if self.checkBox_is_relative.isChecked():
                filename = str((DIRNAME / filename).resolve())
            try:
                connection = sqlite3.connect(filename)
                try:
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
                                           (('DECRYPT', 1, sqlite_decrypt_constructor(self.lineEdit_key.text())),),
                                           (('CUSTOMCONCAT', 1, SqliteConcatStrings),))
                except sqlite3.OperationalError:
                    ex = Exception(f'The database on the path "{filename}" is corrupted')
            except Exception as e:
                ex = e
                connection = None
            else:
                ex = None
            self.config["tabs"].append({"name": self.lineEdit_title.text(),
                                        "tab_number": number,
                                        "db_paths": {
                                            "basic": {"path": self.lineEdit_new_bd_path.text(),
                                                      "is_relative": self.checkBox_is_relative.isChecked()},
                                            "additional": []
                                        },
                                        "secret_key": self.lineEdit_key.text()})
        with open((DIRNAME / "config").resolve(), "wb") as file:
            file.write(Fernet(SECRET_KEY.encode()).encrypt(json.dumps(self.config).encode()))
        self.reload_app_for_new_bd()
        self.close()

    def point_out_db_path(self):
        dialog = QtWidgets.QFileDialog()
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Warning)
        error_dialog.setWindowTitle("Ошибка.")
        error_dialog.setWindowIcon(QtGui.QIcon(DB_ICON_PATH))
        if self.sender().objectName() == "pushButton_select_new_bd":
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Выберите расположение файла базы данных.",
                                                             filter="Базы данных (*.db *.sqlite3 *.sqlite)")
            if filename:
                if not (filename.endswith(".sqlite") or filename.endswith(".sqlite3") or filename.endswith(".db")):
                    error_dialog.setText("Ошибка расширения файла базы данных.")
                    error_dialog.setInformativeText("Укажите файл с корректным расширением.")
                    error_dialog.exec_()
                    return
                if self.checkBox_is_relative.isChecked():
                    filename = os.path.relpath(Path(filename).resolve(), start=DIRNAME)
                else:
                    filename = Path(filename).resolve()
                self.lineEdit_new_bd_path.setText(str(filename))
        elif self.sender().objectName() == "pushButton_select_existing_bd":
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            dialog.setNameFilter("Базы данных (*.db *.sqlite3 *.sqlite)")
            if dialog.exec_():
                filename = Path(dialog.selectedFiles()[0]).resolve()
                if self.checkBox_is_relative.isChecked():
                    filename = os.path.relpath(filename, start=DIRNAME)
                try:
                    self.existing_bd_con = sqlite3.connect(filename)
                except Exception:
                    self.existing_bd_con = None
                    error_dialog.setText("Ошибка подключения к базе данных.")
                    error_dialog.setInformativeText("Укажите корректный файл базы данных.")
                    error_dialog.exec_()
                    return
                self.lineEdit_existing_bd_path.setText(str(filename))

    def on_click_checkbox(self):
        if self.checkBox_is_relative.isChecked():
            if self.lineEdit_new_bd_path.text():
                self.lineEdit_new_bd_path.setText(str(os.path.relpath(self.lineEdit_new_bd_path.text(), start=DIRNAME)))
            if self.lineEdit_existing_bd_path.text():
                self.lineEdit_existing_bd_path.setText(
                    str(os.path.relpath(self.lineEdit_existing_bd_path.text(), start=DIRNAME)))
        else:
            if self.lineEdit_new_bd_path.text():
                self.lineEdit_new_bd_path.setText(str((DIRNAME / self.lineEdit_new_bd_path.text()).resolve()))
            if self.lineEdit_existing_bd_path.text():
                self.lineEdit_existing_bd_path.setText(str((DIRNAME / self.lineEdit_existing_bd_path.text()).resolve()))


# Add db Widget for working with changing existing databases
class ChangeDbWidget(Ui_ChangeDb, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/change_db.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_ChangeDb) to this one
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(DB_ICON_PATH))

        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.is_closed = False

        # Showing widget to user
        self.show()

    def closeEvent(self, event):
        self.is_closed = True

    def set_data(self, config, databases, reload_app_for_new_bd):
        self.config = config
        self.databases = databases
        self.reload_app_for_new_bd = reload_app_for_new_bd

    # Adding databases names in combobox widget
    def create_category_combobox(self):
        self.comboBox_category.clear()
        combobox_list = list(map(lambda x: x["name"], self.databases.values()))
        for db in combobox_list:
            self.comboBox_category.addItem(db)

    def setup_functional_abilities(self):
        self.create_category_combobox()
        self.pushButton_submit.clicked.connect(self.change_db)

    def change_db(self):
        if not self.lineEdit_title.text() and not self.lineEdit_key.text():
            self.label_error.setText("Ошибка. Введите данные для изменения.")
            return
        if self.lineEdit_title.text() in map(lambda x: x["name"], self.config["tabs"]):
            self.label_error.setText("Ошибка. Такая дисциплина уже существует.")
            return
        for tab in self.config["tabs"]:
            if tab["name"] == self.comboBox_category.currentText():
                if self.lineEdit_title.text():
                    tab["name"] = self.lineEdit_title.text()
                if self.lineEdit_key.text():
                    try:
                        Fernet(self.lineEdit_key.text().encode()).encrypt(b"123")
                    except Exception:
                        self.label_error.setText("Ошибка. Ключ шифрования не является действительным.")
                        return
                    tab["secret_key"] = self.lineEdit_key.text()
                self.label_error.setText("Успешно.")
                with open((DIRNAME / "config").resolve(), "wb") as file:
                    file.write(Fernet(SECRET_KEY.encode()).encrypt(json.dumps(self.config).encode()))
                self.reload_app_for_new_bd()
                self.create_category_combobox()
                break


# Delete db Widget for working with deleting existing databases
class DeleteDbWidget(Ui_DeleteDb, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/change_db.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_ChangeDb) to this one
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(DB_ICON_PATH))

        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.is_closed = False

        # Showing widget to user
        self.show()

    def closeEvent(self, event):
        self.is_closed = True

    def set_data(self, config, databases, reload_app_for_new_bd):
        self.config = config
        self.databases = databases
        self.reload_app_for_new_bd = reload_app_for_new_bd

    # Adding databases names in combobox widget
    def create_category_combobox(self):
        self.comboBox_category.clear()
        combobox_list = list(map(lambda x: x["name"], self.databases.values()))
        for db in combobox_list:
            self.comboBox_category.addItem(db)

    def setup_functional_abilities(self):
        self.pushButton_submit.clicked.connect(self.delete_db)
        self.create_category_combobox()

    def delete_db(self):
        for tab in self.config["tabs"]:
            if tab["name"] == self.comboBox_category.currentText():
                self.config["tabs"].pop(self.config["tabs"].index(tab))
        with open((DIRNAME / "config").resolve(), "wb") as file:
            file.write(Fernet(SECRET_KEY.encode()).encrypt(json.dumps(self.config).encode()))
        self.label_error.setText("Успешно.")
        self.reload_app_for_new_bd()


class AdminPanelWidget(Ui_AdminPanel, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # uic.loadUi("ui_files/admin_panel.ui", self)
        # The command above is used to load the application interface directly from the UI interface file
        # Avoids compiling the UI file to py using pyuic5 script
        # It is used exclusively in development to preview the interface design
        # The production uses a file compiled using the pyuic5 script,
        # which is imported and connected as an additional class (Ui_AdminPanel) to this one
        self.setupUi(self)

        self.setup_special_ui()
        self.setWindowIcon(QtGui.QIcon(ADMIN_PANEL_ICON_PATH))

        # Setting initial values of main variables
        self.add_record = None
        self.db_widget = None
        self.previous_search = {"type": "show_btn", "text": ""}

        # Showing widget to user
        self.show()

    def closeEvent(self, event):
        if self.add_record is not None:
            self.add_record.close()
        if self.db_widget is not None:
            self.db_widget.close()

    def setup_table_model(self, headers: list, section_resize_mods: dict, data: list):
        self.tableViewModel = table_models.UniversalTableModel()
        if not data:
            self.tableViewModel.set_data([[''] * len(headers)])
        else:
            self.tableViewModel.set_data(data)
        self.tableViewModel.set_horizontal_headers(headers)
        self.tableView.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.tableView.setModel(self.tableViewModel)
        self.tableView.horizontalHeader().sectionResized.connect(self.tableView.resizeRowsToContents)
        self.tableView.setWordWrap(True)
        for i in section_resize_mods:
            self.tableView.horizontalHeader().setSectionResizeMode(i, section_resize_mods[i])

    # Setting specific interface settings that QtDesigner does not allow you to implement
    def setup_special_ui(self):
        self.radioButton_short_search.setChecked(True)
        self.pushButton_search.clicked.connect(partial(self.change_model, "search_btn"))
        self.pushButton_show.clicked.connect(partial(self.change_model, "show_btn"))
        self.pushButton_add.clicked.connect(self.exec_add_record)
        self.pushButton_delete.clicked.connect(self.exec_delete_record)
        self.pushButton_change.clicked.connect(self.exec_change_record)
        # self.label.setMargin(10)

    def set_data(self, databases: dict, config: None, reload_dbs: None, selected_db_name: str,
                 raise_encryption_exception, reload_main_window, reload_paths_editor, connect_to_dbs):
        self.reload_dbs = reload_dbs
        self.databases = databases
        self.config = config
        self.selected_db_name = selected_db_name
        self.raise_encryption_exception = raise_encryption_exception
        self.reload_main_window = reload_main_window
        self.reload_paths_editor = reload_paths_editor
        self.connect_to_dbs = connect_to_dbs

    def get_search_radio_btn(self):
        for btn in self.buttonGroup_search.buttons():
            if btn.isChecked():
                return btn

    def comboBox_changed(self):
        self.selected_db_name = self.comboBox_category.currentText()

        for tab in self.config["tabs"]:
            if tab["name"] == self.selected_db_name:
                self.selected_db_key = tab["secret_key"]

        for i in self.databases:
            if self.databases[i]["name"] == self.selected_db_name:
                self.db = self.databases[i]["connections"]["basic"]

        self.change_model("show_btn")

    def change_model(self, temp_value: str = None):
        btn = self.get_search_radio_btn().text()
        if temp_value is None:
            value = self.previous_search["type"]
            text = self.previous_search["text"]
        else:
            value = temp_value
            text = self.lineEdit_search.text()
        data = ["", "", "", ""]

        if value == "show_btn":
            if btn.startswith("Термин"):
                query = f'SELECT DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), CUSTOMCONCAT(DECRYPT(D.document)), DECRYPT(T.term) ' \
                        f'FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                        f'GROUP BY T.term ' \
                        f'ORDER BY S.short ASC'
            elif btn.startswith("Синоним"):
                query = f'SELECT DECRYPT(A.abstraction), DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(D.document)), DECRYPT(T.term) ' \
                        f'FROM abstractions A JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(A.id) = DECRYPT(T_T_A.abstraction_id) JOIN terms T ON ' \
                        f'DECRYPT(T_T_A.term_id) = DECRYPT(T.id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id)' \
                        f'GROUP BY T.term, A.abstraction ' \
                        f'ORDER BY A.abstraction ASC'
            elif btn.startswith("Определен"):
                query = f'SELECT DECRYPT(T.term), DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), CUSTOMCONCAT(DECRYPT(D.document)) ' \
                        f'FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                        f'GROUP BY T.term ' \
                        f'ORDER BY S.short ASC'
            elif btn.startswith("Документ"):
                query = f'SELECT DECRYPT(D.document), DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), DECRYPT(T.term) ' \
                        f'FROM documents D JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(D.id) = DECRYPT(T_T_D.document_id) JOIN terms T ON ' \
                        f'DECRYPT(T_T_D.term_id) = DECRYPT(T.id) JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id)' \
                        f'GROUP BY T.term, D.document ' \
                        f'ORDER BY D.document ASC'
        elif value == "search_btn":
            if not text:
                self.label_error_data.setText("Ошибка. Введите текст для поиска.")
                return
            if btn.startswith("Термин"):
                query = f'SELECT DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), CUSTOMCONCAT(DECRYPT(D.document)), DECRYPT(T.term) ' \
                        f'FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                        f'WHERE (LOWER(DECRYPT(S.short)) LIKE "%{text.lower()}%" OR "{text.lower()}" LIKE ("%" || LOWER(DECRYPT(S.short)) || "%")) ' \
                        f'GROUP BY T.term ' \
                        f'ORDER BY S.short ASC'
            elif btn.startswith("Синоним"):
                query = f'SELECT DECRYPT(A.abstraction), DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(D.document)), DECRYPT(T.term) ' \
                        f'FROM abstractions A JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(A.id) = DECRYPT(T_T_A.abstraction_id) JOIN terms T ON ' \
                        f'DECRYPT(T_T_A.term_id) = DECRYPT(T.id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id)' \
                        f'WHERE (LOWER(DECRYPT(A.abstraction)) LIKE "%{text.lower()}%" OR "{text.lower()}" LIKE ("%" || LOWER(DECRYPT(A.abstraction)) || "%")) ' \
                        f'GROUP BY T.term, A.abstraction ' \
                        f'ORDER BY A.abstraction ASC'
            elif btn.startswith("Определен"):
                query = f'SELECT DECRYPT(T.term), DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), CUSTOMCONCAT(DECRYPT(D.document)) ' \
                        f'FROM terms T JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_D.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN documents D ON ' \
                        f'DECRYPT(T_T_D.document_id) = DECRYPT(D.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id) ' \
                        f'WHERE (LOWER(DECRYPT(T.term)) LIKE "%{text.lower()}%" OR "{text.lower()}" LIKE ("%" || LOWER(DECRYPT(T.term)) || "%")) ' \
                        f'GROUP BY T.term ' \
                        f'ORDER BY S.short ASC'
            elif btn.startswith("Документ"):
                query = f'SELECT DECRYPT(D.document), DECRYPT(S.short), CUSTOMCONCAT(DECRYPT(A.abstraction)), DECRYPT(T.term) ' \
                        f'FROM documents D JOIN terms_to_docs T_T_D ON ' \
                        f'DECRYPT(D.id) = DECRYPT(T_T_D.document_id) JOIN terms T ON ' \
                        f'DECRYPT(T_T_D.term_id) = DECRYPT(T.id) JOIN terms_to_abstractions T_T_A ON ' \
                        f'DECRYPT(T.id) = DECRYPT(T_T_A.term_id) JOIN abstractions A ON ' \
                        f'DECRYPT(T_T_A.abstraction_id) = DECRYPT(A.id) JOIN shorts S ON ' \
                        f'DECRYPT(T.short_id) = DECRYPT(S.id)' \
                        f'WHERE (LOWER(DECRYPT(D.document)) LIKE "%{text.lower()}%" OR "{text.lower()}" LIKE ("%" || LOWER(DECRYPT(D.document)) || "%")) ' \
                        f'GROUP BY T.term, D.document ' \
                        f'ORDER BY D.document ASC'
        cursor = execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),),
                               (('CUSTOMCONCAT', 1, SqliteConcatStrings),))
        data = [list(item) for item in cursor.fetchall()]

        if value == "search_btn" or value == "show_btn":
            if btn.startswith("Термин"):
                self.setup_table_model(["Термин", "Синонимы", "Документы", "Определение"],
                                       {0: QtWidgets.QHeaderView.ResizeToContents,
                                        1: QtWidgets.QHeaderView.ResizeToContents,
                                        2: QtWidgets.QHeaderView.ResizeToContents,
                                        3: QtWidgets.QHeaderView.Stretch}, data)
            elif btn.startswith("Синоним"):
                self.setup_table_model(["Синоним", "Термин", "Документы", "Определение"],
                                       {0: QtWidgets.QHeaderView.ResizeToContents,
                                        1: QtWidgets.QHeaderView.ResizeToContents,
                                        2: QtWidgets.QHeaderView.ResizeToContents,
                                        3: QtWidgets.QHeaderView.Stretch}, data)
            elif btn.startswith("Определен"):
                self.setup_table_model(["Определение", "Термин", "Синонимы", "Документы"],
                                       {0: QtWidgets.QHeaderView.Stretch,
                                        1: QtWidgets.QHeaderView.ResizeToContents,
                                        2: QtWidgets.QHeaderView.ResizeToContents,
                                        3: QtWidgets.QHeaderView.ResizeToContents}, data)
            elif btn.startswith("Документ"):
                self.setup_table_model(["Документ", "Термин", "Синонимы", "Определение"],
                                       {0: QtWidgets.QHeaderView.ResizeToContents,
                                        1: QtWidgets.QHeaderView.ResizeToContents,
                                        2: QtWidgets.QHeaderView.ResizeToContents,
                                        3: QtWidgets.QHeaderView.Stretch}, data)

        self.previous_search = {"type": value, "text": text}

    # Opening a window for adding new record
    def exec_add_record(self):
        if self.add_record is not None:
            self.add_record.close()
        self.add_record = RecordWidget()
        self.add_record.set_data(self.databases, self.config, self.reload_dbs, self.comboBox_category.currentText(),
                                 self.raise_encryption_exception, self.change_model)
        self.add_record.create_category_combobox()

    def exec_delete_record(self):
        if len(self.tableView.selectionModel().selectedRows()) > 1:
            self.label_error_data.setText("Ошибка. Выберите не более одной строки для удаления.")
            return
        if len(self.tableView.selectionModel().selectedRows()) == 0:
            self.label_error_data.setText("Ошибка. Выберите строку для удаления.")
            return
        index = self.tableView.selectionModel().selectedRows()[0]
        data = self.tableViewModel.get_data()[index.row()]
        btn = self.get_search_radio_btn().text()
        if btn.startswith("Термин"):
            term = data[3]
        elif btn.startswith("Синоним"):
            term = data[3]
        elif btn.startswith("Определен"):
            term = data[0]
        elif btn.startswith("Документ"):
            term = data[3]
        if self.add_record is not None:
            if not self.add_record.is_closed:
                if self.add_record.is_changing:
                    if self.add_record.record_data_term == term:
                        dialog = QtWidgets.QMessageBox()
                        dialog.setIcon(QtWidgets.QMessageBox.Warning)
                        dialog.setWindowTitle("Ошибка.")
                        dialog.setWindowIcon(QtGui.QIcon(ICON_PATH))
                        ok_button = dialog.addButton("ОК", QtWidgets.QMessageBox.AcceptRole)
                        text = {"text": "В данный момент вы уже редактируете этот термин."}
                        dialog.setText(text["text"])
                        dialog.exec_()
                        return
        query = f'DELETE FROM terms_to_docs WHERE DECRYPT(term_id) = ' \
                f'(SELECT DECRYPT(id) FROM terms WHERE DECRYPT(term) = "{term}")'
        execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        query = f'DELETE FROM terms_to_abstractions WHERE DECRYPT(term_id) = ' \
                f'(SELECT DECRYPT(id) FROM terms WHERE DECRYPT(term) = "{term}")'
        execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        query = f'DELETE FROM terms WHERE DECRYPT(term) = "{term}"'
        execute_query(self.db, query, (('DECRYPT', 1, sqlite_decrypt_constructor(self.selected_db_key)),))
        self.db.commit()
        self.label_error_data.setText("Успешно.")
        self.change_model()

    def exec_change_record(self):
        if len(self.tableView.selectionModel().selectedRows()) > 1:
            self.label_error_data.setText("Ошибка. Выберите не более одной строки для изменения.")
            return
        if len(self.tableView.selectionModel().selectedRows()) == 0:
            self.label_error_data.setText("Ошибка. Выберите строку для изменения.")
            return
        index = self.tableView.selectionModel().selectedRows()[0]
        data = self.tableViewModel.get_data()[index.row()]
        btn = self.get_search_radio_btn().text()
        if btn.startswith("Термин"):
            term = data[3]
        elif btn.startswith("Синоним"):
            term = data[3]
        elif btn.startswith("Определен"):
            term = data[0]
        elif btn.startswith("Документ"):
            term = data[3]
        if self.add_record is not None:
            self.add_record.close()
        self.add_record = RecordWidget()
        self.add_record.set_data(self.databases, self.config, self.reload_dbs, self.comboBox_category.currentText(),
                                 self.raise_encryption_exception, self.change_model, term, True)
        self.add_record.create_category_combobox()
        self.change_model()

    def reload_widgets(self):
        if self.add_record is not None:
            if self.add_record.is_changing:
                combobox_list = list(map(lambda x: x["name"],
                                         filter(lambda x: x["exceptions"]["basic"] is None, self.databases.values())))
                if self.add_record.selected_db_name not in combobox_list:
                    self.add_record = None
            else:
                self.add_record.create_category_combobox()

    def reload_app_for_new_bd(self):
        self.reload_main_window()
        self.connect_to_dbs()
        self.create_elements()
        self.reload_widgets()
        self.reload_paths_editor()

    def exec_add_db(self):
        if self.db_widget is not None:
            self.db_widget.close()
        self.db_widget = AddDbWidget()
        self.db_widget.set_data(self.config, self.databases, self.reload_app_for_new_bd)
        self.db_widget.setup_functional_abilities()

    def exec_change_db(self):
        if self.db_widget is not None:
            self.db_widget.close()
        self.db_widget = ChangeDbWidget()
        self.db_widget.set_data(self.config, self.databases, self.reload_app_for_new_bd)
        self.db_widget.setup_functional_abilities()

    def exec_delete_db(self):
        if self.db_widget is not None:
            self.db_widget.close()
        self.db_widget = DeleteDbWidget()
        self.db_widget.set_data(self.config, self.databases, self.reload_app_for_new_bd)
        self.db_widget.setup_functional_abilities()

    def on_target_change(self):
        self.change_model()

    def create_elements(self):
        # Creating menu on menubar
        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.menu = QtWidgets.QMenu("Меню", self)
        self.open_add_db_action = QtWidgets.QAction(QtGui.QIcon(DB_ICON_PATH),
                                                    "&Добавить дисциплину", self)
        self.open_change_db_action = QtWidgets.QAction(QtGui.QIcon(DB_ICON_PATH),
                                                       "&Изменить дисциплину", self)
        self.open_delete_db_action = QtWidgets.QAction(QtGui.QIcon(DB_ICON_PATH),
                                                       "&Удалить дисциплину", self)
        self.open_add_db_action.triggered.connect(self.exec_add_db)
        self.open_change_db_action.triggered.connect(self.exec_change_db)
        self.open_delete_db_action.triggered.connect(self.exec_delete_db)
        self.menu.addAction(self.open_add_db_action)
        self.menu.addAction(self.open_change_db_action)
        self.menu.addAction(self.open_delete_db_action)
        self.menubar.addMenu(self.menu)

        self.comboBox_category.clear()

        for db in self.databases:
            if self.databases[db]["name"] == self.selected_db_name:
                if self.databases[db]["exceptions"]["basic"] is None:
                    self.comboBox_category.addItem(self.databases[db]["name"])
                    break

        for db in self.databases:
            if self.databases[db]["name"] == self.selected_db_name:
                continue
            if self.databases[db]["exceptions"]["basic"] is None:
                self.comboBox_category.addItem(self.databases[db]["name"])

        self.buttonGroup_search.buttonToggled.connect(self.on_target_change)
        self.comboBox_category.currentTextChanged.connect(self.comboBox_changed)
        self.comboBox_changed()
