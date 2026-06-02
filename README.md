
# Bluestock MF Capstone — Day 1

## Completed Tasks
- Created project folder structure
- Added requirements.txt
- Loaded all 10 datasets using Pandas
- Added dataset exploration script
- Added live NAV fetch script for mfapi.in
- Added AMFI code validation logic
- Added data quality summary report
- Added .gitignore

## Git Commands

```bash
git init
git add .
git commit -m "Day 1: Data ingestion complete"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Run Scripts

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run data ingestion
```bash
python scripts/data_ingestion.py
```

### Fetch live NAV
```bash
python scripts/live_nav_fetch.py
```
