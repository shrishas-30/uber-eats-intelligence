# Uber Eats Operational & Customer Intelligence System

## Project Overview
This project uses synthetic food-delivery data and machine learning to analyze customer behavior, restaurant performance, customer sentiment, delivery operations, and order demand.

## Objectives
- Customer and restaurant segmentation using K-Means and DBSCAN.
- Customer feedback and sentiment analysis using NLP.
- Delivery time or tip prediction using regression models.
- Hourly order demand forecasting using ARIMA and Prophet.
- End-to-end ML pipeline development.
- Data-driven business recommendations.

## Technologies
- Python
- Pandas and NumPy
- Scikit-learn
- NLTK
- Statsmodels and Prophet
- Matplotlib and Seaborn
- Git and GitHub

## Project Structure
- `data/raw/`: Synthetic datasets.
- `data/processed/`: Cleaned datasets.
- `notebooks/`: EDA and experiments.
- `src/`: Python scripts.
- `models/`: Saved ML models.
- `reports/`: Reports and visualizations.
- `docs/`: Project documentation.
- `tests/`: Validation tests.

## Project Status
- **Day 1 – Synthetic Data Generation:** Completed. Generated synthetic customer, restaurant, order, delivery, payment, driver, and review datasets with validation checks.

- **Day 2 – Data Preparation and Segmentation:** Completed. Performed feature engineering, missing-value treatment, standardization, K-Means clustering, DBSCAN clustering, silhouette evaluation, PCA visualization, and cluster profiling for customers and restaurants.