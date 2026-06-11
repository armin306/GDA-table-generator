"""Main application window."""
from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox,
    QScrollArea, QSplitter, QTextEdit, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gda_table_gen.ui.common_params import CommonParamsPanel
from gda_table_gen.ui.orientations import OrientationsPanel
from gda_table_gen.core.generator import generate_xml


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GDA Table Generator")
        self.resize(900, 800)
        self._build_ui()
        self._refresh_preview()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Title
        title = QLabel("GDA Table Generator")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        root.addWidget(title)

        # Main splitter: params (top) / preview (bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # ---- Top: scrollable params ----
        params_scroll = QScrollArea()
        params_scroll.setWidgetResizable(True)
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setContentsMargins(4, 4, 4, 4)

        self.common_params = CommonParamsPanel()
        params_layout.addWidget(self.common_params)

        self.orientations = OrientationsPanel()
        params_layout.addWidget(self.orientations)

        params_layout.addStretch(1)
        params_scroll.setWidget(params_widget)
        splitter.addWidget(params_scroll)

        # ---- Bottom: XML preview ----
        preview_widget = QWidget()
        pv = QVBoxLayout(preview_widget)
        pv.setContentsMargins(4, 4, 4, 4)

        preview_hdr = QHBoxLayout()
        self._entry_count_label = QLabel("Entries: 0")
        preview_hdr.addWidget(self._entry_count_label)
        preview_hdr.addStretch(1)

        self.btn_save = QPushButton("Save XML…")
        self.btn_save.clicked.connect(self._save)
        preview_hdr.addWidget(self.btn_save)

        pv.addLayout(preview_hdr)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Monospace", 9))
        self._preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        pv.addWidget(self._preview)

        splitter.addWidget(preview_widget)
        splitter.setSizes([500, 300])

        root.addWidget(splitter)

        # Wire signals
        self.common_params.changed.connect(self._refresh_preview)
        self.orientations.changed.connect(self._refresh_preview)

    # ---- Preview ----

    def _build_xml(self) -> str:
        params       = self.common_params.get_params()
        orientations = self.orientations.get_orientations()
        return generate_xml(params, orientations)

    def _refresh_preview(self) -> None:
        try:
            xml = self._build_xml()
            self._preview.setPlainText(xml)
            count = xml.count("<extendedCollectRequest>")
            self._entry_count_label.setText(f"Entries: {count}")
            self._entry_count_label.setStyleSheet("")
        except Exception as e:
            self._preview.setPlainText(f"Error generating XML:\n{e}")
            self._entry_count_label.setText("Entries: —")
            self._entry_count_label.setStyleSheet("color: red;")

    # ---- Save ----

    def _save(self) -> None:
        try:
            xml = self._build_xml()
        except Exception as e:
            QMessageBox.critical(self, "Generation failed", str(e))
            return

        params = self.common_params.get_params()
        default_name = f"{params.sample_name}_table.xml"
        default_dir  = params.visit_path if os.path.isdir(params.visit_path) else str(Path.home())

        path, _ = QFileDialog.getSaveFileName(
            self, "Save GDA table", os.path.join(default_dir, default_name),
            "XML files (*.xml);;All files (*)"
        )
        if not path:
            return
        try:
            Path(path).write_text(xml, encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))
