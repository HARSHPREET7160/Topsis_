<<<<<<< HEAD
# Topsis_
=======
# TOPSIS — Harshpreet (102317160)

This package implements **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)** as required by the assignment:
- CLI program
- Input validation
- CSV output with **Topsis Score** and **Rank**
- Packaged for PyPI

## Installation (from source)
```bash
pip install -U pip
pip install .
```

## CLI Usage (Assignment Part-I)
```bash
python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>
```

Example:
```bash
python topsis.py data.csv "1,1,1,2,1" "+,+,-,+,+" output-result.csv
```

## CLI Usage (after installing as a package)
```bash
topsis-harshpreet-102317160 <InputDataFile> <Weights> <Impacts> <OutputResultFileName>
```

## Input Rules
- CSV must contain **3 or more columns**
- **1st column**: alternatives/labels (can be non-numeric)
- **2nd to last columns**: numeric criteria values
- Weights and Impacts must be comma-separated lists, same length as number of criteria
- Impacts must be `+` (benefit) or `-` (cost)

## Output
Adds:
- `Topsis Score`
- `Rank` (1 = best)

## Build & Upload to PyPI (Part-II)
1. Update `authors.email` in `pyproject.toml`
2. Build:
```bash
python -m pip install build twine
python -m build
```
3. Upload:
```bash
python -m twine upload dist/*
```

## Quick Test
```bash
pip install dist/Topsis_Harshpreet_102317160-1.0.0-py3-none-any.whl
topsis-harshpreet-102317160 data.csv "1,1,1,2,1" "+,+,-,+,+" out.csv
```

## Part-III: Web Service (UI + Email Result)
This repository also includes a web service (`app.py`) that:
- Accepts input CSV, weights, impacts, and email.
- Validates assignment constraints.
- Computes TOPSIS result.
- Sends result CSV as email attachment.

### Run locally
```bash
python -m pip install -r requirements-web.txt
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USERNAME=your-email@gmail.com
set SMTP_PASSWORD=your-app-password
set MAIL_FROM=your-email@gmail.com
set SMTP_USE_TLS=true
python app.py
```
Open `http://127.0.0.1:8000`.

### Deploy on Render (recommended)
1. Push this repo to GitHub.
2. Create a new **Web Service** on Render and select the repo.
3. Configure:
   - Build command: `pip install -r requirements-web.txt`
   - Start command: `gunicorn app:app`
4. Add environment variables in Render:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `MAIL_FROM`
   - `SMTP_USE_TLS=true`
5. Deploy and open the generated Render URL.
>>>>>>> b4df2ae (Add topis package)
