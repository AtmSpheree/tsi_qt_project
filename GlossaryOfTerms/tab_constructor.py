# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui


# A constructor class for creating different sections of QTabWidget
class SectionTabQWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Installation of the initial interface
    def setup_ui(self, index):
        self.setObjectName(f"tab{index}")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.frame = QtWidgets.QFrame(self)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(4)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)

        self.label_2 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(250, 0))
        self.label_2.setMaximumSize(QtCore.QSize(250, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)

        self.lineEditSearch = QtWidgets.QLineEdit(self.frame)
        self.lineEditSearch.setMaximumSize(QtCore.QSize(250, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEditSearch.setFont(font)
        self.lineEditSearch.setObjectName("lineEditSearch")
        self.verticalLayout_2.addWidget(self.lineEditSearch)

        self.pushButtonSearch = QtWidgets.QPushButton(self.frame)
        self.pushButtonSearch.setMaximumSize(QtCore.QSize(250, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButtonSearch.setFont(font)
        self.pushButtonSearch.setObjectName("pushButtonSearch")
        self.verticalLayout_2.addWidget(self.pushButtonSearch)

        self.labelError = QtWidgets.QLabel(self.frame)
        self.labelError.setMaximumSize(QtCore.QSize(250, 16777215))
        self.labelError.setText("")
        self.labelError.setObjectName("labelError")
        self.verticalLayout_2.addWidget(self.labelError)

        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)

        self.horizontalLayout.addWidget(self.frame)

        self.frame_2 = QtWidgets.QFrame(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setLineWidth(4)
        self.frame_2.setObjectName("frame_2")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.textBrowserInfo = QtWidgets.QTextBrowser(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowserInfo.sizePolicy().hasHeightForWidth())
        self.textBrowserInfo.setSizePolicy(sizePolicy)
        self.textBrowserInfo.setMinimumSize(QtCore.QSize(200, 163))
        self.textBrowserInfo.setMaximumSize(QtCore.QSize(16777215, 163))
        self.textBrowserInfo.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textBrowserInfo.setFont(font)
        self.textBrowserInfo.setObjectName("textBrowserInfo")
        self.horizontalLayout_3.addWidget(self.textBrowserInfo)

        self.horizontalLayout.addWidget(self.frame_2)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableView = QtWidgets.QTableView(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName("tableViewHistory")
        self.verticalLayout.addWidget(self.tableView)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.label_2.setText("Просмотр определения")
        self.pushButtonSearch.setText("Поиск")