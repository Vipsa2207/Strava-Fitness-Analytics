# Strava Insights Hub

A fitness analytics case study built on the public FitBit Fitness Tracker dataset (33 users, April–May 2016), used as a proxy for Strava-style user behavior. The project cleans three daily datasets, explores them, merges them, and presents the results in an interactive Streamlit app.

## What's in this repo

| File | What it is |
|---|---|
| `Strava_Fitness_Analytics.ipynb` | Full analysis notebook: problem statement, cleaning, 13 EDA charts with insights, key findings, recommendations, and a heart-rate stretch analysis |
| `clean_data.py` | Standalone script that reads the 3 raw CSVs and writes the cleaned versions |
| `app.py` | Streamlit app with four tabs: Dashboard, SQL Analytics Playground, User Explorer, Leaderboard & Badges |
| `dailyActivity_merged.csv`, `sleepDay_merged.csv`, `weightLogInfo_merged.csv` | Raw datasets |
| `daily_clean.csv`, `sleep_clean.csv`, `weight_clean.csv`, `master_clean.csv` | Cleaned datasets and the merged master table |
| `.streamlit/config.toml` | App theme settings |

## How to run the app

```
pip install streamlit pandas matplotlib seaborn
streamlit run app.py
```

Run it from the repo folder so the app can find the CSV files and `strava_logo.png`.

## Sample size note

Activity data covers 33 users, sleep data covers 24, and weight data covers only 8. The heart-rate stretch analysis covers 14 users. Findings involving weight, BMI, or heart rate describe those specific users and should not be generalized.

## Data source

FitBit Fitness Tracker Data (public dataset). This project is not affiliated with Strava or Fitbit.