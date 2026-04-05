# what is feature engineering ?
# it is the process of creating new columns from existing ones to help the ML model to learn better patterns

import os
import pandas as pd
import numpy as np

BASE     = os.path.dirname(__file__)
IN_PATH  = os.path.join(BASE, "data", "processed", "cleaned_data.csv")
OUT_DIR  = os.path.join(BASE, "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "featured_data.csv")


def add_derived_numerics(df):
    df = df.copy()
    df["income_per_age"]      = (df["Annual_Income_(k$)"] / df["Age"]).round(3)
    df["income_score_ratio"]  = (df["Annual_Income_(k$)"] / (df["Spending_Score"] + 1)).round(3)
    return df


def add_bins(df):
    df = df.copy()
    df["age_group"] = pd.cut(
        df["Age"],
        bins=[0, 25, 45, 100],
        labels=["young", "middle", "senior"]
    ).astype(str)

    df["income_tier"] = pd.cut(
        df["Annual_Income_(k$)"],
        bins=[0, 40, 80, 200],
        labels=["low", "mid", "high"]
    ).astype(str)

    return df


def add_binary_flags(df):
    df = df.copy()
    df["is_young_adult"]  = (df["Age"] <= 30).astype(int)
    df["is_high_earner"]  = (df["Annual_Income_(k$)"] >= 80).astype(int)
    return df


def encode_genre(df):
    df    = df.copy()
    dummies = pd.get_dummies(df["Genre"], prefix="Genre").astype(int)
    df    = pd.concat([df.drop(columns=["Genre"]), dummies], axis=1)
    return df


def engineer_features(input_path=IN_PATH):
    df = pd.read_csv(input_path)
    print(f"\n  Input shape    : {df.shape}")

    df = add_derived_numerics(df)
    df = add_bins(df)
    df = add_binary_flags(df)
    df = encode_genre(df)

    print(f"  Output shape   : {df.shape}")
    return df


if __name__ == "__main__":

    print("  MODULE 3 — FEATURE ENGINEERING")

    featured = engineer_features()

    print("\n  New columns added:")
    new_cols = [
        "income_per_age", "income_score_ratio",
        "age_group", "income_tier",
        "is_young_adult", "is_high_earner",
        "Genre_Male", "Genre_Female"
    ]
    for col in new_cols:
        if col in featured.columns:
            if featured[col].dtype == object:
                print(f"    {col:<25} {featured[col].value_counts().to_dict()}")
            else:
                print(f"    {col:<25} mean={featured[col].mean():.3f}  std={featured[col].std():.3f}")

    featured.to_csv(OUT_PATH, index=False)
    print(f"\n  Saved to       : {OUT_PATH}")
