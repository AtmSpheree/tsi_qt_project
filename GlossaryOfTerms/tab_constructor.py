# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui


# A constructor class for creating different sections of QTabWidget
class SectionTabQWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_num = 1

    def set_order_num(self, num: int = 1):
        self.order_num = num

    # Installation of the initial interface
    def setup_ui(self):
        exec(f'self.setObjectName("tab{self.order_num}")')

        exec(f'self.verticalLayout_tab{self.order_num} = QtWidgets.QVBoxLayout(self)')
        exec(f'self.verticalLayout_tab{self.order_num}.setObjectName("verticalLayout_tab{self.order_num}")')

        exec(f'self.horizontalLayout_tab{self.order_num} = QtWidgets.QHBoxLayout()')
        exec(f'self.horizontalLayout_tab{self.order_num}.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)')
        exec(f'self.horizontalLayout_tab{self.order_num}.setObjectName("horizontalLayout_tab{self.order_num}")')

        exec(f'self.frame_tab{self.order_num} = QtWidgets.QFrame(self)')
        exec(f'self.frame_tab{self.order_num}.setFrameShape(QtWidgets.QFrame.Box)')
        exec(f'self.frame_tab{self.order_num}.setFrameShadow(QtWidgets.QFrame.Raised)')
        exec(f'self.frame_tab{self.order_num}.setLineWidth(4)')
        exec(f'self.frame_tab{self.order_num}.setObjectName("frame_tab{self.order_num}")')
        exec(f'self.verticalLayout_2_tab{self.order_num} = QtWidgets.QVBoxLayout(self.frame_tab{self.order_num})')
        exec(f'self.verticalLayout_2_tab{self.order_num}.setObjectName("verticalLayout_2_tab{self.order_num}")')

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        exec(f'self.verticalLayout_2_tab{self.order_num}.addItem(spacerItem)')

        exec(f'self.label_2_tab{self.order_num} = QtWidgets.QLabel(self.frame_tab{self.order_num})')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(eval(f'self.label_2_tab{self.order_num}.sizePolicy().hasHeightForWidth()'))
        exec(f'self.label_2_tab{self.order_num}.setSizePolicy(sizePolicy)')
        exec(f'self.label_2_tab{self.order_num}.setMinimumSize(QtCore.QSize(250, 0))')
        exec(f'self.label_2_tab{self.order_num}.setMaximumSize(QtCore.QSize(250, 16777215))')
        font = QtGui.QFont()
        font.setPointSize(11)
        exec(f'self.label_2_tab{self.order_num}.setFont(font)')
        exec(f'self.label_2_tab{self.order_num}.setFrameShape(QtWidgets.QFrame.NoFrame)')
        exec(f'self.label_2_tab{self.order_num}.setAlignment(QtCore.Qt.AlignCenter)')
        exec(f'self.label_2_tab{self.order_num}.setObjectName("label_2_tab{self.order_num}")')
        exec(f'self.verticalLayout_2_tab{self.order_num}.addWidget(self.label_2_tab{self.order_num})')

        exec(f'self.lineEditSearch_tab{self.order_num} = QtWidgets.QLineEdit(self.frame_tab{self.order_num})')
        exec(f'self.lineEditSearch_tab{self.order_num}.setMaximumSize(QtCore.QSize(250, 16777215))')
        font = QtGui.QFont()
        font.setPointSize(10)
        exec(f'self.lineEditSearch_tab{self.order_num}.setFont(font)')
        exec(f'self.lineEditSearch_tab{self.order_num}.setObjectName("lineEditSearch_tab{self.order_num}")')
        exec(f'self.verticalLayout_2_tab{self.order_num}.addWidget(self.lineEditSearch_tab{self.order_num})')

        exec(f'self.pushButtonSearch_tab{self.order_num} = QtWidgets.QPushButton(self.frame_tab{self.order_num})')
        exec(f'self.pushButtonSearch_tab{self.order_num}.setMaximumSize(QtCore.QSize(250, 16777215))')
        font = QtGui.QFont()
        font.setPointSize(10)
        exec(f'self.pushButtonSearch_tab{self.order_num}.setFont(font)')
        exec(f'self.pushButtonSearch_tab{self.order_num}.setObjectName("pushButtonSearch_tab{self.order_num}")')
        exec(f'self.verticalLayout_2_tab{self.order_num}.addWidget(self.pushButtonSearch_tab{self.order_num})')

        exec(f'self.labelError_tab{self.order_num} = QtWidgets.QLabel(self.frame_tab{self.order_num})')
        exec(f'self.labelError_tab{self.order_num}.setMaximumSize(QtCore.QSize(250, 16777215))')
        exec(f'self.labelError_tab{self.order_num}.setText("")')
        exec(f'self.labelError_tab{self.order_num}.setObjectName("labelError_tab{self.order_num}")')
        exec(f'self.verticalLayout_2_tab{self.order_num}.addWidget(self.labelError_tab{self.order_num})')

        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        exec(f'self.verticalLayout_2_tab{self.order_num}.addItem(spacerItem1)')

        exec(f'self.horizontalLayout_tab{self.order_num}.addWidget(self.frame_tab{self.order_num})')

        exec(f'self.frame_2_tab{self.order_num} = QtWidgets.QFrame(self)')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(eval(f'self.frame_2_tab{self.order_num}.sizePolicy().hasHeightForWidth()'))
        exec(f'self.frame_2_tab{self.order_num}.setSizePolicy(sizePolicy)')
        exec(f'self.frame_2_tab{self.order_num}.setFrameShape(QtWidgets.QFrame.Box)')
        exec(f'self.frame_2_tab{self.order_num}.setFrameShadow(QtWidgets.QFrame.Raised)')
        exec(f'self.frame_2_tab{self.order_num}.setLineWidth(4)')
        exec(f'self.frame_2_tab{self.order_num}.setObjectName("frame_2_tab{self.order_num}")')

        exec(f'self.horizontalLayout_3_tab{self.order_num} = QtWidgets.QHBoxLayout(self.frame_2_tab{self.order_num})')
        exec(f'self.horizontalLayout_3_tab{self.order_num}.setContentsMargins(0, 0, 0, 0)')
        exec(f'self.horizontalLayout_3_tab{self.order_num}.setObjectName("horizontalLayout_3_tab{self.order_num}")')

        exec(f'self.textBrowserInfo_tab{self.order_num} = QtWidgets.QTextBrowser(self.frame_2_tab{self.order_num})')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(eval(f'self.textBrowserInfo_tab{self.order_num}.sizePolicy().hasHeightForWidth()'))
        exec(f'self.textBrowserInfo_tab{self.order_num}.setSizePolicy(sizePolicy)')
        exec(f'self.textBrowserInfo_tab{self.order_num}.setMinimumSize(QtCore.QSize(200, 163))')
        exec(f'self.textBrowserInfo_tab{self.order_num}.setMaximumSize(QtCore.QSize(16777215, 163))')
        exec(f'self.textBrowserInfo_tab{self.order_num}.setSizeIncrement(QtCore.QSize(0, 0))')
        font = QtGui.QFont()
        font.setPointSize(10)
        exec(f'self.textBrowserInfo_tab{self.order_num}.setFont(font)')
        exec(f'self.textBrowserInfo_tab{self.order_num}.setObjectName("textBrowserInfo_tab{self.order_num}")')
        exec(f'self.horizontalLayout_3_tab{self.order_num}.addWidget(self.textBrowserInfo_tab{self.order_num})')

        exec(f'self.horizontalLayout_tab{self.order_num}.addWidget(self.frame_2_tab{self.order_num})')
        exec(f'self.verticalLayout_tab{self.order_num}.addLayout(self.horizontalLayout_tab{self.order_num})')

        exec(f'self.tableViewHistory_tab{self.order_num} = QtWidgets.QTableView(self)')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(eval(f'self.tableViewHistory_tab{self.order_num}.sizePolicy().hasHeightForWidth()'))
        exec(f'self.tableViewHistory_tab{self.order_num}.setSizePolicy(sizePolicy)')
        exec(f'self.tableViewHistory_tab{self.order_num}.setObjectName("tableViewHistory_tab{self.order_num}")')
        exec(f'self.verticalLayout_tab{self.order_num}.addWidget(self.tableViewHistory_tab{self.order_num})')

        QtCore.QMetaObject.connectSlotsByName(self)

        exec(f'self.label_2_tab{self.order_num}.setText("Просмотр определения")')
        exec(f'self.pushButtonSearch_tab{self.order_num}.setText("Поиск")')