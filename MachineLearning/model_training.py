import os
import warnings
import joblib
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)

warnings.filterwarnings("ignore")

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("XGBoost not installed — skipping.")

BASE      = os.path.dirname(__file__)
IN_PATH   = os.path.join(BASE, "data", "processed", "featured_data.csv")
MODEL_DIR = os.path.join(BASE, "models")
RPT_DIR   = os.path.join(BASE, "reports")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RPT_DIR, exist_ok=True)

TARGET    = "high_spender"
DROP_COLS = ["CustomerID", "Spending_Score", TARGET]

NUM_COLS = []
CAT_COLS = []


def build_preprocessor():
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", num_pipe, NUM_COLS),
        ("cat", cat_pipe, CAT_COLS),
    ])


def get_models_and_grids():
    registry = {
        "LogisticRegression": (
            LogisticRegression(max_iter=1000, random_state=42),
            {"clf__C": [0.01, 0.1, 1, 10], "clf__solver": ["lbfgs", "saga"]},
        ),
        "RandomForest": (
            RandomForestClassifier(random_state=42, n_jobs=-1),
            {
                "clf__n_estimators":     [100, 200],
                "clf__max_depth":        [None, 5, 10],
                "clf__min_samples_leaf": [1, 5],
            },
        ),
        "SVM": (
            SVC(probability=True, random_state=42),
            {"clf__C": [0.1, 1, 10], "clf__kernel": ["rbf", "linear"]},
        ),
    }
    if HAS_XGB:
        registry["XGBoost"] = (
            XGBClassifier(eval_metric="logloss", random_state=42, n_jobs=-1),
            {
                "clf__n_estimators":  [100, 200],
                "clf__max_depth":     [3, 6],
                "clf__learning_rate": [0.05, 0.1],
                "clf__subsample":     [0.8, 1.0],
            },
        )
    return registry


def evaluate(estimator, X_test, y_test):
    y_pred = estimator.predict(X_test)
    y_prob = estimator.predict_proba(X_test)[:, 1]
    return {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_prob), 4),
    }


def train(input_path=IN_PATH):
    global NUM_COLS, CAT_COLS

    df = pd.read_csv(input_path)
    X  = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
    y  = df[TARGET]

    NUM_COLS = X.select_dtypes(include="number").columns.tolist()
    CAT_COLS = X.select_dtypes(include=["object", "category"]).columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"\n  Train : {X_train.shape}  |  Test : {X_test.shape}")
    print(f"  Numeric features ({len(NUM_COLS)})    : {NUM_COLS}")
    print(f"  Categorical features ({len(CAT_COLS)}) : {CAT_COLS}")

    cv       = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    registry = get_models_and_grids()
    rows     = {}
    best_pipelines = {}

    print(f"\n  {'MODEL':<22}  {'CV F1':>8}  Best params")
    print("  " + "─" * 65)

    for name, (estimator, param_grid) in registry.items():
        pre  = build_preprocessor()
        pipe = Pipeline([("preprocessor", pre), ("clf", estimator)])

        gs = GridSearchCV(
            pipe, param_grid,
            cv=cv, scoring="f1",
            n_jobs=-1, refit=True,
        )
        gs.fit(X_train, y_train)

        best_pipelines[name] = gs.best_estimator_
        metrics = evaluate(gs.best_estimator_, X_test, y_test)
        metrics["cv_f1"]       = round(gs.best_score_, 4)
        metrics["best_params"] = str({
            k.replace("clf__", ""): v for k, v in gs.best_params_.items()
        })
        rows[name] = metrics

        bp = {k.replace("clf__", ""): v for k, v in gs.best_params_.items()}
        print(f"  {name:<22}  {gs.best_score_:>8.4f}  {bp}")

    results_df = (
        pd.DataFrame(rows).T
        [["cv_f1", "accuracy", "precision", "recall", "f1", "roc_auc", "best_params"]]
        .sort_values("f1", ascending=False)
    )

    best_name  = results_df["f1"].idxmax()
    best_model = best_pipelines[best_name]

    return best_model, best_name, results_df, X_test, y_test


if __name__ == "__main__":
    print("MODULE 4 — MODEL TRAINING & EVALUATION")

    best_model, best_name, results_df, X_test, y_test = train()

    print(f"\nFull results (sorted by F1):")
    print(results_df[["cv_f1", "accuracy", "precision", "recall", "f1", "roc_auc"]].to_string())

    print(f"\nBest model  : {best_name}")
    print(f"Test F1 : {results_df.loc[best_name, 'f1']:.4f}")
    print(f"ROC-AUC : {results_df.loc[best_name, 'roc_auc']:.4f}")

    print(f"\nClassification Report — {best_name}")
    print(classification_report(y_test, best_model.predict(X_test),
                                target_names=["low_spender", "high_spender"]))

    model_path = os.path.join(MODEL_DIR, "best_model.pkl")
    joblib.dump(best_model, model_path)
    print(f"Model saved  : {model_path}")

    rpt_path = os.path.join(RPT_DIR, "training_results.csv")
    results_df.to_csv(rpt_path)
    print(f"Report saved : {rpt_path}")