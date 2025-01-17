import sys

from faslr.indexation import (
    IndexTableModel,
    IndexTableView,
    IndexPane
)

from PyQt6.QtWidgets import QApplication

dummy_ays = list(range(2000, 2009))

app = QApplication(sys.argv)


index_pane = IndexPane(years=dummy_ays)

index_pane.show()

app.exec()