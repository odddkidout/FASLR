import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumWidth(400)

        self.setWindowTitle("FASLR - Free Actuarial System for Loss Reserving")

        self.create_menu_bar()

        # self.create_actions()

    def create_menu_bar(self):

        menu_bar = self.menuBar()

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu("&Edit")
        menu_bar.addMenu("&Tools")
        help_menu = menu_bar.addMenu("&Help")

        self.new_action = QAction(self)
        self.connection_action = QAction("&Connection", self)
        self.new_action.setText("&New Project")
        self.import_action = QAction("&Import Project")

        self.settings_action = QAction("&Settings")

        self.about_action = QAction("&About", self)

        file_menu.addAction(self.connection_action)
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.import_action)
        file_menu.addAction(self.settings_action)

        help_menu.addAction(self.about_action)


app = QApplication(sys.argv)

window = MainWindow()

window.show()

app.exec_()
