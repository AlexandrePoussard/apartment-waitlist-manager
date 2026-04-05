# WohnTraum Zürich 🏔️

**Genossenschaft WohnTraum Zürich — Since 1987. Probably your grandchildren will get an apartment.**

A Streamlit web application for managing a fictional Zurich housing cooperative's apartment waitlist.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database

```bash
python seed_data.py
```

This generates 50 applicants, 20 apartments, and 30 applications with realistic Swiss data.

### 3. Run the app

```bash
streamlit run app.py
```

---

## Features

| Page | Description |
|------|-------------|
| **Dashboard** | Metrics, charts, and a bird's-eye view of the cooperative's hopeless situation |
| **Applicants** | Searchable/filterable table, detail view, status updates, quick letter generation |
| **Apartments** | Card grid with Kreis badges, filters, and AI-powered matching (top 5 eligible applicants) |
| **Letter Generator** | Formal rejection and rare approval letters |
| **Add Applicant** | Application form with automatic scoring, rank, and estimated wait time |

## Scoring Algorithm

```
score = (years_on_waitlist × 8)    # max 40 pts (capped at 5 years)
      + (years_in_zurich × 2)       # max 20 pts (capped at 10 years)
      + income_bracket_score         # 10 pts if income < CHF 80k/year
      + family_size_score            # 5 pts/member (max 15 pts)
      + german_score                 # B2=5, C1=8, C2=10 pts
      + zurisack_bonus               # +5 pts if compliant
```

Maximum theoretical score: **100 points**

## Project Structure

```
apartment-waitlist-manager/
├── app.py               # Streamlit entry point (all pages)
├── database.py          # SQLite setup and queries
├── scoring.py           # Applicant scoring logic
├── seed_data.py         # Fake data generator
├── letter_generator.py  # Rejection/approval letter templates
├── requirements.txt
└── README.md
```

## Database

SQLite file stored at `wohntraum.db`. Delete this file and rerun `seed_data.py` to reset.

---

*WohnTraum Zürich AG — Bahnhofstrasse 42, 8001 Zürich — All rejections are final and binding under Swiss Civil Code Art. 271.*
