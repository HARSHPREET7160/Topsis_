from __future__ import annotations

import io
import os
import re
import smtplib
import socket
from email.message import EmailMessage

import pandas as pd
from flask import Flask, render_template, request

from topsis_harshpreet_102317160.core import InputError, parse_impacts, parse_weights, topsis


from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class EmailDeliveryError(RuntimeError):
    """Raised when SMTP delivery fails with a user-actionable message."""


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.fullmatch(email.strip()))


def _get_smtp_config() -> dict[str, object]:
    smtp_host = (os.getenv("SMTP_HOST") or "").strip()
    smtp_port_raw = (os.getenv("SMTP_PORT") or "587").strip()
    smtp_username = (os.getenv("SMTP_USERNAME") or "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD") or ""
    smtp_from = (os.getenv("MAIL_FROM") or smtp_username).strip()
    smtp_mode = (os.getenv("SMTP_MODE") or "").strip().lower()
    smtp_timeout_raw = (os.getenv("SMTP_TIMEOUT") or "10").strip()
    if not smtp_mode:
        # Backward compatibility with older config that used SMTP_USE_TLS=true/false.
        use_tls_legacy = (os.getenv("SMTP_USE_TLS") or "true").strip().lower() in {"1", "true", "yes", "on"}
        smtp_mode = "tls" if use_tls_legacy else "plain"

    if smtp_mode not in {"tls", "ssl", "plain"}:
        raise EmailDeliveryError("Invalid SMTP_MODE. Use one of: tls, ssl, plain.")

    missing = []
    if not smtp_host:
        missing.append("SMTP_HOST")
    if not smtp_username:
        missing.append("SMTP_USERNAME")
    if not smtp_password:
        missing.append("SMTP_PASSWORD")
    if not smtp_from:
        missing.append("MAIL_FROM")
    if missing:
        raise EmailDeliveryError(f"Email is not configured. Missing: {', '.join(missing)}")

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError as exc:
        raise EmailDeliveryError("SMTP_PORT must be a valid integer.") from exc
    try:
        smtp_timeout = int(smtp_timeout_raw)
    except ValueError as exc:
        raise EmailDeliveryError("SMTP_TIMEOUT must be a valid integer in seconds.") from exc
    if smtp_timeout < 3:
        raise EmailDeliveryError("SMTP_TIMEOUT must be at least 3 seconds.")

    return {
        "host": smtp_host,
        "port": smtp_port,
        "username": smtp_username,
        "password": smtp_password,
        "from": smtp_from,
        "mode": smtp_mode,
        "timeout": smtp_timeout,
    }


def _send_result_email(recipient: str, csv_bytes: bytes) -> None:
    cfg = _get_smtp_config()
    postmark_stream = (os.getenv("POSTMARK_MESSAGE_STREAM") or "").strip()

    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result CSV"
    msg["From"] = str(cfg["from"])
    msg["To"] = recipient
    if postmark_stream:
        # Postmark uses this header to route to a specific message stream.
        msg["X-PM-Message-Stream"] = postmark_stream
    msg.set_content("Please find the attached TOPSIS result file.")
    msg.add_attachment(csv_bytes, maintype="text", subtype="csv", filename="topsis-result.csv")

    host = str(cfg["host"])
    port = int(cfg["port"])
    username = str(cfg["username"])
    password = str(cfg["password"])
    mode = str(cfg["mode"])
    timeout = int(cfg["timeout"])

    try:
        if mode == "ssl":
            with smtplib.SMTP_SSL(host, port, timeout=timeout) as smtp:
                smtp.login(username, password)
                smtp.send_message(msg)
            return

        with smtplib.SMTP(host, port, timeout=timeout) as smtp:
            if mode == "tls":
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
    except socket.gaierror as exc:
        raise EmailDeliveryError(f"DNS lookup failed for SMTP host '{host}'.") from exc
    except TimeoutError as exc:
        raise EmailDeliveryError(f"Timeout while connecting to SMTP server at {host}:{port}.") from exc
    except OSError as exc:
        raise EmailDeliveryError(
            f"Cannot reach SMTP server at {host}:{port} from this deployment ({exc})."
        ) from exc
    except smtplib.SMTPAuthenticationError as exc:
        raise EmailDeliveryError("SMTP authentication failed. Check username/password or app password.") from exc
    except smtplib.SMTPException as exc:
        raise EmailDeliveryError(f"SMTP error: {exc}") from exc


@app.route("/", methods=["GET", "POST"])
def index():
    status = None
    message = None
    hint = None

    if request.method == "POST":
        try:
            uploaded = request.files.get("input_file")
            weights_raw = (request.form.get("weights") or "").strip()
            impacts_raw = (request.form.get("impacts") or "").strip()
            email_id = (request.form.get("email") or "").strip()

            if uploaded is None or uploaded.filename.strip() == "":
                raise InputError("Please upload an input CSV file.")
            if not uploaded.filename.lower().endswith(".csv"):
                raise InputError("Input file must be a CSV.")
            if not _is_valid_email(email_id):
                raise InputError("Format of email id must be correct.")

            weights = parse_weights(weights_raw)
            impacts = parse_impacts(impacts_raw)

            df = pd.read_csv(uploaded)
            result_df = topsis(df, weights, impacts).dataframe

            csv_stream = io.StringIO()
            result_df.to_csv(csv_stream, index=False)
            csv_bytes = csv_stream.getvalue().encode("utf-8")

            _send_result_email(email_id, csv_bytes)

            status = "success"
            message = f"Result sent successfully to {email_id}."
        except pd.errors.EmptyDataError:
            status = "error"
            message = "Input file is empty or invalid CSV."
        except InputError as exc:
            status = "error"
            message = str(exc)
        except EmailDeliveryError as exc:
            status = "error"
            message = str(exc)
            hint = (
                "Check SMTP_HOST/SMTP_PORT/SMTP_MODE/SMTP_USERNAME/SMTP_PASSWORD/MAIL_FROM. "
                "For SendGrid: SMTP_HOST=smtp.sendgrid.net, SMTP_PORT=587, SMTP_MODE=tls, SMTP_USERNAME=apikey."
            )
        except Exception as exc:
            status = "error"
            message = f"Failed to process request: {exc}"

    return render_template("index.html", status=status, message=message, hint=hint)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
