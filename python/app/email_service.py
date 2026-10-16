from __future__ import annotations

import smtplib
import re
from html import escape
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from .settings import settings


def send_reset_email(to_email: str, username: str, code: str) -> bool:
    # Optional: if SMTP is not configured, treat as "not available".
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        return False

    # Try to load external template; fall back to inline HTML.
    template_path = Path(__file__).resolve().parent / "email.html"
    try:
        html = template_path.read_text(encoding="utf-8")
    except Exception:
        html = (
            f"<html lang='zh-CN'><body style='font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:20px'>"
            f"<h2 style='color:#2c3e50'>[org_name]</h2>"
            f"<p><b>[username]</b>，你好：</p>"
            f"<p>你正在重置账号密码，请使用以下验证码：</p>"
            f"<div style='background:#f0f0f0;padding:12px 20px;font-size:24px;font-weight:bold;letter-spacing:4px;text-align:center;border-radius:6px;margin:16px 0'>[verify-code]</div>"
            f"<p style='color:#888;font-size:12px'>验证码将在 30 分钟后失效。如果不是你本人操作，请忽略这封邮件。</p>"
            f"</body></html>"
        )
    replacements = {
        "org_name": escape(settings.org_name),
        "username": escape(username),
        "verify-code": escape(code),
    }
    html = re.sub(r"\[(org_name|username|verify-code)\]", lambda match: replacements[match.group(1)], html)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[{settings.org_name}] 密码重置验证码"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_port == 587:
            server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(msg["From"], [to_email], msg.as_string())

    return True
