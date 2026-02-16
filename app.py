from __future__ import annotations

import io
import os
import re
import smtplib
from email.message import EmailMessage

import pandas as pd
from flask import Flask, render_template, request

from topsis_harshpreet_102317160.core import InputError, parse_impacts, parse_weights, topsis


from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.fullmatch(email.strip()))


def _send_result_email(recipient: str, csv_bytes: bytes) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("MAIL_FROM", smtp_username or "")
    use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes", "on"}

    if not smtp_host or not smtp_username or not smtp_password or not smtp_from:
        raise RuntimeError(
            "Email service is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, MAIL_FROM."
        )

    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result CSV"
    msg["From"] = smtp_from
    msg["To"] = recipient
    msg.set_content("Please find the attached TOPSIS result file.")
    msg.add_attachment(csv_bytes, maintype="text", subtype="csv", filename="topsis-result.csv")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def index():
    status = None
    message = None

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
        except Exception as exc:
            status = "error"
            message = f"Failed to process request: {exc}"

    return render_template("index.html", status=status, message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
