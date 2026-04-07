import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Load
df = pd.read_csv("data/processed/featured_data.csv")
X  = df.drop(columns=["CustomerID", "Spending_Score", "high_spender",
                       "age_group", "income_tier"])  # drop text columns
y  = df["high_spender"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


def evaluate(name, gs):
    y_pred = gs.predict(X_test)
    y_prob = gs.predict_proba(X_test)[:, 1]
    print(f"\n--- {name} ---")
    print(f"  Best Params : { {k.replace('clf__',''):v for k,v in gs.best_params_.items()} }")
    print(f"  Accuracy    : {round(accuracy_score(y_test, y_pred), 4)}")
    print(f"  Precision   : {round(precision_score(y_test, y_pred), 4)}")
    print(f"  Recall      : {round(recall_score(y_test, y_pred), 4)}")
    print(f"  F1          : {round(f1_score(y_test, y_pred), 4)}")
    print(f"  ROC-AUC     : {round(roc_auc_score(y_test, y_prob), 4)}")
    return round(f1_score(y_test, y_pred), 4)


# ── Logistic Regression ──────────────────────────────────────────────
pipe  = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])
gs_lr = GridSearchCV(pipe, {"clf__C": [0.1, 1, 10]}, cv=cv, scoring="f1", n_jobs=-1)
gs_lr.fit(X_train, y_train)
f1_lr = evaluate("Logistic Regression", gs_lr)

# ── Random Forest ────────────────────────────────────────────────────
pipe  = Pipeline([("scaler", StandardScaler()), ("clf", RandomForestClassifier())])
gs_rf = GridSearchCV(pipe, {"clf__n_estimators": [100, 200], "clf__max_depth": [None, 5, 10]}, cv=cv, scoring="f1", n_jobs=-1)
gs_rf.fit(X_train, y_train)
f1_rf = evaluate("Random Forest", gs_rf)

# ── SVM ──────────────────────────────────────────────────────────────
pipe   = Pipeline([("scaler", StandardScaler()), ("clf", SVC(probability=True))])
gs_svm = GridSearchCV(pipe, {"clf__C": [0.1, 1, 10], "clf__kernel": ["rbf", "linear"]}, cv=cv, scoring="f1", n_jobs=-1)
gs_svm.fit(X_train, y_train)
f1_svm = evaluate("SVM", gs_svm)

# ── XGBoost ──────────────────────────────────────────────────────────
try:
    from xgboost import XGBClassifier
    pipe    = Pipeline([("scaler", StandardScaler()), ("clf", XGBClassifier(eval_metric="logloss"))])
    gs_xgb  = GridSearchCV(pipe, {"clf__n_estimators": [100, 200], "clf__max_depth": [3, 6]}, cv=cv, scoring="f1", n_jobs=-1)
    gs_xgb.fit(X_train, y_train)
    f1_xgb  = evaluate("XGBoost", gs_xgb)
except ImportError:
    print("XGBoost not installed — skipping.")
    gs_xgb = None
    f1_xgb = 0

# ── Best Model ───────────────────────────────────────────────────────
all_models = {
    "Logistic Regression": (gs_lr,  f1_lr),
    "Random Forest"      : (gs_rf,  f1_rf),
    "SVM"                : (gs_svm, f1_svm),
    "XGBoost"            : (gs_xgb, f1_xgb),
}

best_name  = max(all_models, key=lambda k: all_models[k][1])
best_model = all_models[best_name][0].best_estimator_

print(f"\nBest Model : {best_name}")
print(f"F1 Score   : {all_models[best_name][1]}")

# Save
joblib.dump(best_model, "best_model.pkl")
print("Model saved : best_model.pkl")