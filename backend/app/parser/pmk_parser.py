from __future__ import annotations

import re
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

_MESES_MAP = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

_META_RE = re.compile(r"del\s+(\d+)\s+al\s+(\d+)\s+de\s+(\w+)\s+(\d{4})", re.IGNORECASE)


def _parse_meta(wb) -> dict[str, Any]:
    try:
        ws = wb["AVANCE ESC."]
        raw = _cell(ws, 2, 2)
        if not isinstance(raw, str):
            raise ValueError("B2 no es texto")
        match = _META_RE.search(raw)
        if not match:
            raise ValueError("B2 no coincide con el patron esperado")
        day_from, day_to, month_name, year = match.groups()
        month_key = month_name.strip().lower()
        month = _MESES_MAP.get(month_key)
        if month is None:
            raise ValueError(f"mes desconocido: {month_name}")
        year_int = int(year)
        day_to_int = int(day_to)
        month_abbr = month_name.strip()[:3].lower()
        return {
            "proyecto": "PMK",
            "periodo": f"{year_int}-{month:02d}",
            "semana": f"{int(day_from)}-{day_to_int} {month_abbr}",
            "fecha": f"{year_int}-{month:02d}-{day_to_int:02d}",
        }
    except Exception:
        return {"proyecto": "PMK", "periodo": "desconocido", "semana": "s/f", "fecha": None}


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


def _mes_actual(wb) -> str | None:
    """Nombre del mes en curso, derivado de AVANCE ESC. B2."""
    import re
    ws = wb["AVANCE ESC."]
    txt = str(_cell(ws, 2, 2) or "")
    m = re.search(r"de\s+([A-Za-zñÑáéíóúÁÉÍÓÚ]+)\s+\d{4}", txt)
    return m.group(1).capitalize() if m else None


def _find_mes_row(ws, col: int, mes: str, r0: int = 13, r1: int = 25) -> int | None:
    mes_l = mes.strip().lower()
    for r in range(r0, r1 + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and v.strip().lower() == mes_l:
            return r
    return None


def _parse_funnel(wb) -> dict[str, Any]:
    """Funnel del MES en curso (Capital + Brokers), no el acumulado anual.

    GESTIÓN: bloque Capital con meses en col B(2) y funnel Ofertas/Desistidos/
    EnCurso/Promesas/Escrituras en C-G(3-7); bloque Brokers con meses en col L(12)
    y funnel en M-Q(13-17). Los bloques están desfasados, por eso se busca por
    etiqueta de mes en cada uno. Suma ambos canales.
    """
    ws = wb["GESTIÓN JUNIO"]
    mes = _mes_actual(wb)

    def bloque(label_col: int, val_start: int) -> list[int]:
        if not mes:
            return [0, 0, 0, 0, 0]
        r = _find_mes_row(ws, label_col, mes)
        if not r:
            return [0, 0, 0, 0, 0]
        return [int(_num(ws.cell(r, val_start + i).value)) for i in range(5)]

    cap = bloque(2, 3)    # Capital Inteligente
    brk = bloque(12, 13)  # Brokers
    tot = [cap[i] + brk[i] for i in range(5)]
    return {
        "ofertas": tot[0],
        "desistidos": tot[1],
        "enCurso": tot[2],
        "promesas": tot[3],
        "escrituras": tot[4],
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


def _sum_label_row(ws, label_col: int, label: str, value_start_col: int, value_end_col: int, max_row: int) -> float:
    """Sum numeric values across a row range, for every row whose label
    (in label_col) exactly matches `label`. Used for JULIO's daily-tracked
    metrics ("VISITAS", "LEADS EFECTIVOS") which repeat once per torre
    block and spread their values across many day columns.
    """
    target = label.strip().upper()
    total = 0.0
    for row in range(1, max_row + 1):
        value = ws.cell(row=row, column=label_col).value
        if isinstance(value, str) and value.strip().upper() == target:
            for col in range(value_start_col, value_end_col + 1):
                total += _num(ws.cell(row=row, column=col).value)
    return total


def _parse_marketing(wb) -> dict[str, Any]:
    ws_medios = wb["Medios (JUNIO)"]
    # Medios (JUNIO): label col B(2), value col C(3), rows 4-11.
    medios = []
    for row in range(4, 12):
        medio = _cell(ws_medios, row, 2)
        if isinstance(medio, str) and medio.strip():
            medios.append({"medio": medio.strip(), "cant": _num(_cell(ws_medios, row, 3))})

    ws_julio = wb["JULIO"]
    # JULIO: labels "VISITAS" and "LEADS EFECTIVOS" repeat once per torre
    # block (col B), with daily values spread across cols C..AR.
    visitas_sala = _sum_label_row(ws_julio, 2, "VISITAS", 3, 44, ws_julio.max_row)
    leads_efectivos = _sum_label_row(ws_julio, 2, "LEADS EFECTIVOS", 3, 44, ws_julio.max_row)

    return {
        "medios": medios,
        "visitasSala": visitas_sala,
        "leadsEfectivos": leads_efectivos,
        "banco": [],
    }


def _parse_avance(wb) -> dict[str, Any]:
    ws = wb["AVANCE ESC."]
    semana = _cell(ws, 2, 2)
    if not isinstance(semana, str):
        semana = None
    else:
        semana = semana.strip()
    row = _find_in_col(ws, 2, "Por firmar", max_row=20)
    por_firmar = _num(_cell(ws, row, 3)) if row else 0.0
    return {"semana": semana, "porFirmar": por_firmar}


_ESTADO_MAP = {
    "ESC.": "ESC",
    "ESC": "ESC",
    "PROM": "PROM",
    "RES.": "RES",
    "RES": "RES",
    "DISPONIBLE": "DISP",
    "INVM": "INVM",
}


def _map_estado(raw: Any) -> str:
    if not isinstance(raw, str):
        return "DESCONOCIDO"
    key = raw.strip().upper()
    return _ESTADO_MAP.get(key, key)


def _parse_grilla(wb) -> list[dict[str, Any]]:
    ws = wb["Ofertas x semana (JUNIO)"]

    # Locate the torre number from the header text (e.g. "TORRE 3 -
    # ARAUCARIA - ORIENTE") in the first few rows.
    torre = 0
    for row in ws.iter_rows(min_row=1, max_row=5):
        for cell in row:
            if isinstance(cell.value, str) and "TORRE" in cell.value.upper():
                match = re.search(r"TORRE\s*(\d+)", cell.value.upper())
                if match:
                    torre = int(match.group(1))
                    break
        if torre:
            break

    result = []
    max_row = ws.max_row
    max_col = ws.max_column
    for row in range(1, max_row + 1):
        piso = _cell(ws, row, 2)
        if not isinstance(piso, (int, float)) or isinstance(piso, bool):
            continue
        col = 3
        while col + 1 <= max_col:
            depto = _cell(ws, row, col)
            estado_raw = _cell(ws, row, col + 1)
            if depto is not None:
                result.append(
                    {
                        "torre": torre,
                        "piso": int(piso),
                        "depto": depto,
                        "estado": _map_estado(estado_raw),
                    }
                )
            col += 2
    return result
