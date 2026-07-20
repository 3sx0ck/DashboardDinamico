from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"


def test_funnel_capital_totales():
    data = parse_pmk(FIX)
    f = data["funnel"]
    assert f["ofertas"] >= 155
    assert set(["ofertas", "desistidos", "enCurso", "promesas", "escrituras"]) <= f.keys()


def test_canal_dos_entradas():
    data = parse_pmk(FIX)
    canales = {c["canal"] for c in data["canal"]}
    assert "Capital Inteligente" in canales
    assert "Brokers" in canales
