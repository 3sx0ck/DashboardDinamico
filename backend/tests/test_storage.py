from app.storage import put_raw, ensure_bucket


def test_put_raw():
    ensure_bucket()
    key = put_raw("test/x.bin", b"hola")
    assert key == "test/x.bin"
