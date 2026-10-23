# Uber Eats Operational & Customer Intelligence System
# Day 1: Synthetic Data Generation

from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. PROJECT SETUP
# --------------------------------------------------

# Find the main project folder automatically.
PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
DOCS_DIR = PROJECT_DIR / "docs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Fixed seed makes the generated data reproducible.
rng = np.random.default_rng(42)

# Number of records to generate.
N_CUSTOMERS = 2000
N_RESTAURANTS = 150
N_ORDERS = 10000
N_DRIVERS = 300

# Synthetic order dates covering one calendar year.
START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2026-01-01")


def save_csv(df, filename):
    """Save a DataFrame as a CSV file."""
    path = RAW_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved {filename}: {df.shape}")


# --------------------------------------------------
# 2. GENERATE CUSTOMERS
# --------------------------------------------------

customer_ids = [
    f"CUST{i:04d}" for i in range(1, N_CUSTOMERS + 1)
]

cities = [
    "Bengaluru",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Chennai",
    "Pune",
]

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "age": rng.integers(18, 66, N_CUSTOMERS),
    "city": rng.choice(cities, N_CUSTOMERS),
    "signup_date": (
        START_DATE
        - pd.to_timedelta(
            rng.integers(1, 1000, N_CUSTOMERS), unit="D"
        )
    ),
    "membership_type": rng.choice(
        ["Regular", "Silver", "Gold", "Premium"],
        N_CUSTOMERS,
        p=[0.45, 0.25, 0.20, 0.10],
    ),
})

save_csv(customers, "customers.csv")


# --------------------------------------------------
# 3. GENERATE RESTAURANTS
# --------------------------------------------------

restaurant_ids = [
    f"REST{i:03d}" for i in range(1, N_RESTAURANTS + 1)
]

cuisines = [
    "Indian",
    "Chinese",
    "Italian",
    "Fast Food",
    "Mexican",
    "Desserts",
    "South Indian",
    "Healthy Food",
]

restaurants = pd.DataFrame({
    "restaurant_id": restaurant_ids,
    "restaurant_name": [
        f"Restaurant {i:03d}"
        for i in range(1, N_RESTAURANTS + 1)
    ],
    "city": rng.choice(cities, N_RESTAURANTS),
    "cuisine_type": rng.choice(cuisines, N_RESTAURANTS),
    "restaurant_rating": np.round(
        rng.uniform(2.8, 5.0, N_RESTAURANTS), 2
    ),
    "avg_preparation_time": rng.integers(
        10, 41, N_RESTAURANTS
    ),
})

save_csv(restaurants, "restaurants.csv")


# --------------------------------------------------
# 4. GENERATE DRIVERS
# --------------------------------------------------

driver_ids = [
    f"DRV{i:04d}" for i in range(1, N_DRIVERS + 1)
]

drivers = pd.DataFrame({
    "driver_id": driver_ids,
    "driver_rating": np.round(
        rng.uniform(3.0, 5.0, N_DRIVERS), 2
    ),
    "vehicle_type": rng.choice(
        ["Bike", "Scooter", "Motorcycle", "Bicycle"],
        N_DRIVERS,
        p=[0.15, 0.35, 0.40, 0.10],
    ),
    "experience_months": rng.integers(
        1, 73, N_DRIVERS
    ),
})

save_csv(drivers, "drivers.csv")


# --------------------------------------------------
# 5. GENERATE ORDERS
# --------------------------------------------------

# Random timestamps across the year.
seconds_in_year = int(
    (END_DATE - START_DATE).total_seconds()
)

random_seconds = rng.integers(
    0, seconds_in_year, N_ORDERS
)

order_timestamps = pd.Series(
    START_DATE + pd.to_timedelta(random_seconds, unit="s")
)

# Increase the likelihood of orders around lunch and dinner.
hours = order_timestamps.dt.hour

meal_probability = np.select(
    [
        hours.isin([11, 12, 13, 19, 20, 21]),
        hours.isin([10, 14, 18, 22]),
    ],
    [0.75, 0.40],
    default=0.15,
)

# Resample selected timestamps toward common meal periods.
for i in range(N_ORDERS):
    if rng.random() < meal_probability[i]:
        if rng.random() < 0.45:
            target_hour = int(rng.choice([11, 12, 13]))
        else:
            target_hour = int(rng.choice([19, 20, 21]))

        order_timestamps[i] = (
            order_timestamps[i].normalize()
            + pd.Timedelta(hours=target_hour)
            + pd.Timedelta(
                minutes=int(rng.integers(0, 60)),
                seconds=int(rng.integers(0, 60)),
            )
        )

# Link orders to existing customers and restaurants.
order_customer_ids = rng.choice(customer_ids, N_ORDERS)
order_restaurant_ids = rng.choice(restaurant_ids, N_ORDERS)

# Generate order amounts and item counts.
num_items = rng.integers(1, 9, N_ORDERS)

item_prices = rng.uniform(80, 220, N_ORDERS)

order_amounts = np.round(
    num_items * item_prices, 2
)

# Generate order statuses.
order_statuses = rng.choice(
    ["Completed", "Cancelled", "Diverted"],
    N_ORDERS,
    p=[0.90, 0.07, 0.03],
)

orders = pd.DataFrame({
    "order_id": [
        f"ORD{i:05d}" for i in range(1, N_ORDERS + 1)
    ],
    "customer_id": order_customer_ids,
    "restaurant_id": order_restaurant_ids,
    "order_timestamp": order_timestamps,
    "order_amount": order_amounts,
    "num_items": num_items,
    "order_status": order_statuses,
})

# Keep timestamps in chronological order for convenient analysis.
orders = orders.sort_values(
    "order_timestamp"
).reset_index(drop=True)

save_csv(orders, "orders.csv")


# --------------------------------------------------
# 6. GENERATE DELIVERIES
# --------------------------------------------------

# Only completed orders receive completed delivery records.
completed_orders = orders.loc[
    orders["order_status"] == "Completed"
].copy()

n_deliveries = len(completed_orders)

delivery_distances = np.round(
    rng.gamma(shape=2.0, scale=2.0, size=n_deliveries),
    2,
)

traffic_conditions = rng.choice(
    ["Low", "Medium", "High"],
    n_deliveries,
    p=[0.30, 0.45, 0.25],
)

weather_conditions = rng.choice(
    ["Clear", "Cloudy", "Rainy", "Stormy"],
    n_deliveries,
    p=[0.45, 0.25, 0.25, 0.05],
)

# Look up restaurant preparation times.
restaurant_prep_lookup = restaurants.set_index(
    "restaurant_id"
)["avg_preparation_time"]

preparation_times = (
    completed_orders["restaurant_id"]
    .map(restaurant_prep_lookup)
    .to_numpy()
    + rng.integers(-4, 6, n_deliveries)
)

preparation_times = np.maximum(
    preparation_times, 5
)

traffic_delay = pd.Series(
    traffic_conditions
).map({
    "Low": 0,
    "Medium": 7,
    "High": 18,
}).to_numpy()

weather_delay = pd.Series(
    weather_conditions
).map({
    "Clear": 0,
    "Cloudy": 2,
    "Rainy": 9,
    "Stormy": 18,
}).to_numpy()

# Synthetic delivery duration depends on distance,
# preparation time, traffic, weather, and random noise.
delivery_times = np.rint(
    8
    + delivery_distances * 4.0
    + preparation_times * 0.45
    + traffic_delay
    + weather_delay
    + rng.normal(0, 4, n_deliveries)
)

delivery_times = np.clip(
    delivery_times, 8, 120
).astype(int)

deliveries = pd.DataFrame({
    "delivery_id": [
        f"DEL{i:05d}" for i in range(1, n_deliveries + 1)
    ],
    "order_id": completed_orders["order_id"].to_numpy(),
    "driver_id": rng.choice(driver_ids, n_deliveries),
    "delivery_distance_km": delivery_distances,
    "preparation_time_minutes": preparation_times,
    "delivery_time_minutes": delivery_times,
    "traffic_condition": traffic_conditions,
    "weather_condition": weather_conditions,
})

save_csv(deliveries, "deliveries.csv")


# --------------------------------------------------
# 7. GENERATE PAYMENTS
# --------------------------------------------------

payment_tips = np.where(
    orders["order_status"].to_numpy() == "Completed",
    np.round(
        orders["order_amount"].to_numpy()
        * rng.choice(
            [0.00, 0.05, 0.10, 0.15],
            N_ORDERS,
            p=[0.20, 0.35, 0.35, 0.10],
        ),
        2,
    ),
    0.0,
)

payments = pd.DataFrame({
    "payment_id": [
        f"PAY{i:05d}" for i in range(1, N_ORDERS + 1)
    ],
    "order_id": orders["order_id"].to_numpy(),
    "payment_method": rng.choice(
        ["UPI", "Credit Card", "Debit Card", "Wallet", "Cash"],
        N_ORDERS,
        p=[0.45, 0.20, 0.15, 0.15, 0.05],
    ),
    "payment_status": np.where(
        orders["order_status"].to_numpy() == "Cancelled",
        "Refunded",
        np.where(
            orders["order_status"].to_numpy() == "Diverted",
            "Pending",
            "Successful",
        ),
    ),
    "order_amount": orders["order_amount"].to_numpy(),
    "tip_amount": payment_tips,
})

save_csv(payments, "payments.csv")


# --------------------------------------------------
# 8. GENERATE CUSTOMER REVIEWS
# --------------------------------------------------

# Reviews are generated for a sample of completed orders.
review_candidates = completed_orders.sample(
    frac=0.67, random_state=42
).copy()

review_candidates = review_candidates.reset_index(drop=True)

review_count = len(review_candidates)

review_ratings = rng.choice(
    [1, 2, 3, 4, 5],
    review_count,
    p=[0.08, 0.10, 0.17, 0.30, 0.35],
)

positive_reviews = [
    "The food was delicious and arrived on time.",
    "Great taste and excellent service.",
    "Fresh food and friendly delivery service.",
    "Everything was perfect. I would order again.",
    "Good packaging and a wonderful experience.",
]

negative_reviews = [
    "The delivery was late and the food was cold.",
    "The order took too long to arrive.",
    "The food quality was disappointing.",
    "The packaging was damaged when it arrived.",
    "The order was incorrect and the service was poor.",
]

mixed_reviews = [
    "The food was good, but delivery was slow.",
    "Nice taste, but the packaging could improve.",
    "The restaurant was good, but the order arrived late.",
    "Good food, although the portion was small.",
    "The meal was fine, but the service was average.",
]

review_texts = []

for rating in review_ratings:
    if rating >= 4:
        review_texts.append(
            rng.choice(positive_reviews)
        )
    elif rating <= 2:
        review_texts.append(
            rng.choice(negative_reviews)
        )
    else:
        review_texts.append(
            rng.choice(mixed_reviews)
        )

reviews = pd.DataFrame({
    "review_id": [
        f"REV{i:05d}" for i in range(1, review_count + 1)
    ],
    "order_id": review_candidates["order_id"],
    "customer_id": review_candidates["customer_id"],
    "restaurant_id": review_candidates["restaurant_id"],
    "review_text": review_texts,
    "review_rating": review_ratings,
})

save_csv(reviews, "reviews.csv")


# --------------------------------------------------
# 9. VALIDATE THE DATASETS
# --------------------------------------------------

datasets = {
    "customers": customers,
    "restaurants": restaurants,
    "orders": orders,
    "deliveries": deliveries,
    "drivers": drivers,
    "reviews": reviews,
    "payments": payments,
}

print("\nDATA VALIDATION")
print("-" * 50)

# Check primary-key uniqueness.
primary_keys = {
    "customers": ("customer_id", customers),
    "restaurants": ("restaurant_id", restaurants),
    "orders": ("order_id", orders),
    "deliveries": ("delivery_id", deliveries),
    "drivers": ("driver_id", drivers),
    "reviews": ("review_id", reviews),
    "payments": ("payment_id", payments),
}

for name, (column, df) in primary_keys.items():
    assert df[column].is_unique, (
        f"Duplicate primary keys in {name}"
    )
    print(f"{name}: primary keys are unique")

# Check foreign-key relationships.
assert orders["customer_id"].isin(
    customers["customer_id"]
).all()

assert orders["restaurant_id"].isin(
    restaurants["restaurant_id"]
).all()

assert deliveries["order_id"].isin(
    orders["order_id"]
).all()

assert deliveries["driver_id"].isin(
    drivers["driver_id"]
).all()

assert reviews["order_id"].isin(
    orders["order_id"]
).all()

assert reviews["customer_id"].isin(
    customers["customer_id"]
).all()

assert reviews["restaurant_id"].isin(
    restaurants["restaurant_id"]
).all()

assert payments["order_id"].isin(
    orders["order_id"]
).all()

print("All foreign-key relationships are valid.")

# Check basic numeric constraints.
assert (orders["order_amount"] >= 0).all()
assert (deliveries["delivery_time_minutes"] > 0).all()
assert (deliveries["delivery_distance_km"] > 0).all()
assert payments["tip_amount"].ge(0).all()
assert reviews["review_rating"].between(1, 5).all()

print("Numeric validation passed.")

# Check whether required fields contain missing values.
required_columns = {
    "customers": ["customer_id", "age", "city"],
    "restaurants": ["restaurant_id", "cuisine_type"],
    "orders": [
        "order_id",
        "customer_id",
        "restaurant_id",
        "order_timestamp",
    ],
    "deliveries": ["delivery_id", "order_id", "driver_id"],
    "drivers": ["driver_id"],
    "reviews": ["review_id", "order_id", "review_text"],
    "payments": ["payment_id", "order_id"],
}

for name, columns in required_columns.items():
    assert datasets[name][columns].notna().all().all(), (
        f"Missing values in required columns of {name}"
    )

print("Required-field validation passed.")


# --------------------------------------------------
# 10. GENERATE DATA DICTIONARY
# --------------------------------------------------

data_dictionary = {
    "customers.csv": {
        "customer_id": "Unique customer identifier",
        "age": "Customer age",
        "city": "Customer city",
        "signup_date": "Customer registration date",
        "membership_type": "Customer membership category",
    },
    "restaurants.csv": {
        "restaurant_id": "Unique restaurant identifier",
        "restaurant_name": "Synthetic restaurant name",
        "city": "Restaurant city",
        "cuisine_type": "Restaurant cuisine category",
        "restaurant_rating": "Synthetic restaurant rating",
        "avg_preparation_time": "Typical preparation time in minutes",
    },
    "orders.csv": {
        "order_id": "Unique order identifier",
        "customer_id": "Customer who placed the order",
        "restaurant_id": "Restaurant receiving the order",
        "order_timestamp": "Order placement timestamp",
        "order_amount": "Synthetic order value",
        "num_items": "Number of items in the order",
        "order_status": "Order outcome",
    },
    "deliveries.csv": {
        "delivery_id": "Unique delivery identifier",
        "order_id": "Associated completed order",
        "driver_id": "Assigned driver",
        "delivery_distance_km": "Delivery distance in kilometres",
        "preparation_time_minutes": "Food preparation duration",
        "delivery_time_minutes": "Synthetic delivery duration",
        "traffic_condition": "Traffic category",
        "weather_condition": "Weather category",
    },
    "drivers.csv": {
        "driver_id": "Unique driver identifier",
        "driver_rating": "Synthetic driver rating",
        "vehicle_type": "Driver vehicle category",
        "experience_months": "Driver experience in months",
    },
    "reviews.csv": {
        "review_id": "Unique review identifier",
        "order_id": "Reviewed order",
        "customer_id": "Customer who submitted the review",
        "restaurant_id": "Restaurant associated with the review",
        "review_text": "Synthetic customer feedback",
        "review_rating": "Customer rating from 1 to 5",
    },
    "payments.csv": {
        "payment_id": "Unique payment identifier",
        "order_id": "Associated order",
        "payment_method": "Payment method category",
        "payment_status": "Synthetic payment outcome",
        "order_amount": "Order value recorded for payment",
        "tip_amount": "Synthetic tip amount",
    },
}

dictionary_path = DOCS_DIR / "data_dictionary.md"

with open(dictionary_path, "w", encoding="utf-8") as file:
    file.write("# Uber Eats Synthetic Data Dictionary\n\n")
    file.write(
        "All records are synthetic and generated for learning. "
        "They do not represent actual Uber Eats customers or operations.\n\n"
    )

    for filename, columns in data_dictionary.items():
        file.write(f"## {filename}\n\n")
        file.write("| Column | Description |\n")
        file.write("|---|---|\n")

        for column, description in columns.items():
            file.write(f"| `{column}` | {description} |\n")

        file.write("\n")

print(f"\nData dictionary saved: {dictionary_path}")

print("\nDAY 1 DATA GENERATION COMPLETED SUCCESSFULLY")
print(f"CSV output directory: {RAW_DIR}")