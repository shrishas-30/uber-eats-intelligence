# Uber Eats -- Business Insights & Recommendations

## Overview

This document summarizes findings from the synthetic food-delivery
datasets and the completed analysis of customer and restaurant
segmentation, sentiment, delivery-time prediction, and hourly demand
forecasting.

## 1. Customer Segmentation

-   K-Means identified two customer segments with different ordering and
    spending patterns.
-   The higher-activity segment averaged **6.36 completed orders** and
    approximately **₹4,200.29 total spending**, compared with **3.16
    completed orders** and approximately **₹1,948.80** in the
    lower-activity segment.
-   The higher-activity segment also recorded more weekend and
    late-night orders.
-   Customer K-Means silhouette score: **0.237**.

**Business implication:** Use the segments to guide differentiated
retention and re-engagement strategies. The modest silhouette score
means these are broad behavioural groupings, not sharply separated
customer types.

## 2. Restaurant Segmentation

-   The stronger-performing segment averaged **96.96 orders** and
    approximately **₹63,398.02 revenue**.
-   The other segment averaged **84.10 orders** and approximately
    **₹52,998.67 revenue**.
-   The stronger-performing segment had a slightly higher average rating
    (**3.82 vs. 3.67**) and a lower cancellation rate (**8% vs. 11%**).
-   Restaurant K-Means silhouette score: **0.235**.

**Business implication:** Focus restaurant support on order handling,
preparation consistency, ratings, and reducing cancellations. Interpret
the clusters as broad profiles because separation is modest.

## 3. Customer Sentiment Analysis

-   The review dataset contained **5,968 reviews**: 3,426 positive,
    1,360 neutral, and 1,182 negative.
-   Common negative-review themes included food temperature and
    freshness, late delivery, incorrect or missing orders, and service
    or packaging issues.
-   The TF-IDF and Naive Bayes model achieved **100% test accuracy** on
    the synthetic review test split.
-   VADER achieved approximately **74% accuracy** and did not identify
    the Neutral class effectively.

**Business implication:** Prioritize food freshness and temperature,
delivery timeliness, and order accuracy when improving customer
experience.

**Caveat:** The reviews are synthetic and contain repeated text
patterns. The perfect Naive Bayes test score should not be treated as
expected real-world performance. Complaint categories can overlap and
are not mutually exclusive.

## 4. Delivery-Time Prediction

-   Ridge Regression was selected based on the compared test results.
-   Ridge test performance: **MAE 5.437 minutes**, **RMSE 6.739
    minutes**, and **R² 0.794**.
-   Delivery distance had a strong positive relationship with delivery
    time (correlation approximately **0.868**).
-   Random Forest feature-importance analysis also identified delivery
    distance as its strongest feature (importance approximately
    **0.8106**).

**Business implication:** Delivery distance is an important factor for
estimating delivery duration and can inform operational planning and
customer-facing time estimates.

**Future improvement:** Include additional predictors such as traffic,
weather, time of day, and rider availability when reliable data is
available.

## 5. Hourly Demand Forecasting

-   The hourly dataset contained **8,760 observations**.
-   Average demand was approximately **1.14 orders per hour**.
-   Approximately **31.44%** of hourly observations had zero orders.
-   ARIMA(1,1,1) slightly outperformed Prophet on the chronological
    80:20 test split:
    -   ARIMA: MAE **0.798**, RMSE **1.016**, MAPE **30.132%**.
    -   Prophet: MAE **0.800**, RMSE **1.018**, MAPE **30.320%**.
-   The next-24-hour forecast was relatively flat at approximately
    **1.14 orders per hour**, reflecting weak recurring hourly patterns
    in the synthetic data.

**Business implication:** Treat the forecast as a baseline for
short-term planning, not as a precise signal for staffing or inventory
decisions.

## 6. Consolidated Recommendations

1.  **Customer engagement:** Use customer segments to guide
    differentiated retention and re-engagement campaigns.
2.  **Restaurant operations:** Support restaurants in improving order
    handling, preparation consistency, ratings, and cancellation rates.
3.  **Customer experience:** Prioritize food freshness and temperature,
    delivery timeliness, and order accuracy.
4.  **Delivery operations:** Use delivery-time estimates as one planning
    input and expand the model with traffic, weather, and
    rider-availability data.
5.  **Demand planning:** Improve forecasts with longer real-world order
    histories and relevant external factors.

## Conclusion

The project demonstrates an end-to-end workflow for turning
food-delivery data into customer, restaurant, sentiment, delivery, and
demand insights.
