import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score


# ==========================================
# 1. LOAD DATASET
# ==========================================

data = pd.read_csv("train.csv")

print("Dataset loaded successfully!")
print("Dataset shape:", data.shape)


# ==========================================
# 2. SELECT FEATURES
# ==========================================

X = data[[
    "GrLivArea",
    "BedroomAbvGr",
    "FullBath",
    "YearBuilt",
    "OverallQual",
    "GarageCars",
    "TotalBsmtSF",
    "1stFlrSF",
    "Neighborhood"
]]

y = data["SalePrice"]


# ==========================================
# 3. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ==========================================
# 4. ENCODE NEIGHBORHOOD
# ==========================================

categorical_features = ["Neighborhood"]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "neighborhood",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# ==========================================
# 5. CREATE MODELS
# ==========================================

models = {

    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
}


# ==========================================
# 6. TRAIN & COMPARE MODELS
# ==========================================

results = {}

for name, regression_model in models.items():

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regression", regression_model)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    results[name] = {
        "MAE": mae,
        "R2": r2,
        "model": pipeline
    }

    print("\n------------------------------")
    print(name)
    print("------------------------------")
    print("Mean Absolute Error:", round(mae, 2))
    print("R2 Score:", round(r2, 4))


# ==========================================
# 7. FIND BEST MODEL
# ==========================================

best_model_name = max(
    results,
    key=lambda name: results[name]["R2"]
)

best_model = results[best_model_name]["model"]

print("\n================================")
print("BEST MODEL:", best_model_name)
print("================================")


# ==========================================
# 8. SAVE BEST MODEL
# ==========================================

joblib.dump(best_model, "house_price_model.pkl")

print("Best model saved successfully!")


# ==========================================
# 9. TEST SAVED MODEL
# ==========================================

loaded_model = joblib.load("house_price_model.pkl")

sample_house = pd.DataFrame([{
    "GrLivArea": 1500,
    "BedroomAbvGr": 3,
    "FullBath": 2,
    "YearBuilt": 2000,
    "OverallQual": 7,
    "GarageCars": 2,
    "TotalBsmtSF": 800,
    "1stFlrSF": 800,
    "Neighborhood": "CollgCr"
}])

saved_prediction = loaded_model.predict(sample_house)[0]

print("\nNew House Prediction")
print("Predicted Price: ₹", round(saved_prediction))