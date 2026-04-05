import os
import pandas as pd #used for data manipulation library
import numpy as np #used for mathametical opertions

BASE     = os.path.dirname(__file__) #explains the current script
OUT_DIR  = os.path.join(BASE, "data", "raw") #i wanted to create the folder data and subfolder raw inside it
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "raw_data.csv") #add this to the folder

#the reason to crete a raw.data.csv is to protect the original data
#if source file is gone or deleted or modified

if __name__ == "__main__":
    print("  MODULE 1 — DATA INGESTION")
