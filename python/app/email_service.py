from __future__ import annotations

import smtplib
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
            f"<html><body style='font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:20px'>"
            f"<h2 style='color:#2c3e50'>{settings.org_name}</h2>"
            f"<p>Dear <b>[username]</b>,</p>"
            f"<p>You have requested to reset your password.</p>"
            f"<p>Your verification code is:</p>"
            f"<div style='background:#f0f0f0;padding:12px 20px;font-size:24px;font-weight:bold;letter-spacing:4px;text-align:center;border-radius:6px;margin:16px 0'>[verify-code]</div>"
            f"<p style='color:#888;font-size:12px'>This code will expire in 30 minutes. If you did not request this, please ignore this email.</p>"
            f"</body></html>"
        )
    html = html.replace("[org_name]", settings.org_name).replace("[username]", username).replace("[verify-code]", code)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[{settings.org_name}] Password Reset Verification Code"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_port == 587:
            server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(msg["From"], [to_email], msg.as_string())

    return True
