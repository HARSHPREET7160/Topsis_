# TOPSIS - Harshpreet (102317160)

This project includes:
- TOPSIS CLI (`topsis.py`)
- Python package (`topsis_harshpreet_102317160`)
- Flask web app (`app.py`) that computes TOPSIS and emails result CSV

## Install
```bash
pip install -r requirements.txt
```

## CLI
```bash
python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>
```

Example:
```bash
python topsis.py data.csv "1,1,1,2,1" "+,+,-,+,+" output-result.csv
```

## Web App (Local)
Set environment variables and run:

```powershell
$env:SMTP_HOST="smtp.sendgrid.net"
$env:SMTP_PORT="2525"
$env:SMTP_MODE="tls"
$env:SMTP_USERNAME="apikey"
$env:SMTP_PASSWORD="<SENDGRID_API_KEY>"
$env:MAIL_FROM="<VERIFIED_SENDER_EMAIL>"
$env:SMTP_TIMEOUT="8"
python app.py
```

Open `http://127.0.0.1:8000`.

## Deploy on Render
1. Push repository to GitHub.
2. Create a Render Web Service from the repo.
3. Set commands:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - --timeout 120`
4. Add environment variables:
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_MODE` (`tls`, `ssl`, or `plain`)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `MAIL_FROM`
- `SMTP_TIMEOUT` (example: `8`)
- `POSTMARK_MESSAGE_STREAM` (optional, only if using Postmark streams)

## Recommended SMTP (SendGrid)
Use this configuration:

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=2525
SMTP_MODE=tls
SMTP_USERNAME=apikey
SMTP_PASSWORD=<SENDGRID_API_KEY>
MAIL_FROM=<VERIFIED_SENDER_EMAIL>
SMTP_TIMEOUT=8
```

Notes:
- `MAIL_FROM` must be a verified sender in your provider.
- Rotate any SMTP/API secret that was exposed in screenshots or chat.
