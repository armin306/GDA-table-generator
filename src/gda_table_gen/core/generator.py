"""
Pure XML generation logic — no UI dependencies.

Supports three table types:
  - single:    one wavelength, one orientation
  - spread:    wavelength-interleaved (SPREAD / MAD), one or more orientations
               ordered wedge-first within each orientation
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional

# hc in eV·Å  →  wavelength(Å) = HC / energy(eV)
_HC = 12398.4197


def energy_to_wavelength(energy_ev: float) -> float:
    return _HC / energy_ev


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class Orientation:
    """One crystal orientation (one run)."""
    kappa:       float = 0.0
    phi:         float = 0.0
    x:           Optional[float] = None
    y:           Optional[float] = None
    z:           Optional[float] = None
    beam_size_x: Optional[float] = None
    beam_size_y: Optional[float] = None


@dataclass
class CollectionParams:
    """All parameters shared across the table."""
    # Sample / visit
    visit_path:  str = ""
    sample_name: str = "sample"

    # Energies: list of eV values.  Single-wavelength = one entry.
    energies_ev: List[float] = field(default_factory=lambda: [12000.0])

    # Oscillation
    osc_start:      float = -180.0
    osc_range:      float = 0.1        # degrees per image
    n_images:       int   = 3600       # images per wedge
    total_images:   int   = 3600       # total images for this energy → n_wedges = total/n_images
    exposure_time:  float = 0.1
    overlap:        float = 0.0

    # Detector / beam
    distance_mm:    float = 238.0
    resolution:     float = 2.0
    transmission:   float = 100.0

    # Metadata
    experiment_type: str = "SAD"        # SAD | MAD
    dose_protocol:   str = "target_exposure"
    centring_mode:   str = "UNSPECIFIED"
    axis_choice:     str = "Omega"
    beamstop_pos:    int = 0
    omega_delta:     float = 0.0
    run_number:      int = 1            # base run number; incremented per orientation when >1 orientation

    # ISPyB
    container_reference: int = 0
    sample_location:     int = 0
    bl_sample_id:        int = 0

    # Table type
    interleaved: bool = True   # False = single entry per orientation (simple SAD)


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def _sub(parent: ET.Element, tag: str, text: str = "") -> ET.Element:
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


def _indent(elem: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation in-place."""
    indent = "\n" + "    " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent
    if not level:
        elem.tail = "\n"


def _fmt(v: float, decimals: int = 4) -> str:
    return f"{v:.{decimals}f}"


# ---------------------------------------------------------------------------
# Entry builder
# ---------------------------------------------------------------------------

def _build_entry(
    p: CollectionParams,
    orientation: Orientation,
    run_number: int,
    energy_ev: float,
    energy_counter: int,      # 1-based index into energy list
    wedge_index: int,         # 0-based
    n_energies: int,
) -> ET.Element:
    """Build a single <extendedCollectRequest> element."""

    directory = f"{p.visit_path}/{p.sample_name}"
    wavelength = energy_to_wavelength(energy_ev)

    # Prefix: {energy}_E{counter} for interleaved, diffraction_N for single
    if p.interleaved and n_energies > 1:
        prefix = f"{int(round(energy_ev))}_E{energy_counter}"
    else:
        prefix = "diffraction_1"

    osc_start       = p.osc_start + wedge_index * p.osc_range * p.n_images
    start_image_num = wedge_index * p.n_images + 1

    entry = ET.Element("extendedCollectRequest")

    # ---- collect_request ----
    cr = ET.SubElement(entry, "collect_request")

    fi = ET.SubElement(cr, "fileinfo")
    _sub(fi, "directory", directory)
    _sub(fi, "prefix", prefix)

    osc = ET.SubElement(cr, "oscillation_sequence")
    _sub(osc, "start",              _fmt(osc_start))
    _sub(osc, "range",              _fmt(p.osc_range))
    _sub(osc, "number_of_images",   str(p.n_images))
    _sub(osc, "overlap",            _fmt(p.overlap))
    _sub(osc, "exposure_time",      _fmt(p.exposure_time))
    _sub(osc, "start_image_number", str(start_image_num))
    _sub(osc, "number_of_passes",   "1")

    _sub(cr, "wavelength", f"{wavelength:.10g}")

    res = ET.SubElement(cr, "resolution")
    _sub(res, "upper", str(p.resolution))

    sr = ET.SubElement(cr, "sample_reference")
    _sub(sr, "code", "")
    _sub(sr, "container_reference", str(p.container_reference))
    _sub(sr, "sample_location",     str(p.sample_location))
    _sub(sr, "blSampleId",          str(p.bl_sample_id))

    # ---- top-level fields ----
    _sub(entry, "runNumber",                str(run_number))
    _sub(entry, "sampleDetectorDistanceInMM", _fmt(p.distance_mm))
    _sub(entry, "transmissionInPerCent",    _fmt(p.transmission))
    _sub(entry, "sampleName",              p.sample_name)
    _sub(entry, "visitPath",               p.visit_path)
    _sub(entry, "comment",                 "")
    _sub(entry, "centringMode",            p.centring_mode)
    _sub(entry, "experimentType",          p.experiment_type)
    _sub(entry, "doseProtocol",            p.dose_protocol)
    _sub(entry, "totalNumberOfImages",     str(p.n_images))
    _sub(entry, "fileNameTemplate",
         f"{directory}/{prefix}_{run_number}_%05d.%s")
    _sub(entry, "dnaFileNameTemplate",
         f"{prefix}_{run_number}_#####.%s")
    _sub(entry, "dnaFilePrefix",
         f"{prefix}_{run_number}_")
    _sub(entry, "dnaFileDir",              directory)
    _sub(entry, "hasTransmission",         "true")
    _sub(entry, "beamstopPosition",        str(p.beamstop_pos))
    _sub(entry, "kappa",                   _fmt(orientation.kappa))
    _sub(entry, "phi",                     _fmt(orientation.phi))
    _sub(entry, "omegaDelta",              _fmt(p.omega_delta))
    _sub(entry, "axisChoice",              p.axis_choice)

    # samplePosition only when at least one coordinate is set
    if any(v is not None for v in (orientation.x, orientation.y, orientation.z)):
        sp = ET.SubElement(entry, "samplePosition")
        _sub(sp, "x", _fmt(orientation.x if orientation.x is not None else 0.0))
        _sub(sp, "y", _fmt(orientation.y if orientation.y is not None else 0.0))
        _sub(sp, "z", _fmt(orientation.z if orientation.z is not None else 0.0))

    bp = ET.SubElement(entry, "beamProfile")
    _sub(bp, "beamSizeX",
         _fmt(orientation.beam_size_x if orientation.beam_size_x is not None else 0.0))
    _sub(bp, "beamSizeY",
         _fmt(orientation.beam_size_y if orientation.beam_size_y is not None else 0.0))

    return entry


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_xml(
    params: CollectionParams,
    orientations: List[Orientation],
) -> str:
    """
    Generate the full GDA XML string for the given parameters and orientations.

    Ordering:
      For each orientation:
        For each wedge position:
          For each energy (if interleaved)
    """
    if not orientations:
        orientations = [Orientation()]

    root = ET.Element("ExtendedCollectRequests")
    _sub(root, "usingDna", "false")

    n_energies = len(params.energies_ev)
    n_wedges   = max(1, params.total_images // params.n_images)
    multi_orientation = len(orientations) > 1

    for ori_idx, orientation in enumerate(orientations):
        run_number = (params.run_number + ori_idx) if multi_orientation else params.run_number

        if params.interleaved and n_energies > 1:
            # Wedge-first, energy-second interleaving
            for wedge_idx in range(n_wedges):
                for e_idx, energy_ev in enumerate(params.energies_ev):
                    entry = _build_entry(
                        params, orientation, run_number,
                        energy_ev, e_idx + 1, wedge_idx, n_energies,
                    )
                    root.append(entry)
        else:
            # Single entry per orientation (simple SAD / one-shot)
            entry = _build_entry(
                params, orientation, run_number,
                params.energies_ev[0], 1, 0, 1,
            )
            root.append(entry)

    _indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        root, encoding="unicode"
    )
