# Uber Eats Operational & Customer Intelligence System

## Project Overview
This project uses synthetic food-delivery data and machine learning to analyze customer behavior, restaurant performance, customer sentiment, delivery operations, and order demand.

The objective is to develop an end-to-end machine learning pipeline that transforms raw data into meaningful business insights and data-driven recommendations.

## Objectives
- Customer and restaurant segmentation using K-Means and DBSCAN.
- Customer feedback and sentiment analysis using NLP.
- Delivery time prediction using regression models.
- Hourly order demand forecasting using ARIMA and Prophet.
- End-to-end ML pipeline development.
- Data-driven business recommendations.

## Technologies
- **Programming Language:** Python
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **Natural Language Processing:** NLTK, TF-IDF
- **Time-Series Forecasting:** Statsmodels (ARIMA), Prophet
- **Data Visualization:** Matplotlib, Seaborn
- **Model Persistence:** Joblib
- **Development Environment:** Jupyter Notebook, VS Code
- **Version Control:** Git, GitHub

## Project Structure
- `data/raw/`: Original synthetic datasets.
- `data/processed/`: Processed datasets generated during analysis.
- `data/processed/cleaned_raw/`: Cleaned copies of the original datasets.
- `notebooks/`: EDA, model development, evaluation, and integration notebooks.
- `src/`: Python scripts for data generation and data cleaning.
- `models/`: Saved machine learning pipelines and models.
- `reports/`: Model evaluation results, forecasts, and business insights.
- `docs/`: Project documentation, including the data dictionary and final presentation.
- `tests/`: Project validation tests.

## Project Status
**Day 1 – Data Generation & Cleaning:** Completed. Generated seven synthetic datasets and implemented a reusable data-cleaning pipeline with validation checks.

- **Day 2 – Data Preparation and Segmentation:** Completed. Performed feature engineering, missing-value treatment, standardization, K-Means clustering, DBSCAN clustering, silhouette evaluation, PCA visualization, and cluster profiling for customers and restaurants.

- **Day 3 – Customer Feedback Analysis Using NLP:** Completed. Preprocessed customer reviews, applied TF-IDF, built and evaluated a Naive Bayes sentiment classifier, compared results with VADER, and identified key sentiment terms and customer complaint themes.

- **Day 4 – Delivery Time Prediction:** Completed. Performed EDA, feature selection, regression modeling, model evaluation, cross-validation, and feature importance analysis to predict delivery times.

- **Day 5 – Hourly Demand Forecasting:** Completed. Analyzed hourly and weekly demand patterns, tested stationarity using the ADF test, built and compared ARIMA and Prophet forecasting models, and generated a 24-hour demand forecast to support operational planning.

- **Day 6 – End-to-End ML Pipeline & Business Insights:** Completed. Integrated customer & restaurant segmentation, sentiment analysis, delivery-time prediction and demand forecasting. Consolidated model comparisons, derived business insights, provided data-backed recommendations and documented model limitations & future improvements.

- **Day 7 – Project Finalization & Presentation:** Completed. Finalized project documentation, data dictionary, business insights report and prepared the final project presentation.

## Conclusion
The Uber Eats Operational & Customer Intelligence System demonstrates how data analytics and machine learning can transform raw food-delivery data into meaningful business insights. Through customer and restaurant segmentation, sentiment analysis, delivery-time prediction, and demand forecasting, the project provides a consolidated understanding of customer behaviour and operational performance.
