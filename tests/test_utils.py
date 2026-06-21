from app.utils import encrypt_md5, parse_maybe_datetime, mask_equip_id


def test_encrypt_md5_consistent():
    assert encrypt_md5("abc") == encrypt_md5("abc")


def test_parse_maybe_datetime_ok():
    assert parse_maybe_datetime("2023-01-01 12:00:00") is not None
    assert parse_maybe_datetime("") is None


def test_mask_equip_id():
    assert mask_equip_id("1234567890") == "123******890"
    assert mask_equip_id(None) == ""
