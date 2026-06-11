# GDA Table Generator

A PyQt6 desktop GUI for generating GDA (Generic Data Acquisition) XML data collection tables for the I23 beamline at Diamond Light Source.

## Overview

GDA uses XML files (`ExtendedCollectRequests`) to define data collection sequences. Building these tables by hand is error-prone and tedious — particularly for complex experiments involving many energies, wedge positions, and crystal orientations. This tool generates correct, ready-to-load XML from a small set of user-defined parameters.

## Supported experiment types

| Type | Description |
|---|---|
| Simple SAD | Single wavelength, single orientation — one XML entry |
| MAD / SPREAD | Wavelength-interleaved: for each wedge position, all energies are collected before moving to the next wedge. Generates `n_wedges × n_energies` entries. |
| Multi-orientation | Multiple crystal orientations (kappa/phi settings with independent centring). Each orientation is a separate entry with its own sample position. |
| Combined | Multi-orientation + wavelength interleaving. Run number increments per orientation. |

## Installation

Requires Python 3.9+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/armin306/GDA-table-generator.git
cd GDA-table-generator
uv run gda-table-gen
```

EPICS readout (live motor positions from the beamline) requires `cothread`:

```bash
uv run --extra epics gda-table-gen
```

The GUI runs fully offline without `cothread` — EPICS fields can be entered manually.

## Usage

### 1. Common parameters

Fill in the top section:

- **Visit path** — e.g. `/dls/i23/data/2026/cm44175-3`
- **Sample name** — used to construct the output directory (`{visit_path}/{sample_name}`) and file prefixes
- **Wavelength interleaved** checkbox — controls whether energies are interleaved across wedges (SPREAD/MAD) or the table is a simple sequence
- **Energies (eV)** — comma or space separated list; a single value gives a single-wavelength collection
- **Images per wedge / Total images** — `total / per_wedge` gives the number of wedge steps
- **ISPyB fields** — `blSampleId`, container reference, and sample location from the ISPyB sample registration

### 2. Orientations

Each row in the orientations table defines one crystal orientation:

| Column | Description |
|---|---|
| Kappa / Phi | Goniometer angles (°) |
| X / Y / Z | Sample centring position (mm); leave blank to use the current GDA position |
| Beam X / Y | Beam size at this orientation |

**Capture from EPICS** reads all motor positions live from the beamline control system and adds a new row. **Capture & update selected** overwrites the selected row with current positions.

Rows can be reordered with the ▲ / ▼ buttons.

### 3. XML preview and saving

The XML preview updates live as parameters change. The entry count is shown above the preview. Click **Save XML…** to write the file — the default filename is `{sample_name}_table.xml` and the default directory is the visit path.

The saved file can be loaded directly into GDA via `Run > Open Data Collection Plan`.

## XML format notes

The following fields are derived automatically and are never entered manually:

| Field | Rule |
|---|---|
| `directory` | `{visitPath}/{sampleName}` |
| `prefix` | `{energy_eV}_E{counter}` (interleaved) or `diffraction_1` (single) |
| `wavelength` | 12398.4197 / energy_eV |
| `start` | `osc_start + wedge_index × (range × n_images)` |
| `start_image_number` | `wedge_index × n_images + 1` |
| `fileNameTemplate` | `{directory}/{prefix}_{runNumber}_%05d.%s` |
| `dnaFileNameTemplate` | `{prefix}_{runNumber}_#####.%s` |
| `dnaFilePrefix` | `{prefix}_{runNumber}_` |
| `samplePosition` | Only included when at least one of X, Y, Z is set |

## EPICS PVs (I23)

| Parameter | PV |
|---|---|
| Kappa | `BL23I-MO-GONIO-01:KAPPA.RBV` |
| Phi | `BL23I-MO-GONIO-01:PHI.RBV` |
| X | `BL23I-MO-GONIO-01:X.RBV` |
| Y | `BL23I-MO-GONIO-01:Y.RBV` |
| Z | `BL23I-MO-GONIO-01:Z.RBV` |
| Beam size X | `BL23I-AL-SLITS-04:X:SIZE.RBV` |
| Beam size Y | `BL23I-AL-SLITS-04:Y:SIZE.RBV` |

PV names are defined in `src/gda_table_gen/core/epics.py`.

## Code structure

```
src/gda_table_gen/
  app.py                  Entry point (main())
  core/
    generator.py          Pure XML generation logic — no UI dependencies
    epics.py              EPICS PV read helpers with offline fallback
  ui/
    main_window.py        Top-level window, live preview, save
    common_params.py      Shared parameters panel
    orientations.py       Orientations table with EPICS capture buttons
```

The `core/` layer has no dependency on PyQt6 and can be used or tested independently.

## Platform

Designed for Diamond Linux workstations. Supports remote NX and X11 forwarding (`ssh -Y`). Run via `uv run gda-table-gen` from the repository root.
