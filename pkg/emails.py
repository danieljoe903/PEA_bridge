from flask import current_app
from flask_mail import Message
from pkg.extension import mail


def clean_header(value):
    return (
        str(value or "")
        .replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .strip()
    )

def send_property_expired_email(email, username, property_title):
    safe_email = clean_header(email)
    safe_sender = clean_header(current_app.config["MAIL_DEFAULT_SENDER"])
    safe_username = clean_header(username)
    safe_title = clean_header(property_title)

    msg = Message(
        subject="Your property listing has expired",
        recipients=[safe_email],
        sender=safe_sender
    )

    msg.body = f"""
Hello {safe_username},

Your property listing "{safe_title}" has expired.

Please login to your PEA-Bridge dashboard to activate it again.

Thank you,
PEA-Bridge Team
"""

    msg.html = f"""
    <div style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif;">
      <div style="max-width:620px; margin:30px auto; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb;">
        <div style="background:#0b1320; padding:24px 30px; text-align:center;">
          <h1 style="margin:0; font-size:28px; color:#7acc16; font-weight:700;">PEA-Bridge</h1>
          <p style="margin:8px 0 0; color:#d1d5db; font-size:14px;">Trusted, Reliable and Secure</p>
        </div>

        <div style="padding:32px 30px;">
          <h3 style="margin-bottom:5px;">Hello {safe_username}</h3>
          <h4>Your property listing <strong>{safe_title}</strong> has expired</h4>
          <p>Please login to your PEA-Bridge dashboard to activate it again.</p>
          <strong>Thank you</strong>
        </div>
      </div>
    </div>
    """

    mail.send(msg)

   