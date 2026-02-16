# TOPSIS - Harshpreet (102317160)

This repository contains:
- TOPSIS CLI implementation
- Python package (`topsis_harshpreet_102317160`)
- Flask web app (`app.py`) that emails result CSV

## Installation
```bash
pip install -U pip
pip install .
```

## CLI Usage
```bash
python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>
```

Example:
```bash
python topsis.py data.csv "1,1,1,2,1" "+,+,-,+,+" output-result.csv
```

## Web App (Local)
Install dependencies:
```bash
pip install -r requirements.txt
```

Set environment variables (PowerShell):
```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_MODE="tls"
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-16-char-app-password"
$env:MAIL_FROM="your-email@gmail.com"
python app.py
```

Open `http://127.0.0.1:8000`.

## Render Deploy
1. Push repository to GitHub.
2. Create Render Web Service from repo.
3. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Add env vars:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_MODE` (`tls` or `ssl`)
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `MAIL_FROM`

For Gmail, prefer:
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_MODE=tls`
- Use a Gmail App Password (not normal password)
