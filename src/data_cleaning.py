"""
Reusable data-cleaning pipeline for the Uber Eats capstone project.

Usage:
    python src/data_cleaning.py

Input:
    data/raw/*.csv

Output:
    data/processed/cleaned_raw/*.csv
    
"""

from pathlib import Path
import re
import sys

import pandas as pd


# ---------------------------------------------------------------------
# 1. Locate the project and define input/output folders
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "cleaned_raw"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# 2. Dataset configuration
# ---------------------------------------------------------------------

DATASETS = {
    "customers": {
        "required_columns": [
            "customer_id", "age", "gender", "city",
            "signup_date", "membership_type"
        ],
        "primary_key": "customer_id",
        "date_columns": ["signup_date"],
        "numeric_columns": ["customer_id", "age"],
    },
    "restaurants": {
        "required_columns": [
            "restaurant_id", "restaurant_name", "restaurant_category",
            "restaurant_rating", "average_preparation_time", "city"
        ],
        "primary_key": "restaurant_id",
        "date_columns": [],
        "numeric_columns": [
            "restaurant_id", "restaurant_rating",
            "average_preparation_time"
        ],
    },
    "orders": {
        "required_columns": [
            "order_id", "customer_id", "restaurant_id", "order_timestamp",
            "order_amount", "number_of_items", "order_status",
            "payment_method"
        ],
        "primary_key": "order_id",
        "date_columns": ["order_timestamp"],
        "numeric_columns": [
            "order_id", "customer_id", "restaurant_id",
            "order_amount", "number_of_items"
        ],
    },
    "deliveries": {
        "required_columns": [
            "delivery_id", "order_id", "driver_id", "delivery_distance_km",
            "delivery_time_minutes", "preparation_time_minutes",
            "traffic_condition", "weather_condition", "tip_amount",
            "delivery_status"
        ],
        "primary_key": "delivery_id",
        "date_columns": [],
        "numeric_columns": [
            "delivery_id", "order_id", "driver_id",
            "delivery_distance_km", "delivery_time_minutes",
            "preparation_time_minutes", "tip_amount"
        ],
    },
    "drivers": {
        "required_columns": [
            "driver_id", "driver_rating", "vehicle_type",
            "experience_years", "city"
        ],
        "primary_key": "driver_id",
        "date_columns": [],
        "numeric_columns": [
            "driver_id", "driver_rating", "experience_years"
        ],
    },
    "payments": {
        "required_columns": [
            "payment_id", "order_id", "payment_method",
            "payment_amount", "payment_status", "payment_timestamp"
        ],
        "primary_key": "payment_id",
        "date_columns": ["payment_timestamp"],
        "numeric_columns": ["payment_id", "order_id", "payment_amount"],
    },
    "reviews": {
        "required_columns": [
            "review_id", "order_id", "customer_id", "restaurant_id",
            "review_text", "rating", "sentiment_label", "review_timestamp"
        ],
        "primary_key": "review_id",
        "date_columns": ["review_timestamp"],
        "numeric_columns": [
            "review_id", "order_id", "customer_id",
            "restaurant_id", "rating"
        ],
    },
}


# ---------------------------------------------------------------------
# 3. General cleaning and validation functions
# ---------------------------------------------------------------------

def clean_text_columns(df):
    """Trim leading/trailing whitespace in text columns without changing case."""
    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        df[column] = df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    return df


def convert_numeric_columns(df, columns):
    """Convert configured numeric fields; invalid values become missing."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def convert_date_columns(df, columns):
    """Parse configured date/time fields and retain datetime values for CSV export."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    return df


def clean_review_text(text):
    """
    Apply the basic text normalization used in the sentiment notebook.
    Repeated reviews are intentionally retained.
    """
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z\s']", " ", text)
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", text)

    # Keep this basic cleaning independent of optional NLTK downloads.
    return " ".join(tokens)


def validate_primary_key(df, key, dataset_name):
    """Report missing or repeated primary-key values without silently dropping rows."""
    if key not in df.columns:
        print(f"  WARNING: Primary key '{key}' is missing.")
        return

    missing_count = int(df[key].isna().sum())
    duplicate_count = int(df[key].duplicated().sum())

    if missing_count or duplicate_count:
        print(
            f"  WARNING: {dataset_name}.{key}: "
            f"{missing_count} missing values, {duplicate_count} duplicate values."
        )
    else:
        print(f"  Primary key check passed: {key}")


def validate_foreign_keys(cleaned_data):
    """Report unmatched references across the available cleaned datasets."""
    relationships = [
        ("orders", "customer_id", "customers", "customer_id"),
        ("orders", "restaurant_id", "restaurants", "restaurant_id"),
        ("deliveries", "order_id", "orders", "order_id"),
        ("deliveries", "driver_id", "drivers", "driver_id"),
        ("payments", "order_id", "orders", "order_id"),
        ("reviews", "order_id", "orders", "order_id"),
        ("reviews", "customer_id", "customers", "customer_id"),
        ("reviews", "restaurant_id", "restaurants", "restaurant_id"),
    ]

    print("\nForeign-key validation:")
    for child_name, child_col, parent_name, parent_col in relationships:
        if child_name not in cleaned_data or parent_name not in cleaned_data:
            continue

        child = cleaned_data[child_name]
        parent = cleaned_data[parent_name]

        if child_col not in child.columns or parent_col not in parent.columns:
            continue

        parent_values = set(parent[parent_col].dropna())
        child_values = child[child_col].dropna()
        unmatched = int((~child_values.isin(parent_values)).sum())

        print(
            f"  {child_name}.{child_col} -> {parent_name}.{parent_col}: "
            f"{unmatched} unmatched reference(s)"
        )


# ---------------------------------------------------------------------
# 4. Clean each raw dataset
# ---------------------------------------------------------------------

def clean_dataset(dataset_name, config):
    input_path = RAW_DIR / f"{dataset_name}.csv"

    if not input_path.exists():
        print(f"\nSKIPPED: {input_path} was not found.")
        return None

    print(f"\nProcessing {dataset_name}.csv")

    df = pd.read_csv(input_path)
    original_rows = len(df)

    missing_columns = [
        column for column in config["required_columns"]
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name}.csv is missing expected columns: {missing_columns}"
        )

    # Remove only fully identical rows. Do not remove repeated review text.
    exact_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Standardize whitespace in text columns.
    df = clean_text_columns(df)

    # Convert configured numeric and date/time fields.
    df = convert_numeric_columns(df, config["numeric_columns"])
    df = convert_date_columns(df, config["date_columns"])

    # Apply the review text cleaning used by the sentiment workflow.
    if dataset_name == "reviews":
        df["cleaned_review"] = df["review_text"].apply(clean_review_text)

        # Do not remove repeated reviews. Only report empty cleaned text.
        empty_review_count = int(df["cleaned_review"].str.len().eq(0).sum())
        print(f"  Reviews with empty cleaned text: {empty_review_count}")

    # Report data quality; avoid blanket fill/drop operations.
    missing_values = int(df.isna().sum().sum())
    validate_primary_key(df, config["primary_key"], dataset_name)

    output_path = OUTPUT_DIR / f"{dataset_name}_cleaned.csv"
    df.to_csv(output_path, index=False)

    print(f"  Original rows: {original_rows}")
    print(f"  Exact duplicate rows removed: {exact_duplicates}")
    print(f"  Rows after cleaning: {len(df)}")
    print(f"  Missing values after conversion: {missing_values}")
    print(f"  Saved: {output_path.relative_to(PROJECT_ROOT)}")

    return df


# ---------------------------------------------------------------------
# 5. Run the complete pipeline
# ---------------------------------------------------------------------

def main():
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw data folder not found: {RAW_DIR}")

    cleaned_data = {}

    print("Starting Uber Eats data-cleaning pipeline")
    print("Project root:", PROJECT_ROOT)
    print("Raw data folder:", RAW_DIR)
    print("Output folder:", OUTPUT_DIR)

    for dataset_name, config in DATASETS.items():
        cleaned_df = clean_dataset(dataset_name, config)

        if cleaned_df is not None:
            cleaned_data[dataset_name] = cleaned_df

    validate_foreign_keys(cleaned_data)

    print("\nData-cleaning pipeline completed.")
    print(f"Cleaned datasets saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nPipeline failed: {error}")
        sys.exit(1)
