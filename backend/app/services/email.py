import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def _send(to: str, subject: str, html: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, to, msg.as_string())


def send_verification_email(to: str, token: str):
    link = f"{settings.frontend_url}/verify-email?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto">
      <h2>Verify your AIveilix account</h2>
      <p>Click the button below to confirm your email address.</p>
      <a href="{link}" style="display:inline-block;padding:12px 24px;background:#6366f1;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">
        Verify Email
      </a>
      <p style="margin-top:16px;color:#888;font-size:13px">This link expires in 24 hours. If you didn't create an account, ignore this email.</p>
    </div>
    """
    _send(to, "Verify your AIveilix email", html)


def send_password_reset_email(to: str, code: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto">
      <h2>Reset your AIveilix password</h2>
      <p>Use the code below to reset your password. Enter it on the forgot password page.</p>
      <div style="margin:24px 0;text-align:center">
        <span style="display:inline-block;padding:16px 40px;background:#6366f1;color:#fff;border-radius:12px;font-size:32px;font-weight:700;letter-spacing:8px">{code}</span>
      </div>
      <p style="color:#888;font-size:13px">This code expires in 1 hour. If you didn't request a reset, ignore this email.</p>
    </div>
    """
    _send(to, "Your AIveilix password reset code", html)


def send_admin_login_code(to: str, code: str):
    """Custom: one-time 6-digit admin login code, valid for 60 seconds."""
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto">
      <h2>AIveilix admin login code</h2>
      <p>Use this code to enter the admin panel. It expires in <strong>1 minute</strong>.</p>
      <div style="margin:24px 0;text-align:center">
        <span style="display:inline-block;padding:16px 40px;background:#1D4ED8;color:#fff;border-radius:12px;font-size:32px;font-weight:700;letter-spacing:8px">{code}</span>
      </div>
      <p style="color:#888;font-size:13px">Valid for 60 seconds — request a new code if it expires. If this wasn't you, rotate your admin key immediately.</p>
    </div>
    """
    _send(to, "Your AIveilix admin login code", html)


def send_enterprise_inquiry(to: str, data: dict):
    """Notify the sales inbox of a new Enterprise contact request."""
    def esc(v):
        return str(v if v not in (None, "") else "—").replace("<", "&lt;").replace(">", "&gt;")
    rows = "".join(
        f'<tr><td style="padding:6px 12px;color:#888;font-size:13px;text-transform:capitalize">{esc(k).replace("_", " ")}</td>'
        f'<td style="padding:6px 12px;font-size:14px">{esc(v)}</td></tr>'
        for k, v in data.items()
    )
    html = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto">
      <h2>New AIveilix Enterprise inquiry</h2>
      <table style="border-collapse:collapse;width:100%;border:1px solid #eee">{rows}</table>
      <p style="margin-top:16px;color:#888;font-size:13px">Reply directly to the requester to book a call.</p>
    </div>
    """
    _send(to, "New AIveilix Enterprise inquiry", html)


def send_demo_team_invite_email(
    to: str,
    teammate_name: str,
    inviter_name: str,
    company_name: str,
    invite_token: str,
):
    """A teammate was invited into a public demo. They enter directly (no code)."""
    link = f"{settings.frontend_url}/try/invite/{invite_token}"
    safe_company = (company_name or "the demo").replace("<", "&lt;").replace(">", "&gt;")
    safe_inviter = (inviter_name or "A teammate").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;color:#111">
      <h2>You've been invited to try AIveilix</h2>
      <p>Hi {teammate_name},</p>
      <p><strong>{safe_inviter}</strong> invited you to explore an AIveilix demo built on
      <strong>{safe_company}</strong>'s own documents — ask questions, get cited answers, and see how it works.</p>
      <p>Click below to jump straight in. No code needed.</p>
      <div style="margin:24px 0">
        <a href="{link}" style="display:inline-block;padding:12px 28px;background:#6366f1;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">
          Open the demo
        </a>
      </div>
      <p style="color:#888;font-size:13px">This invite expires in 7 days. If you weren't expecting this, you can ignore this email.</p>
    </div>
    """
    _send(to, f"{safe_inviter} invited you to try the AIveilix demo", html)


def send_demo_meeting_admin_email(to: str, data: dict):
    """Notify the founder inbox that a demo visitor asked to talk."""
    def esc(v):
        return str(v if v not in (None, "") else "—").replace("<", "&lt;").replace(">", "&gt;")
    rows = "".join(
        f'<tr><td style="padding:6px 12px;color:#888;font-size:13px;text-transform:capitalize">{esc(k).replace("_", " ")}</td>'
        f'<td style="padding:6px 12px;font-size:14px">{esc(v)}</td></tr>'
        for k, v in data.items()
    )
    html = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto">
      <h2>New "let's talk" request from a demo</h2>
      <table style="border-collapse:collapse;width:100%;border:1px solid #eee">{rows}</table>
      <p style="margin-top:16px;color:#888;font-size:13px">Create a Zoom link and email the visitor directly, then paste it into the admin panel.</p>
    </div>
    """
    _send(to, "New AIveilix demo call request", html)


def send_team_invite_email(
    to: str,
    display_name: str,
    owner_name: str,
    invite_token: str,
    note: str | None = None,
):
    link = f"{settings.frontend_url}/invite/{invite_token}"
    note_html = ""
    if note:
        safe_note = note.replace("<", "&lt;").replace(">", "&gt;")
        note_html = (
            f'<div style="margin:16px 0;padding:12px 16px;background:#f5f5f7;border-left:3px solid #6366f1;border-radius:6px;color:#444;font-size:14px;font-style:italic">'
            f'"{safe_note}"</div>'
        )
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;color:#111">
      <h2>You've been invited to join AIveilix</h2>
      <p>Hi {display_name},</p>
      <p><strong>{owner_name}</strong> has invited you to collaborate on their AIveilix workspace.</p>
      {note_html}
      <p>Click the button below to accept the invitation and set up your account.</p>
      <div style="margin:24px 0">
        <a href="{link}" style="display:inline-block;padding:12px 28px;background:#6366f1;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">
          Accept Invitation
        </a>
      </div>
      <p style="color:#888;font-size:13px">This invitation expires in 7 days. If you weren't expecting this, you can safely ignore this email.</p>
    </div>
    """
    _send(to, f"{owner_name} invited you to AIveilix", html)
