
import os
import pandas as pd
import matplotlib.pyplot as plt


def create_dashboard(input_file, output_folder):
    try:
        # Create output folder if it does not exist.
        os.makedirs(output_folder, exist_ok=True)

        # Read the CSV dataset.
        df = pd.read_csv(input_file)

        required_columns = {"enrollment", "name"}
        if not required_columns.issubset(df.columns):
            print("Error: CSV must contain enrollment and name columns.")
            return

        # Identify subject columns.
        subjects = [
            column for column in df.columns
            if column not in ("enrollment", "name")
        ]

        if not subjects:
            print("Error: No subject columns found.")
            return

        # Convert subject marks to numeric values.
        for subject in subjects:
            df[subject] = pd.to_numeric(df[subject], errors="coerce")

            # Treat marks outside 0-100 as missing.
            df.loc[
                (df[subject] < 0) | (df[subject] > 100),
                subject
            ] = float("nan")

            # Replace missing marks with the subject average.
            average = df[subject].mean()

            if pd.isna(average):
                average = 0

            df[subject] = df[subject].fillna(average)

        # Save cleaned data.
        cleaned_file = os.path.join(
            output_folder, "cleaned_marks.csv"
        )
        df.to_csv(cleaned_file, index=False)

        # Calculate subject-wise statistics.
        summary = pd.DataFrame({
            "Subject": subjects,
            "Average": [df[s].mean() for s in subjects],
            "Minimum": [df[s].min() for s in subjects],
            "Maximum": [df[s].max() for s in subjects]
        })

        summary_file = os.path.join(output_folder, "summary.csv")
        summary.to_csv(summary_file, index=False)

        # Calculate total marks and grade for each student.
        df["Total"] = df[subjects].sum(axis=1)
        df["Average"] = df[subjects].mean(axis=1)

        def get_grade(mark):
            if mark >= 90:
                return "A"
            elif mark >= 80:
                return "B"
            elif mark >= 70:
                return "C"
            elif mark >= 60:
                return "D"
            else:
                return "F"

        df["Grade"] = df["Average"].apply(get_grade)

        # Chart 1: Grade distribution.
        df["Grade"].value_counts().sort_index().plot(
            kind="bar", title="Grade Distribution"
        )
        plt.xlabel("Grade")
        plt.ylabel("Number of Students")
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_folder, "grade_distribution.png")
        )
        plt.close()

        # Chart 2: Subject-wise average marks.
        summary.plot(
            x="Subject", y="Average", kind="bar",
            legend=False, title="Subject-wise Average Marks"
        )
        plt.ylabel("Average Marks")
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_folder, "subject_average.png")
        )
        plt.close()

        # Chart 3: Top 10 performers.
        top_students = df.nlargest(10, "Total")

        plt.figure()
        plt.bar(top_students["name"], top_students["Total"])
        plt.title("Top 10 Performers")
        plt.xlabel("Student")
        plt.ylabel("Total Marks")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_folder, "top_performers.png")
        )
        plt.close()

        print("Dashboard generated successfully!")
        print("Files saved in:", output_folder)
        print("1. cleaned_marks.csv")
        print("2. summary.csv")
        print("3. grade_distribution.png")
        print("4. subject_average.png")
        print("5. top_performers.png")

    except FileNotFoundError:
        print("Error: Input CSV file not found.")
    except (OSError, pd.errors.ParserError, ValueError) as error:
        print("Error:", error)


if __name__ == "__main__":
    input_file = input("Enter marks CSV path: ").strip()
    output_folder = input("Enter output folder path: ").strip()

    create_dashboard(input_file, output_folder)
