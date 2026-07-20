from app.parser.pmk_parser import parse_pmk


def test_meta_derivada():
    m = parse_pmk("tests/fixtures/pmk_sample.xlsx")["meta"]
    assert m["periodo"] == "2026-07"
    assert "10" in m["semana"]
    assert m["fecha"] == "2026-07-10"
