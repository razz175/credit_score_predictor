import streamlit as st
import pandas as pd
import mysql.connector

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
# TITLE
# ==================================

st.title("📋 Past Prediction Records")

try:

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@123",
        database="credit_risk_app"
    )

    query = """
    SELECT
        id,
        customer_name,
        customer_mobile,
        age,
        sex,
        credit_amount,
        duration,
        prediction,
        confidence,
        created_at
    FROM predictions
    WHERE user_email=%s
    ORDER BY created_at DESC
    """

    df = pd.read_sql(
        query,
        connection,
        params=(
            st.session_state.user_email,
        )
    )

    if len(df) > 0:

        st.dataframe(
            df,
            use_container_width=True
        )

        st.subheader("Delete Record")

        selected_id = st.selectbox(
            "Select Record ID",
            df["id"]
        )

        if st.button("Delete Selected Record"):

            cursor = connection.cursor()

            delete_query = """
            DELETE FROM predictions
            WHERE id=%s
            """

            cursor.execute(
                delete_query,
                (selected_id,)
            )

            connection.commit()

            st.success("Record Deleted")

            st.rerun()

    else:

        st.info("No records found")

except Exception as e:

    st.error(e)

finally:

    if 'connection' in locals():

        connection.close()