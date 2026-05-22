import streamlit as st
import pandas as pd
import joblib
import os
import mysql.connector

# ==================================
# LOGIN CHECK
# ==================================

if not st.session_state.get("logged_in", False):

    st.switch_page("app.py")

# ==================================
# SIDEBAR
# ==================================

st.sidebar.success(
    f"Welcome {st.session_state.user_name}"
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.user_mobile = ""

    st.switch_page("app.py")

# ==================================
# AUTO TRAIN MODEL
# ==================================

if not os.path.exists("Extra_trees_credit_model.pkl"):

    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import ExtraTreesClassifier

    df = pd.read_csv("german_credit_data.csv")

    df.dropna(inplace=True)

    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    features = [
        "Age",
        "Sex",
        "Job",
        "Housing",
        "Saving accounts",
        "Checking account",
        "Credit amount",
        "Duration"
    ]

    target = "Risk"

    df_model = df[features + [target]].copy()

    cat_cols = [
        "Sex",
        "Housing",
        "Saving accounts",
        "Checking account"
    ]

    for col in cat_cols:

        le = LabelEncoder()

        df_model[col] = le.fit_transform(df_model[col])

        joblib.dump(
            le,
            f"{col}_encoder.pkl"
        )

    target_encoder = LabelEncoder()

    df_model[target] = target_encoder.fit_transform(
        df_model[target]
    )

    X = df_model.drop(target, axis=1)

    y = df_model[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=1
    )

    model = ExtraTreesClassifier(
        n_estimators=200,
        random_state=1
    )

    model.fit(X_train, y_train)

    joblib.dump(
        model,
        "Extra_trees_credit_model.pkl"
    )

# ==================================
# LOAD MODEL
# ==================================

model = joblib.load(
    "Extra_trees_credit_model.pkl"
)

encoders = {
    col: joblib.load(f"{col}_encoder.pkl")
    for col in [
        "Sex",
        "Housing",
        "Saving accounts",
        "Checking account"
    ]
}

# ==================================
# TITLE
# ==================================

st.title("💳 Credit Risk Prediction")

customer_name = st.text_input(
    "Customer Name"
)

customer_mobile = st.text_input(
    "Customer Mobile"
)

col1, col2 = st.columns(2)

with col1:

    age = st.number_input("Age", 18, 80, 30)

    sex = st.selectbox(
        "Sex",
        ["male", "female"]
    )

    job = st.number_input(
        "Job",
        0,
        3,
        1
    )

    housing = st.selectbox(
        "Housing",
        ["own", "rent", "free"]
    )

with col2:

    saving_accounts = st.selectbox(
        "Saving Accounts",
        ["little", "moderate", "rich", "quite rich"]
    )

    checking_account = st.selectbox(
        "Checking Account",
        ["little", "moderate", "rich"]
    )

    credit_amount = st.number_input(
        "Credit Amount",
        0,
        100000,
        1000
    )

    duration = st.number_input(
        "Duration",
        1,
        72,
        12
    )

input_df = pd.DataFrame({

    "Age": [age],

    "Sex": [
        encoders["Sex"].transform([sex])[0]
    ],

    "Job": [job],

    "Housing": [
        encoders["Housing"].transform([housing])[0]
    ],

    "Saving accounts": [
        encoders["Saving accounts"].transform(
            [saving_accounts]
        )[0]
    ],

    "Checking account": [
        encoders["Checking account"].transform(
            [checking_account]
        )[0]
    ],

    "Credit amount": [credit_amount],

    "Duration": [duration]
})

if st.button("Predict Risk"):

    pred = model.predict(input_df)[0]

    prob = model.predict_proba(input_df)[0]

    if pred == 1:

        prediction_label = "GOOD"

        confidence = prob[1] * 100

        st.success("GOOD Credit Risk")

    else:

        prediction_label = "BAD"

        confidence = prob[0] * 100

        st.error("BAD Credit Risk")

    st.metric(
        "Confidence",
        f"{confidence:.2f}%"
    )

    try:

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Root@123",
            database="credit_risk_app"
        )

        cursor = connection.cursor()

        insert_query = """
        INSERT INTO predictions(
            user_email,
            customer_name,
            customer_mobile,
            age,
            sex,
            job,
            housing,
            saving_accounts,
            checking_account,
            credit_amount,
            duration,
            prediction,
            confidence
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(
            insert_query,
            (
                st.session_state.user_email,
                customer_name,
                customer_mobile,
                age,
                sex,
                job,
                housing,
                saving_accounts,
                checking_account,
                credit_amount,
                duration,
                prediction_label,
                confidence
            )
        )

        connection.commit()

        st.success("Prediction Saved")

    except Exception as e:

        st.error(e)

    finally:

        if 'connection' in locals():

            cursor.close()
            connection.close()