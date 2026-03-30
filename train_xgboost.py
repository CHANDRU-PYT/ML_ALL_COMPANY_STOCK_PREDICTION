import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
import joblib

# Load data
df = pd.read_csv('All_Companyreport.csv')

# Preprocessing (same as notebook)
df.drop('S.No', axis=1, inplace=True)

# Fill missing values
df['Price to Earning'] = df['Price to Earning'].fillna(df['Price to Earning'].mean())
df['Current Market price(Rs)'] = df['Current Market price(Rs)'].fillna(df['Current Market price(Rs)'].median())
df['Dividend yield'] = df['Dividend yield'].fillna(df['Dividend yield'].median())
df['Net Profit latest quarter'] = df['Net Profit latest quarter'].fillna(df['Net Profit latest quarter'].median())
df['Sales latest quarter'] = df['Sales latest quarter'].fillna(df['Sales latest quarter'].median())
df['YOY Quarterly profit Growth'] = df['YOY Quarterly profit Growth'].fillna(df['YOY Quarterly profit Growth'].mean())
df['YOY Quarter sales growth'] = df['YOY Quarter sales growth'].fillna(df['YOY Quarter sales growth'].mean())
df['Return on capital employed'] = df['Return on capital employed'].fillna(df['Return on capital employed'].mean())

# Prepare features and target
X = df.drop(['Return on capital employed', 'Name'], axis=1)  # Drop target and Name column
y = df['Return on capital employed']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create XGBoost pipeline (same parameters as notebook)
xg_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    ))
])

# Train model
xg_pipeline.fit(X_train, y_train)

# Evaluate
y_pred = xg_pipeline.predict(X_test)
xg_r2 = r2_score(y_test, y_pred)
xg_mse = mean_squared_error(y_test, y_pred)
xg_rmse = np.sqrt(xg_mse)
xg_mae = mean_absolute_error(y_test, y_pred)

print("XGBoost Model Performance:")
print(f"R² Score: {xg_r2:.4f}")
print(f"MSE: {xg_mse:.4f}")
print(f"RMSE: {xg_rmse:.4f}")
print(f"MAE: {xg_mae:.4f}")

# Load current RandomForest pipeline for comparison
rf_pipeline = joblib.load('pipeline.pkl')
rf_pred = rf_pipeline.predict(X_test)
rf_r2 = r2_score(y_test, rf_pred)
rf_mse = mean_squared_error(y_test, rf_pred)
rf_rmse = np.sqrt(rf_mse)
rf_mae = mean_absolute_error(y_test, rf_pred)

print("\nRandomForest Model Performance:")
print(f"R² Score: {rf_r2:.4f}")
print(f"MSE: {rf_mse:.4f}")
print(f"RMSE: {rf_rmse:.4f}")
print(f"MAE: {rf_mae:.4f}")

# Compare models
print("\nModel Comparison:")
print(f"XGBoost R²: {xg_r2:.4f} vs RandomForest R²: {rf_r2:.4f}")
if xg_r2 > rf_r2:
    print("XGBoost performs better! Saving as new pipeline.")
    joblib.dump(xg_pipeline, 'pipeline_xgboost.pkl')
    # Also update the main pipeline
    joblib.dump(xg_pipeline, 'pipeline.pkl')
    print("Updated pipeline.pkl with XGBoost model.")
else:
    print("RandomForest performs better or equal. Keeping current model.")