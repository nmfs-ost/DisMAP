## Copilot / Agent instructions for DisMAP

Short, actionable notes to help an AI agent be productive in this repository.

### Purpose

This document provides essential guidelines and context for AI agents working within the DisMAP repository. The goal is to ensure efficient, safe, and effective contributions, particularly concerning the R data processing and ArcGIS Python analysis components.


- Project split:
  - `data_processing_rcode/` — R scripts to download and compile raw survey data. Entry point: open `DisMAP.Rproj` and run the `Compile_Dismap_Current.R` and `create_data_for_map_generation.R` scripts. These generate the CSV/GDB inputs consumed by the Python/ArcGIS layer.
  - `ArcGIS-Analysis-Python/` — Python-based ArcGIS Pro tooling that reads the processed CSVs and generates interpolated rasters, mosaics and indicators. Main code is under `ArcGIS-Analysis-Python/src/dismap_tools/`.

- Environment and how to run (high level):
  - The Python tools require an ArcGIS Pro Python environment (ArcPy available). Run scripts from the ArcGIS Pro Python interpreter (for example `arcgispro-py3`).
  - R workflows should be run from the R project (`DisMAP.Rproj`) so relative paths and project options work.

- Project-specific patterns and conventions:
  - Windows paths and raw f-strings are used widely (e.g., rf"{home_folder}\{project}.aprx"). Prefer Windows-style paths when editing code examples.
  - The repository uses date-named version folders (e.g., `"August 1 2025"`) that contain geodatabases and build artifacts. Avoid editing large binary datasets in those folders; treat them as outputs.
  - Many Python modules import `arcpy` and call `arcpy.mp.ArcGISProject(...)` (e.g., `src/dismap_tools/publish_to_portal_director.py`, `dismap_project_setup.py`, and `dismap_metadata_processing.py`). Changes to ArcPy usage must be validated inside an ArcGIS Pro environment.
  - The Python package uses a `src/` layout and a `setup.py` that expects `src/version.py`. Confirm `src/version.py` exists or define `__version__` before packaging.

- Key files to open first (quick tour):
  - `README.md` (repo root) — project overview and where R/ArcGIS pieces live.
  - `DisMAP.Rproj` and `data_processing_rcode/Compile_Dismap_Current.R` — how raw data is ingested.
  - `ArcGIS-Analysis-Python/src/dismap_tools/` — main Python processing scripts (directors/workers, publish scripts).
  - `ArcGIS-Analysis-Python/DisMAP.aprx` — base ArcGIS Pro project referenced by scripts.
  - `ArcGIS-Analysis-Python/setup.py` — packaging layout (src/ package style).

- Common developer workflows (what agents should do / check):
  - Before editing processing logic, reproduce a minimal run: run the R compile script to generate the CSV inputs, then run a single Python director (e.g., `dev_dismap_director.py`) inside ArcGIS Pro Python to confirm behavior.
  - When adjusting ArcPy code, test in ArcGIS Pro (or the `arcgispro-py3` conda env) — unit tests are minimal/absent (`conftest.py` is empty), so use small smoke runs.
  - Publishing scripts call portal APIs via ArcPy and require credentials and a valid `.aprx`. Do not attempt to publish during dry edits; mock or dry-run by inspecting `arcpy.mp` calls.

- Examples (where to change things safely):
  - To add a preprocessing step, modify `data_processing_rcode/create_data_for_map_generation.R` so outputs remain CSVs expected by `src/dismap_tools/*`.
  - To run a single processing step in Python, open ArcGIS Pro Python prompt and run the target director script from `ArcGIS-Analysis-Python\\src\\dismap_tools\\`.

- Integration points & external dependencies to be aware of:
  - ArcGIS Pro / ArcPy (required). Scripts assume ArcGIS Pro APIs and Windows paths.
  - ArcGIS Portal (used by `publish_to_portal_director.py`) — publishing requires portal credentials and network access.
  - Large geodatabases and rasters are stored under versioned folders — these are produced artifacts.

- Safety and commit guidance for agents:
  - **Do not modify or commit large binary geodatabases/raster files.** These are generated outputs. Prefer changes to scripts that produce them.
  - `.aprx` files are referenced but commonly ignored by `.gitignore`; double-check before committing APRX changes.
  - If `src/version.py` is missing, do not fabricate a version without asking — instead add a comment and propose the change in a PR.
  - Always respect the `.gitignore` rules. If new output types are generated, consider adding them to the appropriate `.gitignore` file.

- Code Style and Quality:
  - For Python code, adhere to PEP 8 guidelines.
  - For R code, follow standard R style guides (e.g., Hadley Wickham's style guide).
  - Prioritize clear, readable, and well-commented code.

- Quick checklist for a PR from an agent:
  1. Describe which director/worker you ran and the minimal dataset used.
  2. Confirm tests or smoke-runs and the ArcGIS Pro environment used (path to Python interpreter and Pro version).
  3. Point to exact input CSVs and output GDB/rasters affected (path under a version folder).

If anything above is unclear or you want the file to include more specific run commands for your local ArcGIS Pro installation, tell me which pieces you want expanded and I'll iterate.
