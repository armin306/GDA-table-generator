"""Common parameters panel."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QDoubleSpinBox, QSpinBox,
    QRadioButton, QHBoxLayout, QCheckBox, QComboBox,
)
from PyQt6.QtCore import pyqtSignal

from gda_table_gen.core.generator import CollectionParams


class CommonParamsPanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # ---- Visit / sample ----
        visit_box = QGroupBox("Visit / Sample")
        vg = QGridLayout(visit_box)
        vg.addWidget(QLabel("Visit path:"), 0, 0)
        self.visit_path = QLineEdit("/dls/i23/data/2026/")
        vg.addWidget(self.visit_path, 0, 1)
        vg.addWidget(QLabel("Sample name:"), 1, 0)
        self.sample_name = QLineEdit("sample")
        vg.addWidget(self.sample_name, 1, 1)
        root.addWidget(visit_box)

        # ---- Experiment type ----
        exp_box = QGroupBox("Experiment")
        eg = QHBoxLayout(exp_box)
        self.rb_sad       = QRadioButton("SAD")
        self.rb_mad       = QRadioButton("MAD")
        self.rb_spread    = QRadioButton("SPREAD")
        self.rb_sad.setChecked(True)
        self.chk_interleaved = QCheckBox("Wavelength interleaved")
        self.chk_interleaved.setChecked(True)
        for w in (self.rb_sad, self.rb_mad, self.rb_spread, self.chk_interleaved):
            eg.addWidget(w)
        eg.addStretch(1)
        root.addWidget(exp_box)

        # ---- Energies ----
        en_box = QGroupBox("Energies (eV) — comma or space separated")
        el = QVBoxLayout(en_box)
        self.energies_edit = QLineEdit("12000")
        self.energies_edit.setPlaceholderText("e.g. 4500, 4700, 4900")
        el.addWidget(self.energies_edit)
        root.addWidget(en_box)

        # ---- Oscillation ----
        osc_box = QGroupBox("Oscillation")
        og = QGridLayout(osc_box)

        og.addWidget(QLabel("Start angle (°):"), 0, 0)
        self.osc_start = QDoubleSpinBox()
        self.osc_start.setRange(-360, 360)
        self.osc_start.setDecimals(1)
        self.osc_start.setValue(-180.0)
        og.addWidget(self.osc_start, 0, 1)

        og.addWidget(QLabel("Range / image (°):"), 0, 2)
        self.osc_range = QDoubleSpinBox()
        self.osc_range.setRange(0.001, 10)
        self.osc_range.setDecimals(3)
        self.osc_range.setValue(0.1)
        og.addWidget(self.osc_range, 0, 3)

        og.addWidget(QLabel("Images per wedge:"), 1, 0)
        self.n_images = QSpinBox()
        self.n_images.setRange(1, 100000)
        self.n_images.setValue(3600)
        og.addWidget(self.n_images, 1, 1)

        og.addWidget(QLabel("Total images:"), 1, 2)
        self.total_images = QSpinBox()
        self.total_images.setRange(1, 1000000)
        self.total_images.setValue(3600)
        og.addWidget(self.total_images, 1, 3)

        og.addWidget(QLabel("Exposure time (s):"), 2, 0)
        self.exposure_time = QDoubleSpinBox()
        self.exposure_time.setRange(0.001, 600)
        self.exposure_time.setDecimals(3)
        self.exposure_time.setValue(0.1)
        og.addWidget(self.exposure_time, 2, 1)

        root.addWidget(osc_box)

        # ---- Detector ----
        det_box = QGroupBox("Detector / Beam")
        dg = QGridLayout(det_box)

        dg.addWidget(QLabel("Distance (mm):"), 0, 0)
        self.distance = QDoubleSpinBox()
        self.distance.setRange(50, 2000)
        self.distance.setDecimals(3)
        self.distance.setValue(238.0)
        dg.addWidget(self.distance, 0, 1)

        dg.addWidget(QLabel("Resolution (Å):"), 0, 2)
        self.resolution = QDoubleSpinBox()
        self.resolution.setRange(0.5, 100)
        self.resolution.setDecimals(3)
        self.resolution.setValue(2.0)
        dg.addWidget(self.resolution, 0, 3)

        dg.addWidget(QLabel("Transmission (%):"), 1, 0)
        self.transmission = QDoubleSpinBox()
        self.transmission.setRange(0, 100)
        self.transmission.setDecimals(1)
        self.transmission.setValue(100.0)
        dg.addWidget(self.transmission, 1, 1)

        root.addWidget(det_box)

        # ---- ISPyB ----
        ispyb_box = QGroupBox("ISPyB Sample Reference")
        ig = QGridLayout(ispyb_box)
        ig.addWidget(QLabel("blSampleId:"), 0, 0)
        self.bl_sample_id = QSpinBox()
        self.bl_sample_id.setRange(0, 99999999)
        ig.addWidget(self.bl_sample_id, 0, 1)

        ig.addWidget(QLabel("Container ref:"), 0, 2)
        self.container_ref = QSpinBox()
        self.container_ref.setRange(0, 9999)
        ig.addWidget(self.container_ref, 0, 3)

        ig.addWidget(QLabel("Sample location:"), 1, 0)
        self.sample_location = QSpinBox()
        self.sample_location.setRange(0, 9999)
        ig.addWidget(self.sample_location, 1, 1)

        root.addWidget(ispyb_box)

        # ---- Advanced ----
        adv_box = QGroupBox("Advanced")
        ag = QGridLayout(adv_box)
        ag.addWidget(QLabel("Run number (first):"), 0, 0)
        self.run_number = QSpinBox()
        self.run_number.setRange(0, 9999)
        self.run_number.setValue(1)
        ag.addWidget(self.run_number, 0, 1)

        ag.addWidget(QLabel("Dose protocol:"), 0, 2)
        self.dose_protocol = QComboBox()
        self.dose_protocol.addItems(["target_exposure", "target_dose"])
        ag.addWidget(self.dose_protocol, 0, 3)

        ag.addWidget(QLabel("Experiment type:"), 1, 0)
        self.exp_type_combo = QComboBox()
        self.exp_type_combo.addItems(["SAD", "MAD"])
        ag.addWidget(self.exp_type_combo, 1, 1)

        root.addWidget(adv_box)

        # Connect all signals
        for w in (self.visit_path, self.sample_name, self.energies_edit):
            w.textChanged.connect(self.changed)
        for w in (self.osc_start, self.osc_range, self.exposure_time,
                  self.distance, self.resolution, self.transmission):
            w.valueChanged.connect(self.changed)
        for w in (self.n_images, self.total_images, self.bl_sample_id,
                  self.container_ref, self.sample_location, self.run_number):
            w.valueChanged.connect(self.changed)
        for w in (self.rb_sad, self.rb_mad, self.rb_spread, self.chk_interleaved):
            w.toggled.connect(self.changed)
        self.dose_protocol.currentIndexChanged.connect(self.changed)
        self.exp_type_combo.currentIndexChanged.connect(self.changed)

    def parse_energies(self) -> list[float]:
        text = self.energies_edit.text().replace(",", " ")
        result = []
        for token in text.split():
            try:
                result.append(float(token))
            except ValueError:
                pass
        return result or [12000.0]

    def get_params(self) -> CollectionParams:
        exp_map = {"SAD": "SAD", "MAD": "MAD"}
        return CollectionParams(
            visit_path       = self.visit_path.text().rstrip("/"),
            sample_name      = self.sample_name.text().strip() or "sample",
            energies_ev      = self.parse_energies(),
            osc_start        = self.osc_start.value(),
            osc_range        = self.osc_range.value(),
            n_images         = self.n_images.value(),
            total_images     = self.total_images.value(),
            exposure_time    = self.exposure_time.value(),
            distance_mm      = self.distance.value(),
            resolution       = self.resolution.value(),
            transmission     = self.transmission.value(),
            experiment_type  = self.exp_type_combo.currentText(),
            dose_protocol    = self.dose_protocol.currentText(),
            run_number       = self.run_number.value(),
            container_reference = self.container_ref.value(),
            sample_location  = self.sample_location.value(),
            bl_sample_id     = self.bl_sample_id.value(),
            interleaved      = self.chk_interleaved.isChecked(),
        )
