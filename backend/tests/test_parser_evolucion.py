from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"


def test_evolucion_meses():
    ev = parse_pmk(FIX)["evolucionMensual"]
    meses = {r["mes"] for r in ev}
    assert {"Enero", "Febrero", "Marzo"} <= meses
    for r in ev:
        assert {"mes", "ofertas", "promesas", "escrituras"} <= r.keys()
