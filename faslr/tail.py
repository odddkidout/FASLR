from faslr.base_table import (
    FAbstractTableModel,
    FTableView
)

from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget
)


class TailPane(QWidget):
    def __init__(self):
        super().__init__()


class TailTableModel(FAbstractTableModel):
    def __init__(self):
        super().__init__()


class TailTableView(FTableView):
    def __init__(self):
        super().__init__()
