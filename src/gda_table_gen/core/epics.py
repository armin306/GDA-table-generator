"""
EPICS PV read helpers.

Uses cothread.catools when available; falls back to None so the GUI
can still run offline or in development without a beamline connection.
"""
from __future__ import annotations

from typing import Optional

try:
    from cothread.catools import caget as _caget
    _EPICS_AVAILABLE = True
except ImportError:
    _EPICS_AVAILABLE = False

# ---------------------------------------------------------------------------
# PV definitions for I23
# ---------------------------------------------------------------------------

PVS = {
    "kappa":     "BL23I-MO-GONIO-01:KAPPA.RBV",
    "phi":       "BL23I-MO-GONIO-01:PHI.RBV",
    "x":         "BL23I-MO-GONIO-01:X.RBV",
    "y":         "BL23I-MO-GONIO-01:Y.RBV",
    "z":         "BL23I-MO-GONIO-01:Z.RBV",
    "beam_size_x": "BL23I-AL-SLITS-04:X:SIZE.RBV",
    "beam_size_y": "BL23I-AL-SLITS-04:Y:SIZE.RBV",
}


def is_available() -> bool:
    """Return True if cothread is importable."""
    return _EPICS_AVAILABLE


def read_pv(pv: str, timeout: float = 2.0) -> Optional[float]:
    """Read a single PV and return its value, or None on failure."""
    if not _EPICS_AVAILABLE:
        return None
    try:
        return float(_caget(pv, timeout=timeout))
    except Exception:
        return None


def capture_orientation() -> dict:
    """
    Read all goniometer and beam-size PVs and return a dict with keys:
      kappa, phi, x, y, z, beam_size_x, beam_size_y

    Any PV that cannot be read is returned as None.
    """
    return {name: read_pv(pv) for name, pv in PVS.items()}
