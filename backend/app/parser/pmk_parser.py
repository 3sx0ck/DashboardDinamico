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


# ESCRITURACIÓN sheet: per-torre blocks calibrated against the real fixture.
# Torre 2: label col B(2), value col D(4).
# Torre 3: label col J(10), value col L(12).
# Torre 5 has no "TOTAL VENTA" label; the closest equivalent found in the
# fixture is "SUMA TOTAL VENTA TORRE 5" (label col F(6), value col H(8)).
_VENTAS_TORRE_CONFIG = [
    {"torre": 2, "label_col": 2, "value_col": 4, "venta_label": "TOTAL VENTA", "recibir_label": "X RECIBIR"},
    {"torre": 3, "label_col": 10, "value_col": 12, "venta_label": "TOTAL VENTA", "recibir_label": "X RECIBIR"},
    {"torre": 5, "label_col": 6, "value_col": 8, "venta_label": "SUMA TOTAL VENTA TORRE 5", "recibir_label": "X RECIBIR"},
]


def _parse_ventas(wb) -> dict[str, Any]:
    ws = wb["ESCRITURACIÓN"]
    por_torre = []
    total_uf = 0.0
    for cfg in _VENTAS_TORRE_CONFIG:
        venta_row = _find_in_col(ws, cfg["label_col"], cfg["venta_label"])
        recibir_row = _find_in_col(ws, cfg["label_col"], cfg["recibir_label"])
        venta_uf = _num(_cell(ws, venta_row, cfg["value_col"])) if venta_row else 0.0
        x_recibir_uf = _num(_cell(ws, recibir_row, cfg["value_col"])) if recibir_row else 0.0
        por_torre.append(
            {
                "torre": cfg["torre"],
                "ventaUF": venta_uf,
                "xRecibirUF": x_recibir_uf,
            }
        )
        total_uf += venta_uf
    return {"ventaTotalUF": total_uf, "porTorre": por_torre}


# Tipología sub-blocks in ESCRITURACIÓN: headers "NO O NP P SP SO % Stock
# Total" at cols S..Z (19..26), tipología label in col P (16), rows below
# marked with a "•" bullet (e.g. "•2D-2B"). Two such blocks were located in
# the fixture: one for Torre 3 (header row 4, data rows 5-7) and one for
# Torre 2 (header row 17, data rows 18-20). Torre 5 has no equivalent block.
#
# ASSUMPTION (semantic mapping, genuinely ambiguous from the raw labels):
#   NO ("No Ofertado")  -> disponible
#   O  ("Ofertado")     -> reservado
#   P  ("Promesado")    -> promesado
#   SO ("Sin Oferta"?)  -> escriturado (best-effort stand-in; the sheet has
#                          no column that unambiguously maps to escriturado
#                          at the tipología level)
#   NP and SP are ignored (likely complements of NP/P and SP/O respectively).
_STOCK_TIPOLOGIA_LABEL_COL = 16
_STOCK_COL_NO = 19
_STOCK_COL_O = 20
_STOCK_COL_P = 22
_STOCK_COL_SO = 24
_STOCK_BLOCKS = [
    {"torre": 3, "start_row": 5, "end_row": 7},
    {"torre": 2, "start_row": 18, "end_row": 20},
]


def _parse_stock(wb) -> dict[str, Any]:
    ws = wb["ESCRITURACIÓN"]
    result = []
    for block in _STOCK_BLOCKS:
        for row in range(block["start_row"], block["end_row"] + 1):
            label = _cell(ws, row, _STOCK_TIPOLOGIA_LABEL_COL)
            if not isinstance(label, str):
                continue
            tipologia = label.strip().lstrip("•").strip()
            if not tipologia:
                continue
            result.append(
                {
                    "torre": block["torre"],
                    "tipologia": tipologia,
                    "disponible": _num(_cell(ws, row, _STOCK_COL_NO)),
                    "reservado": _num(_cell(ws, row, _STOCK_COL_O)),
                    "promesado": _num(_cell(ws, row, _STOCK_COL_P)),
                    "escriturado": _num(_cell(ws, row, _STOCK_COL_SO)),
                }
            )
    return {"porTorre": result}


def _parse_funnel(wb) -> dict[str, Any]:
    ws = wb["GESTIÓN JUNIO"]
    # Row 12 = ACUMULADO totals row (Capital Inteligente), cols C..G
    return {
        "ofertas": _num(_cell(ws, 12, 3)),
        "desistidos": _num(_cell(ws, 12, 4)),
        "enCurso": _num(_cell(ws, 12, 5)),
        "promesas": _num(_cell(ws, 12, 6)),
        "escrituras": _num(_cell(ws, 12, 7)),
    }


MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def _parse_evolucion(wb) -> list[dict[str, Any]]:
    ws = wb["GESTIÓN JUNIO"]
    result = []
    for row in range(13, 25):
        mes = _cell(ws, row, 2)
        if isinstance(mes, str) and mes.strip() in MESES:
            result.append(
                {
                    "mes": mes.strip(),
                    "ofertas": _num(_cell(ws, row, 3)),
                    "desistidos": _num(_cell(ws, row, 4)),
                    "enCurso": _num(_cell(ws, row, 5)),
                    "promesas": _num(_cell(ws, row, 6)),
                    "escrituras": _num(_cell(ws, row, 7)),
                }
            )
    return result


def _parse_canal(wb) -> list[dict[str, Any]]:
    ws = wb["GESTIÓN JUNIO"]
    # Rows 5-8: Reservas/Promesas/Escrituras/Desistidos, "Mes" column
    # Capital Inteligente = col D (4), Brokers = col N (14)
    row_labels = {5: "reservas", 6: "promesas", 7: "escrituras", 8: "desistidos"}
    canales = [
        {"nombre": "Capital Inteligente", "col": 4},
        {"nombre": "Brokers", "col": 14},
    ]
    result = []
    for canal in canales:
        entry: dict[str, Any] = {"canal": canal["nombre"]}
        for row, key in row_labels.items():
            entry[key] = _num(_cell(ws, row, canal["col"]))
        result.append(entry)
    return result


def _parse_marketing(wb) -> dict[str, Any]:
    return {"medios": [], "visitasSala": 0, "leadsEfectivos": 0, "banco": []}


def _parse_avance(wb) -> dict[str, Any]:
    return {}


def _parse_grilla(wb) -> list[dict[str, Any]]:
    return []
