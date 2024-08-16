from cryptography.fernet import Fernet
from PyQt5 import QtWidgets, QtGui
import sys
from ui_keygen import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.pushButton.clicked.connect(self.generate_key)

    def generate_key(self):
        self.lineEdit.setText(Fernet.generate_key().decode())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    ex = MainWindow()

    ex.show()

    sys.exit(app.exec_())
