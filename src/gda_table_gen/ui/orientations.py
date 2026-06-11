"""Orientations table panel."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QHeaderView, QMessageBox, QAbstractItemView,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from gda_table_gen.core.generator import Orientation
from gda_table_gen.core import epics


_COLUMNS = ["kappa", "phi", "x", "y", "z", "beamSizeX", "beamSizeY"]
_HEADERS = ["Kappa (°)", "Phi (°)", "X (mm)", "Y (mm)", "Z (mm)",
            "Beam X", "Beam Y"]


class OrientationsPanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        box = QGroupBox("Orientations")
        vl = QVBoxLayout(box)

        # EPICS status
        self._epics_label = QLabel()
        self._update_epics_label()
        vl.addWidget(self._epics_label)

        # Table — sized to its content so the outer scroll area handles scrolling
        self.table = QTableWidget(0, len(_COLUMNS))
        self.table.setHorizontalHeaderLabels(_HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.table.itemChanged.connect(lambda _: self.changed.emit())
        self.table.model().rowsInserted.connect(self._update_table_height)
        self.table.model().rowsRemoved.connect(self._update_table_height)
        vl.addWidget(self.table)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_add_manual   = QPushButton("Add row")
        self.btn_capture      = QPushButton("Capture from EPICS && add")
        self.btn_capture_update = QPushButton("Capture from EPICS && update selected")
        self.btn_remove       = QPushButton("Remove selected")
        self.btn_up           = QPushButton("▲")
        self.btn_down         = QPushButton("▼")

        for btn in (self.btn_add_manual, self.btn_capture,
                    self.btn_capture_update, self.btn_remove,
                    self.btn_up, self.btn_down):
            btn_row.addWidget(btn)
        btn_row.addStretch(1)
        vl.addLayout(btn_row)

        root.addWidget(box)

        # Connections
        self.btn_add_manual.clicked.connect(self._add_manual)
        self.btn_capture.clicked.connect(self._capture_and_add)
        self.btn_capture_update.clicked.connect(self._capture_and_update)
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_up.clicked.connect(self._move_up)
        self.btn_down.clicked.connect(self._move_down)


    # ---- Table height ----

    def _update_table_height(self) -> None:
        header_h = self.table.horizontalHeader().height()
        rows_h = sum(self.table.rowHeight(r) for r in range(self.table.rowCount()))
        self.table.setFixedHeight(header_h + rows_h + 2)

    # ---- EPICS status label ----

    def _update_epics_label(self) -> None:
        if epics.is_available():
            self._epics_label.setText("EPICS: connected (cothread available)")
            self._epics_label.setStyleSheet("color: green;")
        else:
            self._epics_label.setText("EPICS: offline — cothread not available; enter values manually")
            self._epics_label.setStyleSheet("color: #b05000;")

    # ---- Row helpers ----

    def _add_row(self, ori: Orientation) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._set_row(row, ori)
        self.changed.emit()

    def _set_row(self, row: int, ori: Orientation) -> None:
        values = [
            ori.kappa, ori.phi,
            ori.x, ori.y, ori.z,
            ori.beam_size_x, ori.beam_size_y,
        ]
        self.table.blockSignals(True)
        for col, val in enumerate(values):
            text = f"{val:.4f}" if val is not None else ""
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if val is None:
                item.setForeground(QColor("#999999"))
            self.table.setItem(row, col, item)
        self.table.blockSignals(False)

    def _row_to_orientation(self, row: int) -> Orientation:
        def _val(col: int) -> float | None:
            item = self.table.item(row, col)
            if item is None or item.text().strip() == "":
                return None
            try:
                return float(item.text())
            except ValueError:
                return None

        return Orientation(
            kappa       = _val(0) or 0.0,
            phi         = _val(1) or 0.0,
            x           = _val(2),
            y           = _val(3),
            z           = _val(4),
            beam_size_x = _val(5),
            beam_size_y = _val(6),
        )

    # ---- Button actions ----

    def _add_manual(self) -> None:
        self._add_row(Orientation())

    def _capture_and_add(self) -> None:
        if not epics.is_available():
            QMessageBox.warning(self, "EPICS unavailable",
                                "cothread is not installed; cannot read PVs.\n"
                                "Enter values manually.")
            return
        data = epics.capture_orientation()
        ori = Orientation(
            kappa       = data.get("kappa") or 0.0,
            phi         = data.get("phi") or 0.0,
            x           = data.get("x"),
            y           = data.get("y"),
            z           = data.get("z"),
            beam_size_x = data.get("beam_size_x"),
            beam_size_y = data.get("beam_size_y"),
        )
        self._add_row(ori)

    def _capture_and_update(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "No selection", "Select a row to update.")
            return
        if not epics.is_available():
            QMessageBox.warning(self, "EPICS unavailable",
                                "cothread is not installed; cannot read PVs.")
            return
        data = epics.capture_orientation()
        ori = Orientation(
            kappa       = data.get("kappa") or 0.0,
            phi         = data.get("phi") or 0.0,
            x           = data.get("x"),
            y           = data.get("y"),
            z           = data.get("z"),
            beam_size_x = data.get("beam_size_x"),
            beam_size_y = data.get("beam_size_y"),
        )
        for index in rows:
            self._set_row(index.row(), ori)
        self.changed.emit()

    def _remove_selected(self) -> None:
        rows = sorted(
            {i.row() for i in self.table.selectionModel().selectedRows()},
            reverse=True,
        )
        for row in rows:
            self.table.removeRow(row)
        self.changed.emit()

    def _move_up(self) -> None:
        rows = sorted({i.row() for i in self.table.selectionModel().selectedRows()})
        if not rows or rows[0] == 0:
            return
        for row in rows:
            self._swap_rows(row - 1, row)
        self.table.selectRow(rows[0] - 1)
        self.changed.emit()

    def _move_down(self) -> None:
        rows = sorted({i.row() for i in self.table.selectionModel().selectedRows()})
        if not rows or rows[-1] == self.table.rowCount() - 1:
            return
        for row in reversed(rows):
            self._swap_rows(row, row + 1)
        self.table.selectRow(rows[0] + 1)
        self.changed.emit()

    def _swap_rows(self, a: int, b: int) -> None:
        self.table.blockSignals(True)
        for col in range(self.table.columnCount()):
            item_a = self.table.takeItem(a, col)
            item_b = self.table.takeItem(b, col)
            self.table.setItem(a, col, item_b)
            self.table.setItem(b, col, item_a)
        self.table.blockSignals(False)

    # ---- Public API ----

    def get_orientations(self) -> list[Orientation]:
        return [self._row_to_orientation(r) for r in range(self.table.rowCount())]
