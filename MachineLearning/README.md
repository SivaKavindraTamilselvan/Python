## TASK5
## Objective
Build an end-to-end ML pipeline that ingests raw data, handles missing values, engineers features, trains multiple models, tunes hyperparameters, and evaluates with cross-validation.
## Requirements
- [x]  `pandas` for data manipulation
- [x]  `numpy` for numerical operations
- [x]  `scikit-learn` (pipelines, transformers, model selection)
- [x]  Feature engineering techniques (binning, one-hot encoding, scaling)
- [x]  Cross-validation and hyperparameter tuning (`GridSearchCV`)
- [x]  Evaluation metrics (accuracy, precision, recall, F1, ROC-AUC)
## STEPS

Creation of data_injestion.py - for collecting the data and store in raw data csv file

Creation of data_cleaning.py - for cleaning the datasets

IQR
1. What is IQR?

IQR (Interquartile Range) is the distance between Q1 and Q3 — it represents the spread of the middle 50% of your data.

IQR = Q3 - Q1

Simply put — IQR tells you how wide the "normal zone" of your data is.

2. What are Quantiles?

A quantile is a cut point that divides sorted data into equal parts.

Q1 → .quantile(0.25) → 25% of data falls below this

Q2 → .quantile(0.50) → 50% of data falls below this (Median)

Q3 → .quantile(0.75) → 75% of data falls below this

3. How Quantiles Are Calculated

Example — Age Column:

Unsorted: 35, 18, 45, 22, 60, 28, 40, 25, 30, 20

Step 1 — Sort:

18, 20, 22, 25, 28, 30, 35, 40, 45, 60

 1   2   3   4   5   6   7   8   9  10

Step 2 — Find Q1 (25% position):

25% of 10 = 2.5th position

= average of 2nd and 3rd value

= (20 + 22) / 2

= 21

Q1 = 21

Step 3 — Find Q3 (75% position):

75% of 10 = 7.5th position

= average of 7th and 8th value

= (35 + 40) / 2

= 37.5

Q3 = 37.5

Step 4 — Calculate IQR:

IQR = Q3 - Q1

    = 37.5 - 21

    = 16.5

4. Visual Split of Data

18, 20, 22, 25, 28, 30, 35, 40, 45, 60

─────────────────────────────────────────

| bottom 25% |    middle 50%   | top 25% |

  18   20      22 25 28 30 35    40 45 60
          
    ↑                ↑

            Q1=21           Q3=37.5

            |←── IQR = 16.5 ──→|

5. What is an Outlier?

An outlier is a value that is abnormally far from the rest of the data.

Common causes:

→ Data entry mistake   : Age entered as 200 instead of 20

→ Measurement error    : Sensor malfunction recording wrong value

→ System glitch        : Software recording -999 for missing values

→ Genuine rare case    : A billionaire in a normal salary dataset

Why outliers are a problem in ML:

Ages: 20, 22, 25, 23, 21, 150  ← outlier

Mean WITH outlier    = 43.5  → model learns wrong patterns

Mean WITHOUT outlier = 22.2  → correct

6. How the Fence is Calculated

Q1 and Q3 alone do not remove anything — they are just reference points used to build a fence.

Lower Fence = Q1 - factor × IQR

Upper Fence = Q3 + factor × IQR

Using our example (factor = 3.0):

Lower Fence = 21   - 3.0 × 16.5 = 21   - 49.5 = -28.5

Upper Fence = 37.5 + 3.0 × 16.5 = 37.5 + 49.5 =  87.0

Anything outside -28.5 and 87 is an OUTLIER

7. Visual Fence Picture

Lower fence        Q1      Q3       Upper fence

      ↓             ↓       ↓             ↓

──────|─────────────|───────|─────────────|────●──

   -28.5  18 20 22  21    37.5  40 45 60  87  200

      ←─────── everything here is KEPT ───────→  ❌

8. Checking Each Value Against the Fence

18  → between -28.5 and 87 → KEEP

20  → between -28.5 and 87 → KEEP

45  → between -28.5 and 87 → KEEP

60  → between -28.5 and 87 → KEEP

200 → NOT between -28.5 and 87 → REMOVE

9. The Code Explained

# Step 1 — Get Q1 and Q3

q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)

# Step 2 — Calculate IQR

iqr = q3 - q1

# Step 3 — Build fence and check each row

mask &= df[col].between(q1 - factor * iqr, q3 + factor * iqr, inclusive="both")

mask          → starts as True for every row (keep all)

.between()    → True if value inside fence, False if outside

&=            → row must pass ALL columns to be kept

inclusive     → boundary values themselves are also kept

10. What is Factor and How is it Chosen?

Factor is not calculated — it is chosen by you based on how strict you want outlier removal to be.

Where 3.0 came from:

Statistics rule → 99.7% of normal data falls within

3 standard deviations from center

→ Anything beyond that 0.3% is extreme → outlier

→ This is where factor 3.0 comes from

Effect of different factor values:

IQR = 16.5, Q3 = 37.5

Factor 1.5 → Upper fence = 37.5 + 1.5 × 16.5 = 62.25 → removes more (aggressive)

Factor 3.0 → Upper fence = 37.5 + 3.0 × 16.5 = 87.00 → removes only extreme ✅

Factor 5.0 → Upper fence = 37.5 + 5.0 × 16.5 = 120.0 → removes almost nothing

Factor 1.5  → Very strict  → Small clean datasets

Factor 2.0  → Strict       → General statistics

Factor 3.0  → Moderate     → ML pipelines (safe default) ✅

Factor 4.0+ → Loose        → Data with wide natural spread

How to pick factor in your own project:

Step 1 → Start with 3.0 (safe default)

Step 2 → Check how many rows are removed

Step 3 → Too many removed   → increase factor

         Outliers still present → decrease factor

Step 4 → Plot data visually and verify

11. Full Summary

Quantile    → Cut point dividing sorted data into equal parts

Q1          → Value at 25% position of sorted data

Q3          → Value at 75% position of sorted data

IQR         → Q3 - Q1 (spread of middle 50% of data)

Lower Fence → Q1 - factor × IQR (bottom removal boundary)

Upper Fence → Q3 + factor × IQR (top removal boundary)

Outlier     → Any value outside the lower or upper fence

Factor      → Controls fence width — you choose this value

12. One Line to Remember

Q1 and Q3 are reference points

→ IQR measures the normal spread

→ Fence = IQR × Factor

→ Anything outside the fence is an outlier and gets removed

Why Threshold is Checked Here

What This Function Does

This function's only job is to create the target column — the label your ML model will predict.
pythondef create_target(df, threshold=50):
threshold=50 means — by default, anyone with Spending Score ≥ 50 is a high spender.

Why Threshold is Needed Here Specifically

Because Spending Score is a number — but your ML model needs a label (0 or 1) to learn from.
Raw data has:
Spending Score = 39, 81, 6, 77, 40, 76

ML model needs:
high_spender   =  0,  1, 0,  1,  0,  1
Threshold is the tool that converts numbers into labels.

Without Threshold — Problem
If you give model raw Spending Scores:

Model sees: 39, 81, 6, 77, 40, 76
Model gets confused:
→ What am I predicting?
→ Is 60 good or bad?
→ Is 49 a high spender or not?
→ No clear boundary to learn from

With Threshold — Solution
threshold = 50

Model sees: 0, 1, 0, 1, 0, 1
Model learns:
→ Score below 50 = 0 = not high spender
→ Score above 50 = 1 = high spender
→ Clear boundary to learn from ✅

Line by Line
pythondf = df.copy()
Works on a copy — original DataFrame outside this function stays unchanged.
pythondf[TARGET] = (df["Spending_Score"] >= threshold).astype(int)
Compares every Spending Score against threshold and creates 0 or 1 label.
pythonprint(f"  Target created : {df[TARGET].mean():.1%} high spenders")
Calculates what percentage are labeled 1:
df[TARGET].mean() calculates average of 0s and 1s

Example:
Labels = 0, 1, 0, 1, 1, 1
Mean   = (0+1+0+1+1+1) / 6 = 4/6 = 0.666

:.1% converts 0.666 to 66.7%

Output → Target created : 66.7% high spenders
This tells you immediately if your split is balanced or not.
pythonreturn df
Returns the DataFrame with the new target column added.

Why Check Balance After Setting Threshold
threshold = 50 result:
→ 45% high spenders    ✅ fairly balanced → good for model

threshold = 90 result:
→ 5% high spenders     ❌ very imbalanced → bad for model

threshold = 10 result:
→ 95% high spenders    ❌ very imbalanced → bad for model
The print statement immediately warns you if your threshold choice creates an imbalanced dataset — so you can adjust it before wasting time training a bad model.

Summary
Threshold is checked here because:

1. Spending Score is a number → model needs 0 or 1
2. Threshold draws the line between 0 and 1
3. print() checks if the split is balanced
4. If imbalanced → change threshold before training

## Screenshots
