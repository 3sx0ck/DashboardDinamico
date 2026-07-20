from __future__ import annotations

import openpyxl
from typing import Any


def parse_pmk(path: str) -> dict[str, Any]:
    wb = openpyxl.load_workbook(path, data_only=True)
    return {
        "meta": _parse_meta(wb),
        "ventas": _parse_ventas(wb),
        "stock": _parse_stock(wb),
        "funnel": _parse_funnel(wb),
        "evolucionMensual": _parse_evolucion(wb),
        "canal": _parse_canal(wb),
        "marketing": _parse_marketing(wb),
        "avanceSemanal": _parse_avance(wb),
        "grillaUnidades": _parse_grilla(wb),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cell(ws, row: int, col: int):
    """Return the raw value of a cell by 1-indexed row/col."""
    return ws.cell(row=row, column=col).value


def _num(value: Any) -> float:
    """Best-effort coercion of a cell value to a float, defaulting to 0."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            try:
                return float(value.strip())
            except ValueError:
                return 0.0
    return 0.0


def _find_in_col(ws, col: int, label: str, max_row: int = 48, min_row: int = 1) -> int | None:
    """Search a column for a cell whose stripped/upper text matches label.

    Returns the row number, or None if not found.
    """
    target = label.strip().upper()
    for row in range(min_row, max_row + 1):
        value = ws.cell(row=row, column=col).value
        if isinstance(value, str) and value.strip().upper() == target:
            return row
    return None


# ---------------------------------------------------------------------------
# Section parsers (implemented incrementally, TDD)
# ---------------------------------------------------------------------------

def _parse_meta(wb) -> dict[str, Any]:
    return {"proyecto": "PMK", "periodo": "2026-07"}


def _parse_ventas(wb) -> dict[str, Any]:
    return {"ventaTotalUF": 0, "porTorre": []}


def _parse_stock(wb) -> dict[str, Any]:
    return {"porTorre": []}


def _parse_funnel(wb) -> dict[str, Any]:
    return {}


def _parse_evolucion(wb) -> list[dict[str, Any]]:
    return []


def _parse_canal(wb) -> list[dict[str, Any]]:
    return []


def _parse_marketing(wb) -> dict[str, Any]:
    return {"medios": [], "visitasSala": 0, "leadsEfectivos": 0, "banco": []}


def _parse_avance(wb) -> dict[str, Any]:
    return {}


def _parse_grilla(wb) -> list[dict[str, Any]]:
    return []
