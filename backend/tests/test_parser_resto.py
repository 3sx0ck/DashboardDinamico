from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"


def test_marketing_medios():
    m = parse_pmk(FIX)["marketing"]
    medios = {x["medio"].upper() for x in m["medios"]}
    assert {"GOOGLE", "WHATSAPP", "INSTAGRAM"} & medios
    assert m["visitasSala"] >= 0


def test_grilla_unidades():
    g = parse_pmk(FIX)["grillaUnidades"]
    assert len(g) > 0
    for u in g[:5]:
        assert {"torre", "piso", "depto", "estado"} <= u.keys()


def test_meta_periodo():
    assert "periodo" in parse_pmk(FIX)["meta"]
