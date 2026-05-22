import streamlit as st

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

st.title("💰 EMI Calculator")

loan_amount = st.number_input(
    "Loan Amount",
    min_value=1000
)

interest_rate = st.number_input(
    "Interest Rate (%)",
    min_value=1.0
)

years = st.number_input(
    "Loan Tenure (Years)",
    min_value=1
)

if st.button("Calculate EMI"):

    r = interest_rate / (12 * 100)

    n = years * 12

    emi = (
        loan_amount * r * (1+r)**n
    ) / (
        (1+r)**n - 1
    )

    st.success(f"Monthly EMI: ₹ {emi:.2f}")