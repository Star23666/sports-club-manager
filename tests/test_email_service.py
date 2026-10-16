"""Password-reset emails remain Chinese and escape untrusted display text."""

from email import message_from_string
from email.header import decode_header, make_header

import pytest

from app import email_service


@pytest.mark.parametrize("fallback", [False, True])
def test_reset_email_is_chinese_and_escapes_template_values(monkeypatch, fallback):
    sent = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            assert (host, port, timeout) == ("smtp.example", 587, 10)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def starttls(self):
            pass

        def login(self, user, password):
            assert (user, password) == ("sender@example.com", "test-secret")

        def sendmail(self, sender, recipients, message):
            sent.append((sender, recipients, message))

    monkeypatch.setattr(email_service.settings, "smtp_host", "smtp.example")
    monkeypatch.setattr(email_service.settings, "smtp_port", 587)
    monkeypatch.setattr(email_service.settings, "smtp_user", "sender@example.com")
    monkeypatch.setattr(email_service.settings, "smtp_password", "test-secret")
    monkeypatch.setattr(email_service.settings, "org_name", "<俱乐部>")
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)
    if fallback:
        def missing_template(*_args, **_kwargs):
            raise OSError("template not available")
        monkeypatch.setattr(email_service.Path, "read_text", missing_template)

    assert email_service.send_reset_email(
        "member@example.com", "<script>[verify-code]</script>", "ABC123",
    )
    assert len(sent) == 1
    sender, recipients, raw_message = sent[0]
    assert sender == "sender@example.com"
    assert recipients == ["member@example.com"]
    message = message_from_string(raw_message)
    subject = str(make_header(decode_header(message["Subject"])))
    assert subject == "[<俱乐部>] 密码重置验证码"
    html = message.get_payload(0).get_payload(decode=True).decode("utf-8")
    assert "你正在重置账号密码" in html
    assert "30 分钟" in html
    assert "&lt;俱乐部&gt;" in html
    assert "&lt;script&gt;[verify-code]&lt;/script&gt;" in html
    assert "<script>" not in html
    assert "ABC123" in html
