# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\GlossaryOfTerms\ui_files\delete_db.ui'
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
        Form.resize(493, 96)
        Form.setMinimumSize(QtCore.QSize(493, 96))
        Form.setMaximumSize(QtCore.QSize(493, 96))
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.comboBox_category = QtWidgets.QComboBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_category.sizePolicy().hasHeightForWidth())
        self.comboBox_category.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox_category.setFont(font)
        self.comboBox_category.setObjectName("comboBox_category")
        self.horizontalLayout.addWidget(self.comboBox_category)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
        self.verticalLayout_4.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Удаление дисциплины"))
        self.label_3.setText(_translate("Form", "Дисциплина"))
        self.pushButton_submit.setText(_translate("Form", "Удалить дисциплину"))
