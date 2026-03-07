# Nepal Election 2082 — Claude Code Instructions

## Project Overview

Python script that fetches live Nepal Election 2082 results from the official election commission website and displays:

- **PR (Proportional Representation)** seat allocation using the Sainte-Laguë method
- **FPTP (First Past The Post)** win/lead counts

Single-file project: `app.py`

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Key Configuration (top of `app.py`)

| Constant           | Default | Description                        |
| ------------------ | ------- | ---------------------------------- |
| `TOTAL_SEATS`      | `110`   | Federal PR seats                   |
| `FPTP_TOTAL_SEATS` | `165`   | Total FPTP constituencies          |
| `THRESHOLD`        | `0.03`  | Minimum PR vote share (3%)         |

## Data Sources

- PR votes: `https://result.election.gov.np/PRVoteChartResult2082.aspx`
- FPTP results: `https://result.election.gov.np/FPTPWLChartResult2082.aspx`
- Data fetched via CSRF-protected JSON handler at `/Handlers/SecureJson.ashx`

## Architecture

- `fetch_pr_votes()` — creates session, fetches PR vote data, translates Nepali party names to English
- `fetch_fptp_seats()` — reuses session to fetch FPTP win/lead counts
- `sainte_lague()` — pure seat allocation algorithm (max-heap based)
- `print_results()` / `_build_rows()` — merges PR + FPTP data and renders table

## Notes

- Party names are in Nepali (Unicode); `deep_translator.GoogleTranslator` translates them to English
- stdout is reconfigured to UTF-8 for Unicode output on Windows
- Timestamps are displayed in Nepal Standard Time (UTC+5:45)
