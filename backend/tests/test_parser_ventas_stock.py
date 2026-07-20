from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"


def test_ventas_por_torre():
    v = parse_pmk(FIX)["ventas"]
    assert v["ventaTotalUF"] > 0
    torres = {r["torre"] for r in v["porTorre"]}
    assert {2, 3} <= torres


def test_stock_estructura():
    s = parse_pmk(FIX)["stock"]["porTorre"]
    assert len(s) > 0
    for r in s:
        assert {"torre", "tipologia", "disponible", "reservado", "promesado", "escriturado"} <= r.keys()
