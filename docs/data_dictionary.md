# Uber Eats Operational & Customer Intelligence System
# Data Dictionary

## 1. Overview

This document describes the seven raw CSV datasets used in the project. Column names, observed data types, row counts, and null/duplicate checks were inspected directly from the supplied CSV files.

All datasets are synthetic and were generated for this capstone project.

## 2. Dataset Summary

| Dataset | Rows | Columns | Description |
|---|---:|---:|---|
| `customers.csv` | 2,000 | 6 | Customer profile and membership information |
| `restaurants.csv` | 100 | 6 | Restaurant profile, category, rating and preparation time |
| `orders.csv` | 10,000 | 8 | Order details, customer/restaurant references and order status |
| `deliveries.csv` | 8,808 | 10 | Delivery assignment, distance, timing, conditions and tip |
| `drivers.csv` | 500 | 5 | Driver profile, rating, vehicle and experience |
| `payments.csv` | 10,000 | 6 | Payment details associated with orders |
| `reviews.csv` | 5,968 | 8 | Customer review text, rating and sentiment label |

## 3. Column Definitions

### 3.1 Customers — `customers.csv`

**Rows:** 2,000  
**Primary key:** `customer_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `customer_id` | Integer (`int64`) | Unique identifier assigned to each customer. | Primary key |
| `age` | Integer (`int64`) | Customer age in years. | |
| `gender` | Text (`object`) | Recorded customer gender category. | |
| `city` | Text (`object`) | Customer's recorded city. | |
| `signup_date` | Text (`object`) | Date on which the customer signed up. Parse as a date for time-based analysis. | |
| `membership_type` | Text (`object`) | Customer membership category, such as Standard or Plus. | |

### 3.2 Restaurants — `restaurants.csv`

**Rows:** 100  
**Primary key:** `restaurant_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `restaurant_id` | Integer (`int64`) | Unique identifier assigned to each restaurant. | Primary key |
| `restaurant_name` | Text (`object`) | Name assigned to the restaurant. | |
| `restaurant_category` | Text (`object`) | Restaurant's food/category classification. | |
| `restaurant_rating` | Decimal (`float64`) | Recorded restaurant rating. | |
| `average_preparation_time` | Decimal (`float64`) | Average food preparation time recorded for the restaurant. | |
| `city` | Text (`object`) | City in which the restaurant is recorded. | |

### 3.3 Orders — `orders.csv`

**Rows:** 10,000  
**Primary key:** `order_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `order_id` | Integer (`int64`) | Unique identifier assigned to each order. | Primary key |
| `customer_id` | Integer (`int64`) | Identifier of the customer who placed the order. | Foreign key → `customers.customer_id` |
| `restaurant_id` | Integer (`int64`) | Identifier of the restaurant receiving the order. | Foreign key → `restaurants.restaurant_id` |
| `order_timestamp` | Text (`object`) | Date and time when the order was placed. Parse as datetime for time-based analysis. | |
| `order_amount` | Decimal (`float64`) | Recorded monetary amount of the order. | |
| `number_of_items` | Integer (`int64`) | Number of items included in the order. | |
| `order_status` | Text (`object`) | Recorded order status, such as Completed or Cancelled. | |
| `payment_method` | Text (`object`) | Payment method recorded for the order. | |

### 3.4 Deliveries — `deliveries.csv`

**Rows:** 8,808  
**Primary key:** `delivery_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `delivery_id` | Integer (`int64`) | Unique identifier assigned to each delivery record. | Primary key |
| `order_id` | Integer (`int64`) | Identifier of the order associated with the delivery. | Foreign key → `orders.order_id` |
| `driver_id` | Integer (`int64`) | Identifier of the driver assigned to the delivery. | Foreign key → `drivers.driver_id` |
| `delivery_distance_km` | Decimal (`float64`) | Delivery distance measured in kilometres. | |
| `delivery_time_minutes` | Decimal (`float64`) | Recorded delivery time in minutes. | |
| `preparation_time_minutes` | Decimal (`float64`) | Recorded order preparation time in minutes. | |
| `traffic_condition` | Text (`object`) | Traffic condition recorded for the delivery. | |
| `weather_condition` | Text (`object`) | Weather condition recorded for the delivery. | |
| `tip_amount` | Decimal (`float64`) | Tip amount recorded for the delivery. | |
| `delivery_status` | Text (`object`) | Recorded delivery status. | |

### 3.5 Drivers — `drivers.csv`

**Rows:** 500  
**Primary key:** `driver_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `driver_id` | Integer (`int64`) | Unique identifier assigned to each driver. | Primary key |
| `driver_rating` | Decimal (`float64`) | Recorded driver rating. | |
| `vehicle_type` | Text (`object`) | Type of vehicle used by the driver. | |
| `experience_years` | Decimal (`float64`) | Driver experience measured in years. | |
| `city` | Text (`object`) | City recorded for the driver. | |

### 3.6 Payments — `payments.csv`

**Rows:** 10,000  
**Primary key:** `payment_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `payment_id` | Integer (`int64`) | Unique identifier assigned to each payment record. | Primary key |
| `order_id` | Integer (`int64`) | Identifier of the order associated with the payment. | Foreign key → `orders.order_id` |
| `payment_method` | Text (`object`) | Payment method used for the transaction. | |
| `payment_amount` | Decimal (`float64`) | Amount recorded for the payment. | |
| `payment_status` | Text (`object`) | Recorded payment status, such as Paid. | |
| `payment_timestamp` | Text (`object`) | Date and time when the payment was recorded. Parse as datetime for time-based analysis. | |

### 3.7 Reviews — `reviews.csv`

**Rows:** 5,968  
**Primary key:** `review_id`

| Column | Observed data type | Description | Key |
|---|---|---|---|
| `review_id` | Integer (`int64`) | Unique identifier assigned to each review. | Primary key |
| `order_id` | Integer (`int64`) | Identifier of the order associated with the review. | Foreign key → `orders.order_id` |
| `customer_id` | Integer (`int64`) | Identifier of the customer who submitted the review. | Foreign key → `customers.customer_id` |
| `restaurant_id` | Integer (`int64`) | Identifier of the restaurant being reviewed. | Foreign key → `restaurants.restaurant_id` |
| `review_text` | Text (`object`) | Written customer feedback. | |
| `rating` | Integer (`int64`) | Numeric rating submitted with the review. | |
| `sentiment_label` | Text (`object`) | Sentiment category recorded in the dataset, such as Positive, Neutral or Negative. | |
| `review_timestamp` | Text (`object`) | Date and time when the review was recorded. Parse as datetime for time-based analysis. | |

## 4. Dataset Relationships

The following relationships are indicated by matching identifier columns:

| Parent dataset | Parent key | Related dataset | Related column | Relationship |
|---|---|---|---|---|
| Customers | `customer_id` | Orders | `customer_id` | One customer can place multiple orders |
| Restaurants | `restaurant_id` | Orders | `restaurant_id` | One restaurant can receive multiple orders |
| Orders | `order_id` | Deliveries | `order_id` | An order may have an associated delivery record |
| Drivers | `driver_id` | Deliveries | `driver_id` | One driver can handle multiple deliveries |
| Orders | `order_id` | Payments | `order_id` | Payment record associated with an order |
| Orders | `order_id` | Reviews | `order_id` | Review associated with an order |
| Customers | `customer_id` | Reviews | `customer_id` | One customer can submit multiple reviews |
| Restaurants | `restaurant_id` | Reviews | `restaurant_id` | One restaurant can receive multiple reviews |

These are logical relationships inferred from the column names and matching identifiers in the supplied files. The CSV files do not themselves enforce database constraints.

## 5. Data Quality Snapshot

The following checks were performed on the supplied raw files:

| Dataset | Missing values | Exact duplicate rows |
|---|---:|---:|
| Customers | 0 | 0 |
| Restaurants | 0 | 0 |
| Orders | 0 | 0 |
| Deliveries | 0 | 0 |
| Drivers | 0 | 0 |
| Payments | 0 | 0 |
| Reviews | 0 | 0 |

All seven files had zero missing values and zero exact duplicate rows at the time of inspection.

Additional observations:

- The `delivery_id`, `order_id`, `customer_id`, `restaurant_id`, `driver_id`, `payment_id` and `review_id` identifier columns were unique within their respective entity tables.
- The deliveries file contains 8,808 records, fewer than the 10,000 orders.
- The reviews file contains 5,968 records, fewer than the 10,000 orders.
- Date/time columns were read by Pandas as text (`object`) and should be converted to datetime before time-based analysis.


## 6. Notes on Data Types

These types reflect how Pandas loads standard CSV files, which do not store formal data types. The date/time columns are currently plain text and should be converted to datetime during data preparation.

## 7. Scope and Limitations

- This dictionary describes the seven raw CSV files only.
- Processed datasets and engineered features are not included in this version.
- All data is synthetic and intended for learning and demonstration.
