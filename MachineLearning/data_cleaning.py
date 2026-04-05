import os
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer #if any missing values found automatically using strategy choice like mean,median,mode

BASE     = os.path.dirname(__file__)
IN_PATH  = os.path.join(BASE, "data", "raw", "raw_data.csv")
OUT_DIR  = os.path.join(BASE, "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "cleaned_data.csv")

NUMERIC_COLS     = ["Age", "Annual_Income_(k$)", "Spending_Score"]
CATEGORICAL_COLS = ["Genre"]
TARGET           = "high_spender" #column craeted for output printing


#outliers is a value that is abnormally far from the rest of the data - doesn't fit the pattern
def remove_outliers_iqr(df, cols, factor=3.0):
    before = len(df)
    mask   = pd.Series(True, index=df.index)
    for col in cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr     = q3 - q1 #interquartile range
        mask   &= df[col].between(q1 - factor * iqr, q3 + factor * iqr, inclusive="both") #building the border fence
    cleaned = df[mask].copy()
    print(f"  Outlier removal : {before - len(cleaned)} rows dropped")
    return cleaned

def impute_missing(df):
    before = df[NUMERIC_COLS + CATEGORICAL_COLS].isnull().sum().sum() #first sum count per column and second for all columns

    num_imp = SimpleImputer(strategy="median")
    df[NUMERIC_COLS] = num_imp.fit_transform(df[NUMERIC_COLS])

    #fit_transform initially learns and then apply to them

    cat_imp = SimpleImputer(strategy="most_frequent")
    df[CATEGORICAL_COLS] = cat_imp.fit_transform(df[CATEGORICAL_COLS])

    after = df[NUMERIC_COLS + CATEGORICAL_COLS].isnull().sum().sum()
    print(f"  Imputation  : {before} nulls → {after} nulls")
    return df

def create_target(df, threshold=50):
    df = df.copy()
    #usage of thershold mentioned in README file
    df[TARGET] = (df["Spending_Score"] >= threshold).astype(int)
    print(f"  Target created  : {df[TARGET].mean():.1%} high spenders")
    return df

def clean_data(input_path=IN_PATH):
    df = pd.read_csv(input_path)
    print(f"\n  Input shape  : {df.shape}")

    df = df.dropna(subset=["CustomerID"])
    df = remove_outliers_iqr(df, NUMERIC_COLS)
    df = impute_missing(df)
    df = create_target(df)

    print(f"  Output shape : {df.shape}")
    return df


if __name__ == "__main__":
    print("  MODULE 2 — DATA CLEANING")

    cleaned = clean_data()
    cleaned.to_csv(OUT_PATH, index=False)

    print(f"  Remaining nulls      : {cleaned.isnull().sum().sum()}")
    print(f"  Saved to             : {OUT_PATH}")