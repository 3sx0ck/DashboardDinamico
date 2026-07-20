from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"


def test_funnel_mes_actual_combinado():
    # Funnel del mes en curso (Julio) = Capital [1,0,5,0,0] + Brokers [1,2,17,3,8]
    data = parse_pmk(FIX)
    f = data["funnel"]
    assert set(["ofertas", "desistidos", "enCurso", "promesas", "escrituras"]) <= f.keys()
    assert f["ofertas"] == 2
    assert f["desistidos"] == 2
    assert f["enCurso"] == 22
    assert f["promesas"] == 3
    assert f["escrituras"] == 8


def test_canal_dos_entradas():
    data = parse_pmk(FIX)
    canales = {c["canal"] for c in data["canal"]}
    assert "Capital Inteligente" in canales
    assert "Brokers" in canales
