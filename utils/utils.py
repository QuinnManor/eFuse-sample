import os
import git
from pathlib import Path
import pandas as pd


def get_path(x):
    repo_root = Path(git.Repo(os.getcwd(), search_parent_directories=True).git.rev_parse("--show-toplevel"))
    return f"{repo_root}/data/{x}"


def get_monthly_event_count(df):
    df_copy = df.groupby("date", as_index=False).size().copy()
    df_copy["year"] = df_copy["date"].dt.strftime('%Y')
    df_copy["month"] = df_copy["date"].dt.strftime('%b')
    df_copy = df_copy.groupby(["year", "month"], as_index=False).sum().rename(columns={"size":"total_events"})
    return df_copy.set_index("month")


def create_time_series_df(df, sd="2019-01-01", ed="2021-12-31", fill_nans=False):
    date_range = pd.date_range(sd, ed).strftime("%b")
    new_df = pd.DataFrame(index=date_range.unique())
    for year in df.year.unique():
        new_df[f"y_{year}"] = df[df["year"] == year]["total_events"]

    if fill_nans:
        new_df.fillna(method="ffill", inplace=True)
        new_df.fillna(0, inplace=True)
    return new_df


def get_followers(df, user_id):
    return df.query(f"source == '{user_id}'").target.to_list()
