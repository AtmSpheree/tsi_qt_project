# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\GlossaryOfTerms\ui_files\add_db.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(493, 344)
        Form.setMinimumSize(QtCore.QSize(493, 344))
        Form.setMaximumSize(QtCore.QSize(493, 344))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.lineEdit_title = QtWidgets.QLineEdit(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_title.setFont(font)
        self.lineEdit_title.setObjectName("lineEdit_title")
        self.verticalLayout_2.addWidget(self.lineEdit_title)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.lineEdit_key = QtWidgets.QLineEdit(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_key.setFont(font)
        self.lineEdit_key.setObjectName("lineEdit_key")
        self.verticalLayout_3.addWidget(self.lineEdit_key)
        self.pushButton_generate_key = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_generate_key.setFont(font)
        self.pushButton_generate_key.setObjectName("pushButton_generate_key")
        self.verticalLayout_3.addWidget(self.pushButton_generate_key)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.radioButton_create_new_bd = QtWidgets.QRadioButton(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.radioButton_create_new_bd.setFont(font)
        self.radioButton_create_new_bd.setChecked(True)
        self.radioButton_create_new_bd.setObjectName("radioButton_create_new_bd")
        self.buttonGroup_is_create = QtWidgets.QButtonGroup(Form)
        self.buttonGroup_is_create.setObjectName("buttonGroup_is_create")
        self.buttonGroup_is_create.addButton(self.radioButton_create_new_bd)
        self.verticalLayout_4.addWidget(self.radioButton_create_new_bd)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_new_bd_path = QtWidgets.QLineEdit(Form)
        self.lineEdit_new_bd_path.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_new_bd_path.setFont(font)
        self.lineEdit_new_bd_path.setReadOnly(True)
        self.lineEdit_new_bd_path.setObjectName("lineEdit_new_bd_path")
        self.horizontalLayout_2.addWidget(self.lineEdit_new_bd_path)
        self.pushButton_select_new_bd = QtWidgets.QPushButton(Form)
        self.pushButton_select_new_bd.setEnabled(True)
        self.pushButton_select_new_bd.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_select_new_bd.setFont(font)
        self.pushButton_select_new_bd.setObjectName("pushButton_select_new_bd")
        self.horizontalLayout_2.addWidget(self.pushButton_select_new_bd)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.radioButton_select_existing_bd = QtWidgets.QRadioButton(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.radioButton_select_existing_bd.setFont(font)
        self.radioButton_select_existing_bd.setObjectName("radioButton_select_existing_bd")
        self.buttonGroup_is_create.addButton(self.radioButton_select_existing_bd)
        self.verticalLayout_4.addWidget(self.radioButton_select_existing_bd)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_existing_bd_path = QtWidgets.QLineEdit(Form)
        self.lineEdit_existing_bd_path.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_existing_bd_path.setFont(font)
        self.lineEdit_existing_bd_path.setReadOnly(True)
        self.lineEdit_existing_bd_path.setObjectName("lineEdit_existing_bd_path")
        self.horizontalLayout.addWidget(self.lineEdit_existing_bd_path)
        self.pushButton_select_existing_bd = QtWidgets.QPushButton(Form)
        self.pushButton_select_existing_bd.setEnabled(False)
        self.pushButton_select_existing_bd.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_select_existing_bd.setFont(font)
        self.pushButton_select_existing_bd.setObjectName("pushButton_select_existing_bd")
        self.horizontalLayout.addWidget(self.pushButton_select_existing_bd)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_4)
        self.checkBox_is_relative = QtWidgets.QCheckBox(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.checkBox_is_relative.setFont(font)
        self.checkBox_is_relative.setObjectName("checkBox_is_relative")
        self.verticalLayout.addWidget(self.checkBox_is_relative)
        self.pushButton_submit = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_submit.setFont(font)
        self.pushButton_submit.setObjectName("pushButton_submit")
        self.verticalLayout.addWidget(self.pushButton_submit)
        self.label_error = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_error.setFont(font)
        self.label_error.setText("")
        self.label_error.setObjectName("label_error")
        self.verticalLayout.addWidget(self.label_error)
        self.verticalLayout_5.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Добавление дисциплины"))
        self.label.setText(_translate("Form", "Введите название дисциплины"))
        self.label_2.setText(_translate("Form", "Введите ключ шифрования"))
        self.pushButton_generate_key.setText(_translate("Form", "Сгенерировать"))
        self.radioButton_create_new_bd.setText(_translate("Form", "Создать новую базу данных"))
        self.lineEdit_new_bd_path.setPlaceholderText(_translate("Form", "Укажите путь к базе данных"))
        self.pushButton_select_new_bd.setText(_translate("Form", "..."))
        self.radioButton_select_existing_bd.setText(_translate("Form", "Указать существующую базу данных"))
        self.lineEdit_existing_bd_path.setPlaceholderText(_translate("Form", "Укажите путь к базе данных"))
        self.pushButton_select_existing_bd.setText(_translate("Form", "..."))
        self.checkBox_is_relative.setText(_translate("Form", "Относительный путь."))
        self.pushButton_submit.setText(_translate("Form", "Добавить дисциплину"))
