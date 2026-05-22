import streamlit as st
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="Credit Risk App",
    page_icon="🔐",
    layout="centered"
)

# ==================================
# MYSQL CONFIG
# ==================================

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Root@123"
DB_NAME = "credit_risk_app"

# ==================================
# DATABASE CREATION
# ==================================

def create_database():

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = connection.cursor()

    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
    )

    connection.database = DB_NAME

    user_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        mobile VARCHAR(20),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255)
    )
    """

    prediction_table = """
    CREATE TABLE IF NOT EXISTS predictions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_email VARCHAR(255),
        customer_name VARCHAR(255),
        customer_mobile VARCHAR(20),
        age INT,
        sex VARCHAR(20),
        job INT,
        housing VARCHAR(50),
        saving_accounts VARCHAR(50),
        checking_account VARCHAR(50),
        credit_amount INT,
        duration INT,
        prediction VARCHAR(20),
        confidence FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(user_table)
    cursor.execute(prediction_table)

    cursor.close()
    connection.close()

create_database()

# ==================================
# CONNECTION
# ==================================

def get_connection():

    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# ==================================
# SESSION STATE
# ==================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_mobile" not in st.session_state:
    st.session_state.user_mobile = ""

# ==================================
# LOGOUT FUNCTION
# ==================================

def logout():

    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.user_mobile = ""

    st.switch_page("app.py")

# ==================================
# HIDE SIDEBAR BEFORE LOGIN
# ==================================

if not st.session_state.logged_in:

    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display:none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================================
# SIDEBAR AFTER LOGIN
# ==================================

if st.session_state.logged_in:

    st.sidebar.success(
        f"Welcome {st.session_state.user_name}"
    )

    if st.sidebar.button("Logout"):
        logout()

# ==================================
# LOGIN/SIGNUP PAGE
# ==================================

if not st.session_state.logged_in:

    st.title("🔐 Credit Risk Authentication")

    menu = st.radio(
        "Select Option",
        ["Login", "Signup"]
    )

    # ==================================
    # SIGNUP
    # ==================================

    if menu == "Signup":

        st.subheader("Create Account")

        first_name = st.text_input("First Name")

        last_name = st.text_input("Last Name")

        mobile = st.text_input("Mobile")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Signup"):

            if password != confirm_password:

                st.error("Passwords do not match")

            else:

                try:

                    connection = get_connection()

                    cursor = connection.cursor()

                    query = """
                    SELECT * FROM users
                    WHERE email=%s
                    """

                    cursor.execute(query, (email,))

                    existing_user = cursor.fetchone()

                    if existing_user:

                        st.error("Email already exists")

                    else:

                        hashed_password = generate_password_hash(
                            password
                        )

                        insert_query = """
                        INSERT INTO users(
                            first_name,
                            last_name,
                            mobile,
                            email,
                            password
                        )
                        VALUES(%s,%s,%s,%s,%s)
                        """

                        cursor.execute(
                            insert_query,
                            (
                                first_name,
                                last_name,
                                mobile,
                                email,
                                hashed_password
                            )
                        )

                        connection.commit()

                        st.success("Signup Successful")

                except Exception as e:

                    st.error(e)

                finally:

                    cursor.close()
                    connection.close()

    # ==================================
    # LOGIN
    # ==================================

    if menu == "Login":

        st.subheader("Login")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            try:

                connection = get_connection()

                cursor = connection.cursor(
                    dictionary=True
                )

                query = """
                SELECT * FROM users
                WHERE email=%s
                """

                cursor.execute(query, (email,))

                user = cursor.fetchone()

                if user and check_password_hash(
                    user["password"],
                    password
                ):

                    st.session_state.logged_in = True

                    st.session_state.user_name = (
                        f"{user['first_name']} {user['last_name']}"
                    )

                    st.session_state.user_email = user["email"]

                    st.session_state.user_mobile = user["mobile"]

                    st.rerun()

                else:

                    st.error("Invalid Credentials")

            except Exception as e:

                st.error(e)

            finally:

                cursor.close()
                connection.close()

# ==================================
# PROFILE PAGE AFTER LOGIN
# ==================================

else:

    st.title("👤 Profile")

    st.subheader("User Details")

    st.write(
        f"**Full Name:** {st.session_state.user_name}"
    )

    st.write(
        f"**Email:** {st.session_state.user_email}"
    )

    st.write(
        f"**Mobile:** {st.session_state.user_mobile}"
    )

    # ==================================
    # UPDATE PROFILE
    # ==================================

    st.divider()

    st.subheader("✏️ Edit Profile")

    current_names = st.session_state.user_name.split()

    new_first_name = st.text_input(
        "First Name",
        value=current_names[0]
    )

    new_last_name = st.text_input(
        "Last Name",
        value=current_names[1]
    )

    new_mobile = st.text_input(
        "Mobile Number",
        value=st.session_state.user_mobile
    )

    if st.button("Update Profile"):

        try:

            connection = get_connection()

            cursor = connection.cursor()

            update_query = """
            UPDATE users
            SET first_name=%s,
                last_name=%s,
                mobile=%s
            WHERE email=%s
            """

            cursor.execute(
                update_query,
                (
                    new_first_name,
                    new_last_name,
                    new_mobile,
                    st.session_state.user_email
                )
            )

            connection.commit()

            st.session_state.user_name = (
                f"{new_first_name} {new_last_name}"
            )

            st.session_state.user_mobile = new_mobile

            st.success("Profile Updated")

        except Exception as e:

            st.error(e)

        finally:

            cursor.close()
            connection.close()

    # ==================================
    # CHANGE PASSWORD
    # ==================================

    st.divider()

    st.subheader("🔒 Change Password")

    old_password = st.text_input(
        "Old Password",
        type="password"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    if st.button("Update Password"):

        try:

            connection = get_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            query = """
            SELECT * FROM users
            WHERE email=%s
            """

            cursor.execute(
                query,
                (st.session_state.user_email,)
            )

            user = cursor.fetchone()

            if check_password_hash(
                user["password"],
                old_password
            ):

                hashed_password = generate_password_hash(
                    new_password
                )

                update_query = """
                UPDATE users
                SET password=%s
                WHERE email=%s
                """

                cursor.execute(
                    update_query,
                    (
                        hashed_password,
                        st.session_state.user_email
                    )
                )

                connection.commit()

                st.success("Password Updated")

            else:

                st.error("Old Password Incorrect")

        except Exception as e:

            st.error(e)

        finally:

            cursor.close()
            connection.close()