from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"


def test_ventas_por_torre():
    v = parse_pmk(FIX)["ventas"]
    assert v["ventaTotalUF"] > 0
    torres = {r["torre"] for r in v["porTorre"]}
    assert {2, 3} <= torres


def test_ventas_escriturados():
    # Escriturados = ESC.Pagado + Esc x pagar. Torre 3 trae un total
    # explícito "Escriturados"=154 en la hoja que valida la fórmula
    # (129 ESC.Pagado + 25 Esc x pagar = 154).
    v = parse_pmk(FIX)["ventas"]
    por_torre = {t["torre"]: t for t in v["porTorre"]}
    assert por_torre[3]["escriturados"] == 154
    assert por_torre[2]["escriturados"] == 295  # 285 + 10
    assert por_torre[5]["escriturados"] == 46   # 46 + 0


def test_stock_estructura():
    s = parse_pmk(FIX)["stock"]["porTorre"]
    assert len(s) > 0
    for r in s:
        assert {"torre", "tipologia", "disponible", "reservado", "promesado", "escriturado"} <= r.keys()
