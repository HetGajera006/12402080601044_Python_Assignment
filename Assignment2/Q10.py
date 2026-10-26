import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

GRADE_BINS = [0, 40, 50, 60, 70, 80, 90, 100.0001]
GRADE_LABELS = ["F", "D", "C", "B", "A", "A+"]


def load_and_clean(path):
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    lower = {c.lower(): c for c in df.columns}
    if "enrollment" not in lower or "name" not in lower:
        raise ValueError("CSV must contain 'enrollment' and 'name' columns")
    id_col, name_col = lower["enrollment"], lower["name"]
    subjects = [c for c in df.columns if c not in (id_col, name_col)]
    if not 1 <= len(subjects) <= 20:
        raise ValueError("Number of subjects must be between 1 and 20")

    df = df.dropna(subset=[id_col]).drop_duplicates(subset=[id_col], keep="first").copy()
    df[name_col] = df[name_col].fillna("Unknown").astype(str).str.strip()
    for s in subjects:
        col = pd.to_numeric(df[s], errors="coerce")
        df[s] = col.where((col >= 0) & (col <= 100))
    if df.empty:
        raise ValueError("No valid rows in dataset")
    return df, id_col, name_col, subjects


def build_summary(df, subjects):
    rows = []
    for s in subjects:
        col = df[s]
        rows.append(
            {
                "subject": s,
                "count": int(col.count()),
                "missing": int(col.isna().sum()),
                "mean": round(col.mean(), 2) if col.count() else 0.0,
                "median": round(col.median(), 2) if col.count() else 0.0,
                "min": col.min() if col.count() else 0.0,
                "max": col.max() if col.count() else 0.0,
                "std": round(col.std(), 2) if col.count() > 1 else 0.0,
            }
        )
    return pd.DataFrame(rows)


def fill_missing(df, subjects):
    for s in subjects:
        mean = df[s].mean()
        df[s] = df[s].fillna(round(mean, 2) if pd.notna(mean) else 0.0)
    return df


def save_charts(df, name_col, subjects, out_dir):
    grades = df["Grade"].value_counts().reindex(GRADE_LABELS, fill_value=0)
    plt.figure(figsize=(7, 4))
    plt.bar(grades.index, grades.values, color="#4C78A8")
    plt.title("Grade Distribution")
    plt.xlabel("Grade")
    plt.ylabel("Students")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "grade_distribution.png"), dpi=150)
    plt.close()

    means = df[subjects].mean()
    plt.figure(figsize=(8, 4))
    plt.bar(means.index, means.values, color="#59A14F")
    plt.title("Subject-wise Average")
    plt.xlabel("Subject")
    plt.ylabel("Average marks")
    plt.ylim(0, 100)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "subject_average.png"), dpi=150)
    plt.close()

    top = df.nlargest(10, "Average").iloc[::-1]
    plt.figure(figsize=(8, 5))
    plt.barh(top[name_col].astype(str), top["Average"], color="#F28E2B")
    plt.title("Top Performers")
    plt.xlabel("Average marks")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "top_performers.png"), dpi=150)
    plt.close()


def main():
    path = input("Path of marks CSV: ").strip()
    out_dir = input("Output folder path: ").strip()
    if not os.path.isfile(path):
        print("Error: CSV file not found.")
        sys.exit(1)
    try:
        os.makedirs(out_dir, exist_ok=True)
        df, id_col, name_col, subjects = load_and_clean(path)
    except (ValueError, OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as e:
        print("Error:", e)
        sys.exit(1)

    summary = build_summary(df, subjects)
    df = fill_missing(df, subjects)
    df["Average"] = df[subjects].mean(axis=1).round(2)
    df["Grade"] = pd.cut(df["Average"], bins=GRADE_BINS, labels=GRADE_LABELS, right=False)

    df.to_csv(os.path.join(out_dir, "cleaned_marks.csv"), index=False)
    summary.to_csv(os.path.join(out_dir, "summary.csv"), index=False)
    save_charts(df, name_col, subjects, out_dir)
    print("Saved: cleaned_marks.csv, summary.csv, grade_distribution.png, subject_average.png, top_performers.png")


if __name__ == "__main__":
    main()
