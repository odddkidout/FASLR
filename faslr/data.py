import numpy as np
import pandas as pd

from faslr.analysis import AnalysisTab

from faslr.base_table import (
    FAbstractTableModel,
    FTableView
)

from chainladder import Triangle

from faslr.constants import (
    DEVELOPMENT_FIELDS,
    LOSS_FIELDS,
    ORIGIN_FIELDS,
    QT_FILEPATH_OPTION
)

from PyQt6.QtCore import (
    QModelIndex,
    Qt
)

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTabWidget,
    QVBoxLayout,
    QWidget
)

from typing import Any


class DataPane(QWidget):
    def __init__(
            self,
            parent=None
    ):
        super().__init__()

        self.wizard = None
        self.parent = parent

        self.layout = QVBoxLayout()
        self.upload_btn = QPushButton("Upload")
        self.setLayout(self.layout)
        self.layout.addWidget(
            self.upload_btn,
            alignment=Qt.AlignmentFlag.AlignRight
        )
        filler = QWidget()
        self.layout.addWidget(filler)
        self.upload_btn.pressed.connect(self.start_wizard)  # noqa

    def start_wizard(self) -> None:
        self.wizard = DataImportWizard()
        self.wizard.show()


class DataImportWizard(QTabWidget):
    def __init__(
            self,
    ):
        super().__init__()

        self.args_tab = ImportArgumentsTab()
        self.preview_tab = TrianglePreviewTab(
            sibling=self.args_tab
        )

        self.addTab(
            self.args_tab,
            "Arguments"
        )

        self.addTab(
            self.preview_tab,
            "Preview"
        )

        self.currentChanged.connect( # noqa
            self.preview_tab.generate_triangle
        )


class ImportArgumentsTab(QWidget):
    def __init__(
            self,
            parent=None
    ):
        super().__init__()

        self.setWindowTitle("Import Wizard")
        self.parent = parent

        # Holds the uploaded dataframe
        self.data = None

        self.triangle = None

        self.arg_tab = QTabWidget()
        self.layout = QVBoxLayout()
        self.upload_form = QFormLayout()
        self.file_path = QLineEdit()

        # File upload section
        self.upload_btn = QPushButton("Upload File")
        self.upload_container = QWidget()
        self.upload_container.setLayout(self.upload_form)

        self.file_path_layout = QHBoxLayout()
        self.file_path_container = QWidget()
        self.file_path_container.setLayout(self.file_path_layout)
        self.file_path_layout.addWidget(self.upload_btn)
        self.file_path_layout.addWidget(self.file_path)

        self.upload_form.addRow(
            self.file_path_container
        )

        self.layout.addWidget(self.upload_container)
        self.setLayout(self.layout)

        self.upload_btn.pressed.connect(self.load_file)  # noqa

        # Column mapping section

        self.dropdowns = {}
        self.mapping_groupbox = QGroupBox("Header Mapping")
        self.mapping_layout = QFormLayout()
        self.mapping_groupbox.setLayout(self.mapping_layout)
        self.origin_selection = QWidget()
        self.origin_dropdown = QComboBox()
        self.development_dropdown = QComboBox()
        self.values_dropdown = QComboBox()

        self.origin_dropdown.setFixedWidth(120)
        self.development_dropdown.setFixedWidth(120)
        self.values_dropdown.setFixedWidth(120)

        self.values_container = QWidget()
        self.values_layout = QHBoxLayout()

        self.values_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.values_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.values_container.setLayout(self.values_layout)
        self.values_layout.addWidget(self.values_dropdown)
        self.values_button = QPushButton("+")
        self.remove_values_btn = QPushButton("-")
        self.values_button.setFixedWidth(30)
        self.remove_values_btn.setFixedWidth(30)
        self.values_layout.addWidget(self.values_button)
        self.values_layout.addWidget(self.remove_values_btn)

        self.mapping_layout.addRow(
            "Origin: ",
            self.origin_dropdown
        )

        self.mapping_layout.addRow(
            "Development: ",
            self.development_dropdown
        )

        self.mapping_layout.addRow(
            "Values: ",
            self.values_container
        )

        self.values_button.pressed.connect( # noqa
            lambda form=self.mapping_layout: self.add_values_row(form)
        )

        self.remove_values_btn.pressed.connect( # noqa
            lambda form=self.mapping_layout: self.delete_values_row(form)
        )

        self.layout.addWidget(self.mapping_groupbox)

        # Data sample section
        self.sample_groupbox = QGroupBox("File Data")
        self.sample_layout = QVBoxLayout()
        self.sample_groupbox.setLayout(self.sample_layout)
        self.upload_sample_model = UploadSampleModel()
        self.upload_sample_view = UploadSampleView()
        self.upload_sample_view.setModel(self.upload_sample_model)

        self.sample_layout.addWidget(self.upload_sample_view)

        self.measure_groupbox = QGroupBox("Measure")
        # self.measure_layout = QGridLayout()
        self.measure_layout = QHBoxLayout()
        self.measure_groupbox.setLayout(self.measure_layout)
        self.incremental_btn = QRadioButton("Incremental")
        self.cumulative_btn = QRadioButton("Cumulative")

        self.measure_layout.addWidget(self.cumulative_btn, stretch=0)
        self.measure_layout.addWidget(self.incremental_btn, stretch=0)
        self.cumulative_btn.setChecked(True)
        spacer = QWidget()
        self.measure_layout.addWidget(spacer, stretch=2)
        self.layout.addWidget(self.measure_groupbox)

        self.layout.addWidget(self.sample_groupbox)

        self.dropdowns['origin'] = self.origin_dropdown
        self.dropdowns['development'] = self.development_dropdown
        self.dropdowns['values_1'] = self.values_dropdown

        self.setStyleSheet(
            """
            ImportArgumentsTab {{
              background: rgb(0, 0, 0);
            }}
            """
        )

    def load_file(self) -> None:

        filename = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open File',
            filter='CSV (*.csv)',
            options=QT_FILEPATH_OPTION
        )[0]

        self.file_path.setText(filename)

        self.upload_sample_model.read_header(
            file_path=filename
        )

        self.data = pd.read_csv(filename)
        columns = self.data.columns

        width = None
        for i in self.dropdowns.keys():
            hint_widths = []
            self.dropdowns[i].addItems(columns)
            hint_widths.append(self.dropdowns[i].sizeHint().width())
            width = max(hint_widths) + 55

        for i in self.dropdowns.keys():
            self.dropdowns[i].setFixedWidth(width)

        self.smart_match()

    def add_values_row(
            self,
            form: QFormLayout
    ) -> None:

        # of value keys is total number of keys - 3
        n_keys = len(self.dropdowns.keys())
        last_value_key = n_keys - 2

        new_value_key = last_value_key + 1

        new_dropdown = QComboBox()
        new_dropdown.setFixedWidth(120)

        # add new entry to dropdowns dictionary
        self.dropdowns['values_' + str(new_value_key)] = new_dropdown

        print(self.dropdowns.keys())

        form.addRow(
            "",
            new_dropdown
        )

        # add fields if there are any
        if self.data is None:
            pass
        else:
            new_dropdown.addItems(self.data.columns)
            new_dropdown.setFixedWidth(new_dropdown.sizeHint().width() - 1)

    def delete_values_row(
            self,
            form: QFormLayout
    ) -> None:

        n_row = form.rowCount()

        if n_row == 3:
            return
        else:
            form.removeRow(n_row - 1)

        # remove last entry from dropdown dict
        values_key = n_row - 3
        del self.dropdowns['values_' + str(values_key)]

    def smart_match(self):

        columns = self.data.columns

        for column in columns:
            if column.upper() in ORIGIN_FIELDS:
                self.dropdowns['origin'].setCurrentText(column)
            elif column.upper() in DEVELOPMENT_FIELDS:
                self.dropdowns['development'].setCurrentText(column)
            elif column.upper() in LOSS_FIELDS:
                self.dropdowns['values_1'].setCurrentText(column)


class UploadSampleModel(FAbstractTableModel):
    def __init__(self):
        super().__init__()

        self._data = pd.DataFrame(
            data={'A': [np.nan, np.nan, np.nan],
                  'B': [np.nan, np.nan, np.nan],
                  'C': [np.nan, np.nan, np.nan],
                  'D': [np.nan, np.nan, np.nan]
                  })

    def data(
            self,
            index: QModelIndex,
            role: int = None
    ) -> Any:

        if role == Qt.ItemDataRole.DisplayRole:

            value = self._data.iloc[index.row(), index.column()]

            value = str(value)

            if value == "nan":
                value = ""

            return value

    def headerData(
            self,
            p_int: int,
            qt_orientation: Qt.Orientation,
            role: int = None
    ) -> Any:

        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if qt_orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[p_int])

            # if qt_orientation == Qt.Orientation.Vertical:
            #     return str(self._data.index[p_int])

    def read_header(
            self,
            file_path: str
    ):
        df = pd.read_csv(file_path)

        self._data = df.head()

        index = QModelIndex()

        self.setData(
            index=index,
            value=None,
            role=Qt.ItemDataRole.DisplayRole,
            refresh=True
        )

    def setData(
            self,
            index: QModelIndex,
            value: Any,
            role: int = None,
            refresh: bool = False
    ):

        self.layoutChanged.emit() # noqa


class UploadSampleView(FTableView):
    def __init__(self):
        super().__init__()

        # self.horizontalHeader().setStretchLastSection(True)
        # self.verticalHeader().setStretchLastSection(True)


class TrianglePreviewTab(QWidget):
    def __init__(
        self,
        parent: DataImportWizard = None,
        sibling: ImportArgumentsTab = None
    ):
        super().__init__()

        self.sibling = sibling
        self.parent = parent
        self.analysis_layout = QVBoxLayout()
        self.analysis_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.setLayout(self.analysis_layout)
        self.analysis_tab = None
        self.triangle = None
        self.dropdowns = None
        self.columns = None
        self.cumulative = None

    def generate_triangle(
            self,
    ):
        self.clear_layout()
        self.dropdowns = self.sibling.dropdowns
        self.columns = self.get_columns()

        if self.sibling.cumulative_btn.isChecked():
            self.cumulative = True
        else:
            self.cumulative = False

        self.triangle = Triangle(
            data=self.sibling.data,
            origin=self.dropdowns['origin'].currentText(),
            development=self.sibling.dropdowns['development'].currentText(),
            columns=self.columns,
            cumulative=self.cumulative
        )
        self.analysis_tab = AnalysisTab(
            triangle=self.triangle
        )

        self.analysis_layout.addWidget(self.analysis_tab)

    def get_columns(self) -> list:

        columns = []
        for key in self.sibling.dropdowns:
            # print(key)
            if 'values' in key:
                columns.append(self.dropdowns[key].currentText())

        return columns

    def clear_layout(self):
        if self.analysis_layout is not None:
            while self.analysis_layout.count():
                item = self.analysis_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout()
