#!/usr/bin/env python3
"""
recalc.py — Recalculate Excel formulas using MS Office (xlwings/Windows COM/macOS AppleScript).

openpyxl writes formula strings but does NOT compute values. Excel will
recalculate on open, but for automated pipelines (validation, QC, handoff)
we need calculated values written back into the file. This script forces
recalculation by driving Microsoft Excel through one of three engines:

  1. xlwings (Python lib, native macOS/Windows)
  2. WSL → Windows Excel.exe via PowerShell COM
  3. macOS Microsoft Excel.app via osascript (AppleScript)

Usage:
    python scripts/recalc.py <file.xlsx> [timeout_seconds]

Requires:
    - MS Office (Excel) — installed on host. Optionally `pip install xlwings`
      for direct Python control (recommended on macOS/Windows native).
    - openpyxl (for post-recalc error scanning)
        pip install openpyxl

Returns JSON to stdout with:
    - status: "success" | "errors_found" | "failed"
    - total_formulas: count of formulas in file
    - total_errors: count of Excel error values
    - error_summary: {error_type: {count, locations}}
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


EXCEL_ERRORS = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#NULL!", "#NUM!", "#N/A"}


def find_excel_engine() -> dict | None:
    """Locate MS Office engine. Priority: xlwings → WSL Windows Excel → macOS osascript.

    Returns dict with 'type' and 'path' keys, or None if no engine found.
    """
    # 1) xlwings (Python lib, macOS/Windows native)
    if importlib.util.find_spec("xlwings") is not None:
        return {"type": "xlwings"}

    # 2) WSL → Windows Excel.exe
    wsl_excel_paths = [
        "/mnt/c/Program Files/Microsoft Office/root/Office16/EXCEL.EXE",
        "/mnt/c/Program Files (x86)/Microsoft Office/root/Office16/EXCEL.EXE",
        "/mnt/c/Program Files/Microsoft Office/Office16/EXCEL.EXE",
    ]
    for p in wsl_excel_paths:
        if Path(p).exists():
            return {"type": "wsl_excel", "path": p}

    # 3) macOS Excel.app via osascript
    mac_excel = Path("/Applications/Microsoft Excel.app")
    if mac_excel.exists() and shutil.which("osascript"):
        return {"type": "macos_osascript", "path": str(mac_excel)}

    return None


def recalc_with_office(xlsx_path: Path, timeout: int) -> None:
    """Force recalculation using MS Office engine."""
    engine = find_excel_engine()
    if engine is None:
        raise RuntimeError(
            "MS Office not found. This pipeline requires Microsoft Excel.\n"
            "  macOS:   Install Microsoft Excel from App Store/MS, or `pip install xlwings`\n"
            "  Windows: Install MS Office, or `pip install xlwings`\n"
            "  WSL:     Install MS Office on Windows host (xlwings auto-detects via /mnt/c/)"
        )

    if engine["type"] == "xlwings":
        import xlwings as xw  # type: ignore[import-not-found]
        # Use Book API directly — macOS Excel doesn't fully support headless App mode.
        wb = xw.Book(str(xlsx_path))
        try:
            wb.app.calculate()
            wb.save()
        finally:
            wb.close()

    elif engine["type"] == "wsl_excel":
        # Convert WSL path to Windows path
        win_path = subprocess.check_output(
            ["wslpath", "-w", str(xlsx_path)], text=True
        ).strip()
        # Use cmd.exe to invoke Excel COM via PowerShell one-liner
        ps_cmd = (
            f'$xl = New-Object -ComObject Excel.Application; '
            f'$xl.Visible = $false; '
            f'$xl.DisplayAlerts = $false; '
            f'$wb = $xl.Workbooks.Open(\\"{win_path}\\"); '
            f'$xl.CalculateFull(); '
            f'$wb.Save(); '
            f'$wb.Close(); '
            f'$xl.Quit()'
        )
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            raise RuntimeError(f"Windows Excel COM failed:\n{result.stderr}")

    elif engine["type"] == "macos_osascript":
        # macOS AppleScript automation (Excel.app required).
        # Note: macOS Excel cannot run truly headless; window may briefly appear.
        # `display alerts` suppresses dialogs during open/save/close.
        applescript = f'''
        tell application "Microsoft Excel"
            set display alerts to false
            open POSIX file "{xlsx_path}"
            calculate
            save active workbook
            close active workbook saving no
            set display alerts to true
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            raise RuntimeError(f"macOS Excel osascript failed:\n{result.stderr}")


def scan_errors(xlsx_path: Path) -> dict:
    """Scan all cells for formulas and Excel error values."""
    try:
        import openpyxl
    except ImportError as e:
        raise ImportError("openpyxl not installed. Run: pip install openpyxl") from e

    wb_formulas = openpyxl.load_workbook(xlsx_path, data_only=False)
    wb_values = openpyxl.load_workbook(xlsx_path, data_only=True)

    total_formulas = 0
    errors: dict[str, dict] = {}

    for sheet_name in wb_formulas.sheetnames:
        ws_f = wb_formulas[sheet_name]
        ws_v = wb_values[sheet_name]
        for row in ws_f.iter_rows():
            for cell in row:
                try:
                    coord = cell.coordinate
                except AttributeError:
                    continue
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    total_formulas += 1
                    computed = ws_v[coord].value
                    if isinstance(computed, str) and computed in EXCEL_ERRORS:
                        entry = errors.setdefault(
                            computed, {"count": 0, "locations": []}
                        )
                        entry["count"] += 1
                        if len(entry["locations"]) < 25:
                            entry["locations"].append(f"{sheet_name}!{coord}")

    total_errors = sum(e["count"] for e in errors.values())
    return {
        "total_formulas": total_formulas,
        "total_errors": total_errors,
        "error_summary": errors,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error": "usage: python recalc.py <file.xlsx> [timeout_seconds]",
                }
            )
        )
        return 2

    xlsx_path = Path(sys.argv[1]).expanduser().resolve()
    timeout = int(sys.argv[2]) if len(sys.argv) >= 3 else 120

    if not xlsx_path.exists():
        print(json.dumps({"status": "failed", "error": f"File not found: {xlsx_path}"}))
        return 2

    try:
        recalc_with_office(xlsx_path, timeout)
    except Exception as e:
        print(json.dumps({"status": "failed", "error": str(e)}))
        return 1

    try:
        scan = scan_errors(xlsx_path)
    except Exception as e:
        print(json.dumps({"status": "failed", "error": f"scan failed: {e}"}))
        return 1

    status = "errors_found" if scan["total_errors"] > 0 else "success"
    print(json.dumps({"status": status, **scan}, indent=2))
    return 0 if status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
