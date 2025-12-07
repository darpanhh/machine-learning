import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import pandas as pd

# -------------------------
# Load model + preprocessors
# -------------------------

def load_model_and_preprocessors():
    # SAFE loading (fixes “pop from empty list”)
    model = tf.keras.models.load_model("model.h5",compile=False)

    with open("label_encoder_gender.pkl", "rb") as f:
        label_encoder_gender = pickle.load(f)

    with open("onehot_encoder_geo.pkl", "rb") as f:
        onehot_encoder_geo = pickle.load(f)

    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    return model, label_encoder_gender, onehot_encoder_geo, scaler


model, label_encoder_gender, onehot_encoder_geo, scaler = load_model_and_preprocessors()

# -------------------------
# Streamlit UI
# -------------------------
st.title("Customer Churn Prediction")
st.write("Provide customer details to predict the likelihood of churn.")

st.sidebar.header("Customer Information")

geography = st.sidebar.selectbox("Geography", onehot_encoder_geo.categories_[0])
gender = st.sidebar.selectbox("Gender", label_encoder_gender.classes_)

age = st.sidebar.slider("Age", 18, 92, 30)
credit_score = st.sidebar.number_input("Credit Score", min_value=300, max_value=850, value=600)
balance = st.sidebar.number_input("Balance", min_value=0, value=50000)
estimated_salary = st.sidebar.number_input("Estimated Salary", min_value=0, value=50000)
tenure = st.sidebar.slider("Tenure (years)", 0, 10, 3)
num_of_products = st.sidebar.slider("Number of Products", 1, 4, 1)
has_cr_card = st.sidebar.selectbox("Has Credit Card", [0, 1])
is_active_member = st.sidebar.selectbox("Is Active Member", [0, 1])

# -------------------------
# Prediction
# -------------------------
if st.button("Predict Churn"):
    # Encode gender safely
    gender_encoded = label_encoder_gender.transform([gender])[0]

    # Base numeric data
    input_data = pd.DataFrame({
        "CreditScore": [credit_score],
        "Gender": [gender_encoded],
        "Age": [age],
        "Tenure": [tenure],
        "Balance": [balance],
        "NumOfProducts": [num_of_products],
        "HasCrCard": [has_cr_card],
        "IsActiveMember": [is_active_member],
        "EstimatedSalary": [estimated_salary],
    })

    # Geo OHE
    geo_encoded = onehot_encoder_geo.transform([[geography]]).toarray()
    geo_encoded_df = pd.DataFrame(
        geo_encoded,
        columns=onehot_encoder_geo.get_feature_names_out(["Geography"])
    )

    # Merge
    input_data = pd.concat([input_data.reset_index(drop=True), geo_encoded_df], axis=1)

    # Scaling
    input_data_scaled = scaler.transform(input_data)

    # Predict
    prediction_proba = float(model.predict(input_data_scaled)[0][0])

    # -------------------------
    # Output results
    # -------------------------
    st.subheader("Prediction Result")
    st.write(f"**Churn Probability:** `{prediction_proba:.2f}`")

    if prediction_proba > 0.5:
        st.error("⚠️ The customer is likely to churn.")
    else:
        st.success("✅ The customer is not likely to churn.")

    st.subheader("Input Data Used")
    st.dataframe(input_data)
