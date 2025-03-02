# pages/profile.py
import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_config import db
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(page_title="My Profile - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")
st.sidebar.page_link("pages/profile.py", label="👤 My Profile")
st.sidebar.page_link("pages/auth.py", label="🔑 Login/Register")

# Check authentication status
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in to view your profile")
    st.button("Go to Login Page", on_click=lambda: st.switch_page("pages/auth.py"))
else:
    # Get user data from Firestore
    user_ref = db.collection('users').document(st.session_state.user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        st.error("User data not found. Please try logging in again.")
    else:
        user_data = user_doc.to_dict()
        username = user_data.get('username', '')
        email = user_data.get('email', '')
        full_name = user_data.get('full_name', '')
        bio = user_data.get('bio', '')
        profile_pic = user_data.get('profile_pic', '')
        date_joined = user_data.get('date_joined', '')
        is_premium = user_data.get('is_premium', False)
        
        # --- PROFILE HEADER ---
        profile_header_col1, profile_header_col2 = st.columns([1, 3])
        
        with profile_header_col1:
            if profile_pic:
                st.image(profile_pic, width=200)
            else:
                st.image("https://api.placeholder.com/200/200", width=200)
                
        with profile_header_col2:
            if is_premium:
                st.title(f"{username} 🌟")
                st.caption("Premium Member")
            else:
                st.title(username)
                
            st.write(f"**Member since:** {date_joined}")
            st.write(f"**Full Name:** {full_name or 'Not set'}")
            
            if bio:
                st.write(f"**About me:** {bio}")
                
            # Edit profile button
            if st.button("Edit Profile"):
                st.session_state.editing_profile = True
        
        # Edit profile form
        if st.session_state.get('editing_profile', False):
            st.subheader("Edit Your Profile")
            
            with st.form("edit_profile_form"):
                new_full_name = st.text_input("Full Name", value=full_name)
                new_bio = st.text_area("Bio", value=bio)
                new_profile_pic = st.file_uploader("Profile Picture", type=["jpg", "jpeg", "png"])
                
                submit_changes = st.form_submit_button("Save Changes")
                
                if submit_changes:
                    # Update user data in Firestore
                    updates = {
                        'full_name': new_full_name,
                        'bio': new_bio
                    }
                    
                    # Handle profile picture upload (in a real app, you'd upload to Firebase Storage)
                    if new_profile_pic is not None:
                        # This is a placeholder. In a real app, you'd upload to Firebase Storage
                        # and store the URL in Firestore
                        updates['profile_pic'] = "https://api.placeholder.com/200/200"
                    
                    # Update user document
                    user_ref.update(updates)
                    
                    st.success("Profile updated successfully!")
                    st.session_state.editing_profile = False
                    st.rerun()
            
            if st.button("Cancel"):
                st.session_state.editing_profile = False
                st.rerun()
        
        # --- TABS FOR DIFFERENT SECTIONS ---
        tab1, tab2, tab3 = st.tabs(["My Stats", "My Recipes", "Saved Recipes"])
        
        with tab1:
            st.subheader("Nutrition Summary")
            
            # In a real app, you'd query the user's nutrition data from Firestore
            # For now, using mock data
            dates = pd.date_range(start='2025-02-01', end='2025-03-01')
            nutrition_data = pd.DataFrame({
                'Date': dates,
                'Protein': [round(100 + i*1.5) for i in range(len(dates))],
                'Carbs': [round(150 - i) for i in range(len(dates))],
                'Fat': [round(50 + i*0.5) for i in range(len(dates))],
                'Calories': [round(1800 + i*10) for i in range(len(dates))]
            })
            
            # Nutrition trend chart
            st.subheader("Your Macro Trends")
            fig = px.line(nutrition_data, x='Date', y=['Protein', 'Carbs', 'Fat'], 
                          title='Daily Macro Nutrients (Last 30 Days)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Calorie tracking
            st.subheader("Calorie Tracking")
            fig2 = px.bar(nutrition_data, x='Date', y='Calories', 
                          title='Daily Calorie Intake (Last 30 Days)')
            st.plotly_chart(fig2, use_container_width=True)
            
            # Weekly summary stats
            st.subheader("Weekly Summary")
            weekly_data = nutrition_data.tail(7)
            
            avg_col1, avg_col2, avg_col3, avg_col4 = st.columns(4)
            with avg_col1:
                st.metric("Avg. Protein", f"{round(weekly_data['Protein'].mean())}g", 
                          f"{round(weekly_data['Protein'].mean() - weekly_data['Protein'].iloc[0])}g")
            with avg_col2:
                st.metric("Avg. Carbs", f"{round(weekly_data['Carbs'].mean())}g", 
                          f"{round(weekly_data['Carbs'].mean() - weekly_data['Carbs'].iloc[0])}g")
            with avg_col3:
                st.metric("Avg. Fat", f"{round(weekly_data['Fat'].mean())}g", 
                          f"{round(weekly_data['Fat'].mean() - weekly_data['Fat'].iloc[0])}g")
            with avg_col4:
                st.metric("Avg. Calories", f"{round(weekly_data['Calories'].mean())}", 
                          f"{round(weekly_data['Calories'].mean() - weekly_data['Calories'].iloc[0])}")
        
        with tab2:
            st.subheader("My Shared Recipes")
            
            # Query Firestore for user's recipes
            # In a real app, you'd use this:
            # recipes_query = db.collection('recipes').where('user_id', '==', st.session_state.user_id).get()
            
            # For demo purposes, using mock data
            user_recipes = [
                {"name": "Protein Pancakes", "date": "Feb 28, 2025", "likes": 24, "comments": 3, 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe1"},
                {"name": "Chicken Avocado Wrap", "date": "Feb 20, 2025", "likes": 18, "comments": 2, 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe2"},
                {"name": "Greek Yogurt Bowl", "date": "Feb 15, 2025", "likes": 32, "comments": 5, 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe3"}
            ]
            
            for i, recipe in enumerate(user_recipes):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(recipe["image"], use_column_width=True)
                    
                with col2:
                    st.subheader(recipe["name"])
                    st.write(f"Posted on: {recipe['date']}")
                    st.write(f"❤️ {recipe['likes']} likes • 💬 {recipe['comments']} comments")
                    
                    action_col1, action_col2, action_col3 = st.columns(3)
                    with action_col1:
                        st.button("View Recipe", key=f"view_{i}")
                    with action_col2:
                        st.button("Edit", key=f"edit_{i}")
                    with action_col3:
                        # In a real app, this would delete the recipe document from Firestore
                        if st.button("Delete", key=f"delete_{i}"):
                            # Delete logic would go here, e.g.:
                            # db.collection('recipes').document(recipe['id']).delete()
                            st.success(f"Recipe '{recipe['name']}' deleted successfully!")
                            st.rerun()
                        
                st.divider()
            
            st.button("Create New Recipe", on_click=lambda: st.switch_page("pages/post_meal.py"))
        
        with tab3:
            st.subheader("Recipes You've Saved")
            
            # Query Firestore for saved recipes
            # In a real app, you'd use:
            # saved_refs = db.collection('saved_recipes').where('user_id', '==', st.session_state.user_id).get()
            # saved_recipe_ids = [saved.to_dict()['recipe_id'] for saved in saved_refs]
            # saved_recipes = []
            # for recipe_id in saved_recipe_ids:
            #     recipe = db.collection('recipes').document(recipe_id).get()
            #     if recipe.exists:
            #         recipe_data = recipe.to_dict()
            #         saved_recipes.append(recipe_data)
            
            # For demo purposes, using mock data
            saved_recipes = [
                {"name": "Banana Protein Muffins", "author": "@HealthyBaker", "date_saved": "Mar 1, 2025", 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe4"},
                {"name": "Quinoa Salad Bowl", "author": "@NutritionChef", "date_saved": "Feb 25, 2025", 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe5"},
                {"name": "Low-Carb Pizza", "author": "@KetoKing", "date_saved": "Feb 20, 2025", 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe6"},
                {"name": "Protein Ice Cream", "author": "@FitnessFoodie", "date_saved": "Feb 18, 2025", 
                 "image": "https://api.placeholder.com/300/200", "id": "recipe7"}
            ]
            
            saved_grid_cols = st.columns(2)
            
            for i, recipe in enumerate(saved_recipes):
                with saved_grid_cols[i % 2]:
                    st.image(recipe["image"], use_column_width=True)
                    st.subheader(recipe["name"])
                    st.write(f"By {recipe['author']} • Saved on {recipe['date_saved']}")
                    
                    view_col, unsave_col = st.columns(2)
                    with view_col:
                        st.button("View Recipe", key=f"saved_view_{i}")
                    with unsave_col:
                        # In a real app, this would remove the saved_recipe document from Firestore
                        if st.button("Unsave", key=f"saved_unsave_{i}"):
                            # Unsave logic would go here, e.g.:
                            # saved_query = db.collection('saved_recipes').where('user_id', '==', st.session_state.user_id).where('recipe_id', '==', recipe['id']).get()
                            # for doc in saved_query:
                            #     doc.reference.delete()
                            st.success(f"Recipe '{recipe['name']}' removed from saved recipes!")
                            st.rerun()
                    
                    st.write("")  # Add some spacing