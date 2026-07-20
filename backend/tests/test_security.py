from app.auth.security import hash_password, verify_password, create_token, decode_token

def test_hash_roundtrip():
    h = hash_password("secret")
    assert h != "secret"
    assert verify_password("secret", h)
    assert not verify_password("bad", h)

def test_token_roundtrip():
    t = create_token({"sub": "1", "rol": "admin"})
    data = decode_token(t)
    assert data["sub"] == "1"
    assert data["rol"] == "admin"
