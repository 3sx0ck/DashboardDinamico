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
        assert {"torre", "cara", "piso", "depto", "estado"} <= u.keys()


def test_grilla_sin_desconocidos():
    # El parser antiguo generaba filas basura con estado "DESCONOCIDO" por
    # desalineación de columnas entre los bloques ORIENTE/PONIENTE. El nuevo
    # detecta pares (depto numérico + estado texto) por contenido.
    g = parse_pmk(FIX)["grillaUnidades"]
    estados = {u["estado"] for u in g}
    assert "DESCONOCIDO" not in estados


def test_grilla_ambas_caras():
    g = parse_pmk(FIX)["grillaUnidades"]
    caras = {u["cara"] for u in g}
    assert "ORIENTE" in caras
    assert "PONIENTE" in caras
    assert all(u["torre"] == 3 for u in g)


def test_meta_periodo():
    assert "periodo" in parse_pmk(FIX)["meta"]
