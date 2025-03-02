# pages/auth.py
import streamlit as st
import pandas as pd
import hashlib
import re
from datetime import datetime
from firebase_config import db
import uuid

# Page configuration
st.set_page_config(page_title="Login/Register - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")
st.sidebar.page_link("pages/auth.py", label="👤 Login/Register")

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Email validation function
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_id = None
    st.rerun()

# Main content
if st.session_state.authenticated:
    # Display logged in user interface
    st.title(f"Welcome back, {st.session_state.username}! 👋")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image("https://api.placeholder.com/200/200", use_column_width=True)
        st.button("Edit Profile", key="edit_profile")
        
    with col2:
        # Fetch user info from Firestore
        user_doc = db.collection('users').document(st.session_state.user_id).get()
        
        if user_doc.exists:
            user_info = user_doc.to_dict()
            full_name = user_info.get('full_name', 'Not set')
            bio = user_info.get('bio', 'No bio yet')
            date_joined = user_info.get('date_joined', 'Unknown')
            is_premium = user_info.get('is_premium', False)
            
            if is_premium:
                st.markdown("#### 🌟 Premium Member")
            
            st.markdown(f"**Full Name:** {full_name}")
            st.markdown(f"**Bio:** {bio}")
            st.markdown(f"**Member since:** {date_joined}")
    
    # Activity overview
    st.subheader("Your Activity")
    
    # Count user's activity metrics from Firestore
    # For demo purposes, using static numbers
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Recipes Shared", "12")
    with metric_col2:
        st.metric("Saved Recipes", "34")
    with metric_col3:
        st.metric("Total Likes", "156")
    with metric_col4:
        st.metric("Comments", "28")
    
    # Recent activity
    st.subheader("Recent Activity")
    st.markdown("• You shared a recipe: **Protein Banana Bread** (2 days ago)")
    st.markdown("• You commented on **@HealthyChef's** recipe (3 days ago)")
    st.markdown("• You saved 2 recipes to your collection (1 week ago)")
    
    # Logout option
    st.divider()
    st.button("Logout", on_click=logout)

else:
    # Display login/register interface with tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        # Login form
        with st.form("login_form"):
            username_email = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me")
            
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                if not username_email or not password:
                    st.error("Please fill in all fields.")
                else:
                    # Check if input is email or username
                    if '@' in username_email:
                        query = db.collection('users').where('email', '==', username_email).limit(1)
                    else:
                        query = db.collection('users').where('username', '==', username_email).limit(1)
                    
                    results = query.get()
                    
                    if len(results) > 0:
                        user_doc = results[0]
                        user_data = user_doc.to_dict()
                        
                        if user_data['password_hash'] == hash_password(password):
                            st.session_state.authenticated = True
                            st.session_state.user_id = user_doc.id
                            st.session_state.username = user_data['username']
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid password.")
                    else:
                        st.error("Username or email not found.")
        
        # Password recovery link
        st.markdown("[Forgot your password?](#)")
        
    with tab2:
        st.subheader("Create a New Account")
        
        # Registration form
        with st.form("register_form"):
            reg_username = st.text_input("Username (required)")
            reg_email = st.text_input("Email (required)")
            reg_password = st.text_input("Password (required)", type="password")
            reg_confirm_password = st.text_input("Confirm Password", type="password")
            reg_full_name = st.text_input("Full Name (optional)")
            
            terms_agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            register_submitted = st.form_submit_button("Register")
            
            if register_submitted:
                # Validate input
                if not reg_username or not reg_email or not reg_password:
                    st.error("Please fill in all required fields.")
                elif not is_valid_email(reg_email):
                    st.error("Please enter a valid email address.")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords don't match.")
                elif not terms_agree:
                    st.error("You must agree to the Terms of Service and Privacy Policy.")
                else:
                    # Check if username or email already exists
                    username_query = db.collection('users').where('username', '==', reg_username).limit(1).get()
                    email_query = db.collection('users').where('email', '==', reg_email).limit(1).get()
                    
                    if len(username_query) > 0:
                        st.error("Username already exists. Please choose a different one.")
                    elif len(email_query) > 0:
                        st.error("Email already exists. Please use a different email.")
                    else:
                        try:
                            # Create new user in Firestore
                            new_user = {
                                'username': reg_username,
                                'email': reg_email,
                                'password_hash': hash_password(reg_password),
                                'full_name': reg_full_name,
                                'bio': '',
                                'profile_pic': '',
                                'date_joined': datetime.now().strftime("%Y-%m-%d"),
                                'is_premium': False
                            }
                            
                            # Add user to Firestore
                            user_ref = db.collection('users').document()
                            user_ref.set(new_user)
                            
                            # Set session state
                            st.session_state.authenticated = True
                            st.session_state.user_id = user_ref.id
                            st.session_state.username = reg_username
                            
                            st.success("Registration successful! Welcome to Leo's Food App!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error creating account: {e}")
        
        # Terms and conditions
        st.markdown("By creating an account, you agree to our [Terms of Service](#) and [Privacy Policy](#).")

# Add some helpful information at the bottom
st.divider()
st.markdown("""
### Why Create an Account?
- **Save your favorite recipes** for quick access
- **Share your own meals** with the community
- **Track your nutrition goals** with personalized dashboards
- **Connect with other food enthusiasts** and share tips
""")