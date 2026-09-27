"""
Strava Fitness Analytics — Data Cleaning Script
Deliverable 2

BEFORE RUNNING: place this script in the same folder as:
  - dailyActivity_merged.csv
  - sleepDay_merged.csv
  - weightLogInfo_merged.csv

Run with: python clean_data.py
Outputs (written to the same folder): daily_clean.csv, sleep_clean.csv, weight_clean.csv
"""

import pandas as pd
from pathlib import Path

# Folder where this script file lives — works regardless of where it's launched from
SCRIPT_DIR = Path(__file__).resolve().parent


def clean_daily_activity(path):
    """Clean dailyActivity_merged.csv: convert date, flag zero-activity days."""
    df = pd.read_csv(path)
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%m/%d/%Y')
    df['is_zero_activity'] = df['TotalSteps'] == 0
    df = df.rename(columns={'ActivityDate': 'Date'})
    return df


def clean_sleep(path):
    """Clean sleepDay_merged.csv: drop duplicates, convert date, strip time."""
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    df['SleepDay'] = pd.to_datetime(df['SleepDay'], format='%m/%d/%Y %I:%M:%S %p').dt.date
    df['SleepDay'] = pd.to_datetime(df['SleepDay'])
    df = df.rename(columns={'SleepDay': 'Date'})
    return df


def clean_weight(path):
    """Clean weightLogInfo_merged.csv: drop Fat column, convert date, strip time."""
    df = pd.read_csv(path)
    df = df.drop(columns=['Fat'])
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p').dt.date
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def main():
    print("Loading and cleaning raw data...")

    daily = clean_daily_activity(SCRIPT_DIR / 'dailyActivity_merged.csv')
    sleep = clean_sleep(SCRIPT_DIR / 'sleepDay_merged.csv')
    weight = clean_weight(SCRIPT_DIR / 'weightLogInfo_merged.csv')

    # Sanity checks — confirm cleaning matches the documented audit
    assert daily['Id'].nunique() == 33, "Expected 33 users in daily"
    assert sleep['Id'].nunique() == 24, "Expected 24 users in sleep"
    assert weight['Id'].nunique() == 8, "Expected 8 users in weight"
    assert 'Fat' not in weight.columns, "Fat column should be dropped"
    assert daily['is_zero_activity'].sum() == 77, "Expected 77 zero-activity rows"
    print("All sanity checks passed.")

    # Save cleaned files next to the script
    daily.to_csv(SCRIPT_DIR / 'daily_clean.csv', index=False)
    sleep.to_csv(SCRIPT_DIR / 'sleep_clean.csv', index=False)
    weight.to_csv(SCRIPT_DIR / 'weight_clean.csv', index=False)

    print("\nSaved: daily_clean.csv, sleep_clean.csv, weight_clean.csv")
    print("Final shapes:", daily.shape, sleep.shape, weight.shape)


if __name__ == "__main__":
    main()