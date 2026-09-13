# 🏠 EstateIQ — AI House Price Predictor

EstateIQ is a machine-learning powered house price prediction web application. It takes key property details such as living area, bedrooms, bathrooms, construction year, quality, garage capacity, basement area, first-floor area, and neighborhood, then predicts an estimated house price.

The project combines a complete machine-learning workflow with an interactive Streamlit web application.

## 🚀 Live Demo

👉 **[Try EstateIQ live](https://estateiq-tech.streamlit.app/)**

---

## ✨ Features

- 🏠 House price prediction from property details
- 🤖 Multiple ML models tested and compared
- 🏆 Best-model selection based on evaluation metrics
- 📊 Model performance displayed inside the app
- 🎨 Modern responsive Streamlit interface
- ✨ Animated network-style background
- 🌙 Dark/light UI theme
- ⚡ Instant predictions from user input
- 💾 Trained model saved with Joblib

---

## 🧠 Machine Learning Workflow

```text
Historical Housing Data
          ↓
    Feature Selection
          ↓
    Train/Test Split
          ↓
   Data Preprocessing
          ↓
     Model Training
          ↓
   Model Comparison
          ↓
      Best Model
          ↓
    Saved .pkl Model
          ↓
     Streamlit App
          ↓
    House Price Estimate
```

---

## 📊 Features Used

The prediction model uses the following nine features:

| Feature | Description |
|---|---|
| `GrLivArea` | Above-ground living area |
| `BedroomAbvGr` | Number of bedrooms |
| `FullBath` | Number of full bathrooms |
| `YearBuilt` | Year the house was built |
| `OverallQual` | Overall material/finish quality |
| `GarageCars` | Garage capacity |
| `TotalBsmtSF` | Total basement area |
| `1stFlrSF` | First-floor area |
| `Neighborhood` | Neighborhood/location category |

### Target

```text
SalePrice
```

The model learns patterns between these property features and the historical sale price.

---

## 🤖 Models Compared

Three regression algorithms were evaluated:

### 1. Linear Regression

A baseline regression model used to establish a simple benchmark.

### 2. Random Forest Regressor

An ensemble of decision trees used to capture more complex relationships between property features and price.

### 3. Gradient Boosting Regressor

A sequential ensemble approach where new trees improve on previous prediction errors.

---

## 🏆 Model Performance

| Model | MAE | R² |
|---|---:|---:|
| Linear Regression | ₹22,335.07 | 0.8297 |
| Random Forest | ₹18,136.72 | 0.8978 |
| **Gradient Boosting** | **₹18,080.30** | **0.9019** |

### Best Model

**Gradient Boosting Regressor**

- **R² Score:** 0.9019
- **Mean Absolute Error:** approximately ₹18,080

The best-performing model is automatically saved as:

```text
house_price_model.pkl
```

---

## 🔤 Handling Categorical Data

`Neighborhood` is a categorical text feature, so it is converted into numerical features using:

```python
OneHotEncoder(handle_unknown="ignore")
```

This allows the regression models to work with location categories while also handling neighborhoods that may not have appeared during training.

---

## 🔄 Train/Test Split

The dataset is split into:

```text
80% → Training data
20% → Testing data
```

The training set is used to learn the relationships between the features and `SalePrice`.

The testing set is used to evaluate how well the trained model performs on unseen data.

---

## 📐 Evaluation Metrics

### Mean Absolute Error (MAE)

MAE measures the average absolute difference between the actual and predicted prices.

```text
Lower MAE = better
```

### R² Score

R² measures how much of the variation in house prices is explained by the model.

```text
Higher R² = better
```

EstateIQ's best model achieved an R² of **0.9019** on the held-out test set.

---

## 🖥️ Tech Stack

- **Python**
- **Pandas**
- **Scikit-learn**
- **Joblib**
- **Streamlit**
- HTML/CSS/JavaScript via Streamlit components for UI effects

---

## 📁 Project Structure

```text
EstateIQ/
│
├── ML_Project/
│   ├── app.py
│   ├── train.py
│   ├── train.csv
│   └── house_price_model.pkl
│
├── requirements.txt
└── README.md
```

### File Description

| File | Purpose |
|---|---|
| `ML_Project/app.py` | Streamlit web application and prediction interface |
| `ML_Project/train.py` | Model training, evaluation, comparison, and model saving |
| `ML_Project/train.csv` | Historical housing dataset |
| `ML_Project/house_price_model.pkl` | Saved best-performing trained model |
| `requirements.txt` | Python dependencies for the deployed application |
| `README.md` | Project documentation |

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd EstateIQ
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the model

```bash
cd ML_Project
python3 train.py
```

This will train and compare the models and create:

```text
house_price_model.pkl
```

### 4. Start the Streamlit app

```bash
python3 -m streamlit run app.py
```

The app will open locally in your browser.

---

## 🌐 Deployment

EstateIQ is deployed as a Streamlit application and is available through the live demo above.

Typical deployment flow:

```text
GitHub Repository
       ↓
Streamlit Cloud
       ↓
Install requirements.txt
       ↓
Run app.py
       ↓
Public EstateIQ URL
```

Make sure the repository contains the files required by the app and that the saved model is available when the app starts.

---

## 🎯 Example Prediction Flow

A user enters:

```text
Living Area       : 1500 sq ft
Bedrooms          : 3
Bathrooms         : 2
Year Built        : 2000
Overall Quality   : 7
Garage            : 2 cars
Basement          : 800 sq ft
1st Floor         : 800 sq ft
Neighborhood      : CollgCr
```

The application sends these values to the saved machine-learning pipeline and returns an estimated house price.

---

## ⚠️ Disclaimer

The predicted price is an estimate generated from patterns learned from historical housing data. It should not be treated as a professional property valuation or guaranteed market price.

---

## 🔮 Future Improvements

Possible next versions could include:

- More extensive feature engineering
- Hyperparameter tuning
- Cross-validation
- Prediction intervals / price ranges
- More detailed neighborhood analysis
- Interactive charts and explainability
- Larger and more recent housing datasets
- Production API backend
- User authentication and saved predictions

---

## 👨‍💻 Project

**EstateIQ — AI House Price Prediction**

Built as an end-to-end machine learning project combining model development, evaluation, model persistence, and an interactive web application.
