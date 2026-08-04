"""Feature engineering for ML forecasting models."""
import numpy as np
import pandas as pd
from datetime import datetime


def build_time_features(df: pd.DataFrame):
    """Build time-based features from a DataFrame with 'ds' and 'y' columns."""
    df = df.copy()
    df["hour"] = df["ds"].dt.hour
    df["day_of_week"] = df["ds"].dt.dayofweek
    df["month"] = df["ds"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    feature_cols = ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "is_weekend", "month"]
    X = df[feature_cols].values
    y = df["y"].values
    return X, y


def build_time_features_for_dates(dates: list[datetime]) -> np.ndarray:
    """Build feature matrix for a list of datetime objects (for prediction)."""
    rows = []
    for d in dates:
        hour = d.hour
        dow = d.weekday()
        month = d.month
        is_weekend = int(dow >= 5)
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        dow_sin = np.sin(2 * np.pi * dow / 7)
        dow_cos = np.cos(2 * np.pi * dow / 7)
        rows.append([hour_sin, hour_cos, dow_sin, dow_cos, is_weekend, month])
    return np.array(rows)
