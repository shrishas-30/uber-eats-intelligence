# Uber Eats Operational & Customer Intelligence System
# Day 2: Data Preparation and Customer/Restaurant Segmentation

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


# 1. PROJECT SETUP

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
MODEL_DIR = PROJECT_DIR / "models" / "day2"
FIGURE_DIR = PROJECT_DIR / "reports" / "figures"

for folder in [PROCESSED_DIR, MODEL_DIR, FIGURE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


# 2. LOAD DATASETS

customers = pd.read_csv(RAW_DIR / "customers.csv")
restaurants = pd.read_csv(RAW_DIR / "restaurants.csv")
orders = pd.read_csv(RAW_DIR / "orders.csv")
deliveries = pd.read_csv(RAW_DIR / "deliveries.csv")
reviews = pd.read_csv(RAW_DIR / "reviews.csv")

print("DATASETS LOADED SUCCESSFULLY")

for name, df in {
    "Customers": customers,
    "Restaurants": restaurants,
    "Orders": orders,
    "Deliveries": deliveries,
    "Reviews": reviews,
}.items():
    print(f"{name}: {df.shape}")


# Check that required columns exist.

required_columns = {
    "customers": {"customer_id"},
    "restaurants": {
        "restaurant_id",
        "restaurant_name",
        "restaurant_rating",
        "avg_preparation_time",
    },
    "orders": {
        "order_id",
        "customer_id",
        "restaurant_id",
        "order_timestamp",
        "order_amount",
        "order_status",
    },
    "deliveries": {
        "order_id",
        "preparation_time_minutes",
        "delivery_time_minutes",
    },
    "reviews": {
        "customer_id",
        "restaurant_id",
        "review_rating",
    },
}

datasets = {
    "customers": customers,
    "restaurants": restaurants,
    "orders": orders,
    "deliveries": deliveries,
    "reviews": reviews,
}

for name, required in required_columns.items():
    missing = required - set(datasets[name].columns)

    if missing:
        raise ValueError(
            f"{name}.csv is missing required columns: {sorted(missing)}"
        )


# 3. PREPARE ORDER DATA

orders["order_timestamp"] = pd.to_datetime(
    orders["order_timestamp"], errors="coerce"
)

orders["order_amount"] = pd.to_numeric(
    orders["order_amount"], errors="coerce"
)

orders["order_status"] = (
    orders["order_status"].astype("string").str.strip().str.lower()
)

# Completed orders represent successfully fulfilled orders.
completed_orders = orders[
    orders["order_status"] == "completed"
].copy()

# Create time-based features.
orders["order_hour"] = orders["order_timestamp"].dt.hour

orders["is_weekend"] = (
    orders["order_timestamp"].dt.day_of_week >= 5
).astype(int)

# Late-night orders: 10 PM to before 5 AM.
orders["is_late_night"] = (
    (orders["order_hour"] >= 22)
    | (orders["order_hour"] < 5)
).astype(int)


# 4. CUSTOMER FEATURE ENGINEERING

customer_order_features = orders.groupby("customer_id").agg(
    total_orders=("order_id", "nunique"),
    weekend_orders=("is_weekend", "sum"),
    late_night_orders=("is_late_night", "sum"),
    first_order_date=("order_timestamp", "min"),
    last_order_date=("order_timestamp", "max"),
).reset_index()

# Calculate ordering frequency per active month.
active_days = (
    customer_order_features["last_order_date"]
    - customer_order_features["first_order_date"]
).dt.days

active_months = (active_days / 30.44).clip(lower=1)

customer_order_features["ordering_frequency"] = (
    customer_order_features["total_orders"] / active_months
)

# Spending features use completed orders only.
customer_spending = completed_orders.groupby("customer_id").agg(
    total_spending=("order_amount", "sum"),
    average_order_value=("order_amount", "mean"),
).reset_index()

# Average customer rating from submitted reviews.
customer_ratings = reviews.groupby("customer_id").agg(
    average_rating_given=("review_rating", "mean")
).reset_index()

# Keep every customer, including customers without orders.
customer_features = customers[["customer_id"]].copy()

customer_features = customer_features.merge(
    customer_order_features.drop(
        columns=["first_order_date", "last_order_date"]
    ),
    on="customer_id",
    how="left",
)

customer_features = customer_features.merge(
    customer_spending,
    on="customer_id",
    how="left",
)

customer_features = customer_features.merge(
    customer_ratings,
    on="customer_id",
    how="left",
)

customer_feature_columns = [
    "total_orders",
    "average_order_value",
    "total_spending",
    "ordering_frequency",
    "average_rating_given",
    "weekend_orders",
    "late_night_orders",
]

customer_features[customer_feature_columns] = (
    customer_features[customer_feature_columns]
    .replace([np.inf, -np.inf], np.nan)
)

customer_features.to_csv(
    PROCESSED_DIR / "customer_features.csv", index=False
)

print("\nCUSTOMER FEATURES CREATED")
print(customer_features.head())


# 5. RESTAURANT FEATURE ENGINEERING

restaurant_order_features = orders.groupby("restaurant_id").agg(
    total_orders=("order_id", "nunique"),
).reset_index()

# Revenue from completed orders only.
restaurant_revenue = completed_orders.groupby("restaurant_id").agg(
    revenue=("order_amount", "sum")
).reset_index()

# Cancellation rate: cancelled orders divided by all orders.
cancelled_orders = orders.copy()

cancelled_orders["is_cancelled"] = (
    cancelled_orders["order_status"] == "cancelled"
).astype(int)

restaurant_cancellations = cancelled_orders.groupby(
    "restaurant_id"
).agg(
    cancellation_rate=("is_cancelled", "mean")
).reset_index()

# Average preparation and delivery times.
delivery_details = deliveries.merge(
    orders[["order_id", "restaurant_id"]],
    on="order_id",
    how="inner",
)

for col in ["preparation_time_minutes", "delivery_time_minutes"]:
    delivery_details[col] = pd.to_numeric(
        delivery_details[col], errors="coerce"
    )

restaurant_delivery_features = delivery_details.groupby(
    "restaurant_id"
).agg(
    average_preparation_time=(
        "preparation_time_minutes", "mean"
    ),
    average_delivery_time=(
        "delivery_time_minutes", "mean"
    ),
).reset_index()

# Average rating from customer reviews.
restaurant_ratings = reviews.groupby("restaurant_id").agg(
    average_rating=("review_rating", "mean")
).reset_index()

# Use the original restaurant rating if no reviews are available.
restaurant_features = restaurants[
    [
        "restaurant_id",
        "restaurant_name",
        "restaurant_rating",
        "avg_preparation_time",
    ]
].copy()

restaurant_features = restaurant_features.merge(
    restaurant_order_features,
    on="restaurant_id",
    how="left",
)

restaurant_features = restaurant_features.merge(
    restaurant_revenue,
    on="restaurant_id",
    how="left",
)

restaurant_features = restaurant_features.merge(
    restaurant_cancellations,
    on="restaurant_id",
    how="left",
)

restaurant_features = restaurant_features.merge(
    restaurant_delivery_features,
    on="restaurant_id",
    how="left",
)

restaurant_features = restaurant_features.merge(
    restaurant_ratings,
    on="restaurant_id",
    how="left",
)

restaurant_features["average_rating"] = (
    restaurant_features["average_rating"]
    .fillna(restaurant_features["restaurant_rating"])
)

restaurant_features["average_preparation_time"] = (
    restaurant_features["average_preparation_time"]
    .fillna(restaurant_features["avg_preparation_time"])
)

restaurant_feature_columns = [
    "total_orders",
    "revenue",
    "average_rating",
    "average_preparation_time",
    "cancellation_rate",
    "average_delivery_time",
]

restaurant_features[restaurant_feature_columns] = (
    restaurant_features[restaurant_feature_columns]
    .replace([np.inf, -np.inf], np.nan)
)

# Keep identifiers and descriptive names for interpretation.
restaurant_features.drop(
    columns=["restaurant_rating", "avg_preparation_time"],
    inplace=True,
)

restaurant_features.to_csv(
    PROCESSED_DIR / "restaurant_features.csv", index=False
)

print("\nRESTAURANT FEATURES CREATED")
print(restaurant_features.head())


# 6. PREPROCESSING AND STANDARDIZATION

def prepare_features(df, feature_columns, name):
    # Select only numerical analytical features.
    X = df[feature_columns].copy()

    # Handle missing and infinite values.
    X = X.replace([np.inf, -np.inf], np.nan)

    # Remove features that contain no usable information.
    usable_columns = [
        col for col in X.columns
        if X[col].notna().any() and X[col].nunique(dropna=True) > 1
    ]

    if len(usable_columns) < 2:
        raise ValueError(
            f"{name} has fewer than two usable features for clustering."
        )

    removed_columns = sorted(set(X.columns) - set(usable_columns))

    if removed_columns:
        print(f"{name}: excluded constant/empty features: {removed_columns}")

    X = X[usable_columns]

    # Replace missing values with the median.
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)

    # Standardize features to a common scale.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    preprocessor = {
        "feature_columns": usable_columns,
        "imputer": imputer,
        "scaler": scaler,
    }

    joblib.dump(
        preprocessor,
        MODEL_DIR / f"{name}_preprocessor.joblib",
    )

    return X, X_scaled, usable_columns


# Scaling matters because K-Means and DBSCAN use distances.
# Without scaling, high-magnitude features such as spending
# can dominate features such as ratings.


# 7. K-MEANS, ELBOW METHOD AND SILHOUETTE SCORE

def run_kmeans(X_scaled, name, feature_columns):
    row_count = len(X_scaled)

    if row_count < 3:
        raise ValueError(f"Not enough rows to cluster {name}.")

    max_k = min(8, row_count - 1)
    k_values = list(range(2, max_k + 1))

    inertias = []
    silhouette_scores = []

    for k in k_values:
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        labels = model.fit_predict(X_scaled)

        inertias.append(model.inertia_)
        silhouette_scores.append(
            silhouette_score(X_scaled, labels)
        )

    # Save elbow plot.
    plt.figure(figsize=(8, 5))
    plt.plot(k_values, inertias, marker="o")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Inertia")
    plt.title(f"Elbow Method - {name.title()}")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / f"{name}_elbow.png", dpi=150
    )
    plt.close()

    # Save silhouette scores for comparison.
    score_df = pd.DataFrame({
        "k": k_values,
        "inertia": inertias,
        "silhouette_score": silhouette_scores,
    })

    score_df.to_csv(
        PROCESSED_DIR / f"{name}_cluster_evaluation.csv",
        index=False,
    )

    # Choose K with the highest silhouette score.
    best_index = int(np.argmax(silhouette_scores))
    best_k = k_values[best_index]

    final_model = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=10,
    )

    labels = final_model.fit_predict(X_scaled)

    joblib.dump(
        final_model,
        MODEL_DIR / f"{name}_kmeans.joblib",
    )

    print(f"\n{name.upper()} K-MEANS")
    print(f"Selected K: {best_k}")
    print(f"Silhouette score: {silhouette_scores[best_index]:.4f}")

    return final_model, labels, score_df


# 8. DBSCAN DENSITY-BASED CLUSTERING

def run_dbscan(X_scaled, name):
    # Try several epsilon values to find a useful density structure.
    eps_values = [0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0]

    min_samples = max(5, X_scaled.shape[1] * 2)

    best_model = None
    best_labels = None
    best_score = -1
    results = []

    for eps in eps_values:
        model = DBSCAN(
            eps=eps,
            min_samples=min_samples,
        )

        labels = model.fit_predict(X_scaled)

        # -1 represents noise, not a regular cluster.
        valid_mask = labels != -1
        valid_labels = labels[valid_mask]

        cluster_count = len(set(valid_labels))
        noise_count = int((labels == -1).sum())

        score = np.nan

        # Calculate silhouette only when at least two valid
        # clusters exist and enough non-noise samples remain.
        if (
            cluster_count >= 2
            and valid_mask.sum() > cluster_count
        ):
            score = silhouette_score(
                X_scaled[valid_mask],
                valid_labels,
            )

            if score > best_score:
                best_score = score
                best_model = model
                best_labels = labels.copy()

        results.append({
            "eps": eps,
            "min_samples": min_samples,
            "clusters_excluding_noise": cluster_count,
            "noise_points": noise_count,
            "noise_percentage": noise_count / len(labels) * 100,
            "silhouette_score": score,
        })

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        PROCESSED_DIR / f"{name}_dbscan_evaluation.csv",
        index=False,
    )

    # If no tested epsilon gives at least two clusters,
    # retain a baseline model and report its noise count.
    if best_model is None:
        best_model = DBSCAN(
            eps=1.5,
            min_samples=min_samples,
        )
        best_labels = best_model.fit_predict(X_scaled)

        print(
            f"\n{name.upper()}: DBSCAN did not find "
            "two valid non-noise clusters in the tested range."
        )
        print(
            "Inspect the saved DBSCAN evaluation file. "
            "The baseline labels are still saved."
        )
    else:
        print(f"\n{name.upper()} DBSCAN")
        print(f"Selected epsilon: {best_model.eps}")
        print(f"Silhouette score: {best_score:.4f}")

    joblib.dump(
        best_model,
        MODEL_DIR / f"{name}_dbscan.joblib",
    )

    print(f"Noise points: {(best_labels == -1).sum()}")
    print(
        f"Noise percentage: "
        f"{(best_labels == -1).mean() * 100:.2f}%"
    )

    return best_model, best_labels, results_df


# 9. CLUSTER INTERPRETATION AND BUSINESS NAMES

def assign_business_names(profiles, name):
    names = {}

    if name == "customer":
        feature_labels = {
            "total_orders": (
                "Frequent Diners",
                "Occasional Diners",
            ),
            "total_spending": (
                "High-Spending Customers",
                "Budget-Oriented Customers",
            ),
            "average_order_value": (
                "Premium-Value Customers",
                "Low-Value Customers",
            ),
            "ordering_frequency": (
                "Regular Diners",
                "Infrequent Diners",
            ),
            "weekend_orders": (
                "Weekend Diners",
                "Weekday-Oriented Diners",
            ),
            "late_night_orders": (
                "Late-Night Diners",
                "Daytime-Oriented Diners",
            ),
            "average_rating_given": (
                "High-Rating Reviewers",
                "Low-Rating Reviewers",
            ),
        }
    else:
        feature_labels = {
            "total_orders": (
                "High-Volume Restaurants",
                "Low-Volume Restaurants",
            ),
            "revenue": (
                "High-Revenue Restaurants",
                "Low-Revenue Restaurants",
            ),
            "average_rating": (
                "Highly Rated Restaurants",
                "Lower-Rated Restaurants",
            ),
            "average_preparation_time": (
                "Slow-Preparation Restaurants",
                "Fast-Preparation Restaurants",
            ),
            "cancellation_rate": (
                "High-Cancellation Restaurants",
                "Reliable Restaurants",
            ),
            "average_delivery_time": (
                "Long-Delivery-Time Restaurants",
                "Fast-Delivery Restaurants",
            ),
        }

    for cluster_id in profiles.index:
        differences = (
            profiles.loc[cluster_id] - profiles.mean()
        )

        available_features = [
            col for col in feature_labels
            if col in differences.index
            and pd.notna(differences[col])
        ]

        if not available_features:
            names[cluster_id] = f"{name.title()} Cluster {cluster_id}"
            continue

        profile_std = profiles[available_features].std().replace(0, np.nan)

        standardized_difference = (
            differences[available_features] / profile_std
        ).replace([np.inf, -np.inf], np.nan)

        if standardized_difference.isna().all():
            names[cluster_id] = f"{name.title()} Cluster {cluster_id}"
            continue

        key = standardized_difference.abs().idxmax()
        is_above_average = differences[key] > 0

        high_name, low_name = feature_labels[key]

        names[cluster_id] = (
            high_name if is_above_average else low_name
        )

    return names


# 10. PCA VISUALIZATION AND CLUSTER PROFILES

def save_results(
    df,
    X,
    X_scaled,
    feature_columns,
    kmeans_labels,
    dbscan_labels,
    name,
):
    result = df.copy()

    # Save both cluster assignments.
    result["kmeans_cluster"] = kmeans_labels
    result["dbscan_cluster"] = dbscan_labels

    # Generate business names from K-Means cluster profiles.
    profiles = (
        pd.DataFrame(X, columns=feature_columns)
        .assign(kmeans_cluster=kmeans_labels)
        .groupby("kmeans_cluster")[feature_columns]
        .mean()
    )

    cluster_names = assign_business_names(profiles, name)

    result["cluster_name"] = result["kmeans_cluster"].map(
        cluster_names
    )

    result.to_csv(
        PROCESSED_DIR / f"{name}_segmented.csv",
        index=False,
    )

    profiles["cluster_name"] = profiles.index.map(
        cluster_names
    )

    profiles.to_csv(
        PROCESSED_DIR / f"{name}_cluster_profiles.csv"
    )

    print(f"\n{name.upper()} CLUSTER PROFILES")
    print(profiles.to_string())

    # PCA reduces the standardized features to two dimensions.
    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)

    pca_df = pd.DataFrame({
        "PCA1": components[:, 0],
        "PCA2": components[:, 1],
        "cluster": kmeans_labels,
    })

    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=pca_df,
        x="PCA1",
        y="PCA2",
        hue="cluster",
        palette="tab10",
        s=35,
    )

    plt.title(f"PCA Visualization - {name.title()} K-Means")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / f"{name}_pca_kmeans.png",
        dpi=150,
    )
    plt.close()

    # Also visualize DBSCAN clusters and noise.
    pca_df["cluster"] = dbscan_labels

    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=pca_df,
        x="PCA1",
        y="PCA2",
        hue="cluster",
        palette="tab10",
        s=35,
    )

    plt.title(f"PCA Visualization - {name.title()} DBSCAN")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / f"{name}_pca_dbscan.png",
        dpi=150,
    )
    plt.close()

    joblib.dump(
        pca,
        MODEL_DIR / f"{name}_pca.joblib",
    )

    print(f"\nSaved {name} segmentation results.")


# 11. RUN CUSTOMER SEGMENTATION

customer_X, customer_scaled, customer_columns = prepare_features(
    customer_features,
    customer_feature_columns,
    "customer",
)

customer_kmeans, customer_kmeans_labels, customer_scores = (
    run_kmeans(
        customer_scaled,
        "customer",
        customer_columns,
    )
)

customer_dbscan, customer_dbscan_labels, customer_dbscan_scores = (
    run_dbscan(customer_scaled, "customer")
)

save_results(
    customer_features,
    customer_X,
    customer_scaled,
    customer_columns,
    customer_kmeans_labels,
    customer_dbscan_labels,
    "customer",
)


# 12. RUN RESTAURANT SEGMENTATION

restaurant_X, restaurant_scaled, restaurant_columns = prepare_features(
    restaurant_features,
    restaurant_feature_columns,
    "restaurant",
)

restaurant_kmeans, restaurant_kmeans_labels, restaurant_scores = (
    run_kmeans(
        restaurant_scaled,
        "restaurant",
        restaurant_columns,
    )
)

restaurant_dbscan, restaurant_dbscan_labels, restaurant_dbscan_scores = (
    run_dbscan(restaurant_scaled, "restaurant")
)

save_results(
    restaurant_features,
    restaurant_X,
    restaurant_scaled,
    restaurant_columns,
    restaurant_kmeans_labels,
    restaurant_dbscan_labels,
    "restaurant",
)


# 13. FINAL SUMMARY

print("\n" + "=" * 55)
print("DAY 2 SEGMENTATION COMPLETED")
print("=" * 55)

print(f"Processed datasets: {PROCESSED_DIR}")
print(f"Saved models: {MODEL_DIR}")
print(f"Saved visualizations: {FIGURE_DIR}")

print("\nCheck these deliverables:")
print("- customer_features.csv")
print("- restaurant_features.csv")
print("- customer_segmented.csv")
print("- restaurant_segmented.csv")
print("- customer_cluster_profiles.csv")
print("- restaurant_cluster_profiles.csv")
print("- customer_cluster_evaluation.csv")
print("- restaurant_cluster_evaluation.csv")
print("- customer_dbscan_evaluation.csv")
print("- restaurant_dbscan_evaluation.csv")
print("- customer_elbow.png")
print("- restaurant_elbow.png")
print("- customer_pca_kmeans.png")
print("- restaurant_pca_kmeans.png")
print("- customer_pca_dbscan.png")
print("- restaurant_pca_dbscan.png")
