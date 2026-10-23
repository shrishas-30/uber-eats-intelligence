# Uber Eats Synthetic Data Dictionary

All records are synthetic and generated for learning. They do not represent actual Uber Eats customers or operations.

## customers.csv

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `age` | Customer age |
| `city` | Customer city |
| `signup_date` | Customer registration date |
| `membership_type` | Customer membership category |

## restaurants.csv

| Column | Description |
|---|---|
| `restaurant_id` | Unique restaurant identifier |
| `restaurant_name` | Synthetic restaurant name |
| `city` | Restaurant city |
| `cuisine_type` | Restaurant cuisine category |
| `restaurant_rating` | Synthetic restaurant rating |
| `avg_preparation_time` | Typical preparation time in minutes |

## orders.csv

| Column | Description |
|---|---|
| `order_id` | Unique order identifier |
| `customer_id` | Customer who placed the order |
| `restaurant_id` | Restaurant receiving the order |
| `order_timestamp` | Order placement timestamp |
| `order_amount` | Synthetic order value |
| `num_items` | Number of items in the order |
| `order_status` | Order outcome |

## deliveries.csv

| Column | Description |
|---|---|
| `delivery_id` | Unique delivery identifier |
| `order_id` | Associated completed order |
| `driver_id` | Assigned driver |
| `delivery_distance_km` | Delivery distance in kilometres |
| `preparation_time_minutes` | Food preparation duration |
| `delivery_time_minutes` | Synthetic delivery duration |
| `traffic_condition` | Traffic category |
| `weather_condition` | Weather category |

## drivers.csv

| Column | Description |
|---|---|
| `driver_id` | Unique driver identifier |
| `driver_rating` | Synthetic driver rating |
| `vehicle_type` | Driver vehicle category |
| `experience_months` | Driver experience in months |

## reviews.csv

| Column | Description |
|---|---|
| `review_id` | Unique review identifier |
| `order_id` | Reviewed order |
| `customer_id` | Customer who submitted the review |
| `restaurant_id` | Restaurant associated with the review |
| `review_text` | Synthetic customer feedback |
| `review_rating` | Customer rating from 1 to 5 |

## payments.csv

| Column | Description |
|---|---|
| `payment_id` | Unique payment identifier |
| `order_id` | Associated order |
| `payment_method` | Payment method category |
| `payment_status` | Synthetic payment outcome |
| `order_amount` | Order value recorded for payment |
| `tip_amount` | Synthetic tip amount |

