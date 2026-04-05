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

if __name__ == "__main__":
    print("  MODULE 2 — DATA CLEANING")