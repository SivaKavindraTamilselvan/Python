import os
import pandas as pd #used for data manipulation library
import numpy as np #used for mathametical opertions

BASE     = os.path.dirname(__file__) #explains the current script
OUT_DIR  = os.path.join(BASE, "data", "raw") #i wanted to create the folder data and subfolder raw inside it
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "raw_data.csv") #add this to the folder

#the reason to crete a raw.data.csv is to protect the original data
#if source file is gone or deleted or modified

def load_raw_data(csv_path: str = "./Mall_Customer.csv") -> pd.DataFrame:
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"  Loaded from file : {csv_path}")
    else:
        raise FileNotFoundError(f"CSV not found at: {csv_path}")
    return df


if __name__ == "__main__":
    print("  MODULE 1 — DATA INGESTION")

    df = load_raw_data(csv_path="./Mall_Customers.csv")
    df.to_csv(OUT_PATH, index=False)
