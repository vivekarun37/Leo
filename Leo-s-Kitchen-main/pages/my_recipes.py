import streamlit as st
from firebase_config import db

# Page configuration
st.set_page_config(page_title="My Recipes - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")

# Check if user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in to view your saved recipes.")
    if st.button("Go to Login"):
        st.switch_page("pages/auth.py")
else:
    st.title("My Recipes")
    st.write(f"Welcome, {st.session_state.username}! Here are all your saved recipes.")
    
    # Create tabs for different recipe views
    tab1, tab2, tab3 = st.tabs(["Saved Recipes", "My Posts", "Favorites"])
    
    with tab1:
        # Fetch saved recipes from Firebase
        try:
            saved_recipes = db.collection('users').document(st.session_state.user_id).collection('saved_recipes').get()
            
            if not saved_recipes:
                st.info("You haven't saved any recipes yet. Explore the home page to find recipes to save!")
            else:
                # Display recipes in a grid
                st.subheader(f"You have {len(saved_recipes)} saved recipes")
                
                # Create columns for grid layout
                cols = st.columns(3)
                
                for i, recipe_doc in enumerate(saved_recipes):
                    recipe = recipe_doc.to_dict()
                    
                    with cols[i % 3]:
                        # Display recipe card
                        if 'image' in recipe:
                            st.image(recipe['image'], use_column_width=True)
                        else:
                            st.image("https://api.placeholder.com/400/300", use_column_width=True)
                        
                        st.markdown(f"#### {recipe.get('name', 'Untitled Recipe')}")
                        
                        if 'rating' in recipe and 'reviews' in recipe:
                            st.markdown(f"⭐ {recipe['rating']} ({recipe['reviews']} ratings)")
                        
                        # Display macros if available
                        if all(key in recipe for key in ['protein', 'carbs', 'fat', 'calories']):
                            st.markdown(f"**Protein:** {recipe['protein']}g • **Carbs:** {recipe['carbs']}g • **Fat:** {recipe['fat']}g")
                            st.markdown(f"**Calories:** {recipe['calories']}")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("View Recipe", key=f"view_{recipe_doc.id}"):
                                # Save recipe ID to session state and navigate to detail page
                                st.session_state.current_recipe_id = recipe_doc.id
                                st.switch_page("pages/recipe_detail.py")
                        
                        with col2:
                            if st.button("Remove", key=f"remove_{recipe_doc.id}"):
                                # Remove recipe from saved recipes
                                db.collection('users').document(st.session_state.user_id).collection('saved_recipes').document(recipe_doc.id).delete()
                                st.success("Recipe removed from your saved recipes!")
                                st.rerun()
        
        except Exception as e:
            st.error(f"Error fetching your saved recipes: {e}")
    
    with tab2:
        # Fetch recipes posted by the user
        try:
            user_posts = db.collection('recipes').where('user_id', '==', st.session_state.user_id).get()
            
            if not user_posts:
                st.info("You haven't posted any recipes yet. Share your meals to see them here!")
                if st.button("Create Recipe Post"):
                    st.switch_page("pages/post_meal.py")
            else:
                st.subheader(f"You have {len(user_posts)} posted recipes")
                
                # Create columns for grid layout
                cols = st.columns(3)
                
                for i, post_doc in enumerate(user_posts):
                    post = post_doc.to_dict()
                    
                    with cols[i % 3]:
                        # Display recipe card
                        if 'image' in post:
                            st.image(post['image'], use_column_width=True)
                        else:
                            st.image("https://api.placeholder.com/400/300", use_column_width=True)
                        
                        st.markdown(f"#### {post.get('name', 'Untitled Recipe')}")
                        st.markdown(f"Posted on: {post.get('date_posted', 'Unknown date')}")
                        
                        if 'likes' in post:
                            st.markdown(f"❤️ {post['likes']} likes")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("View", key=f"view_post_{post_doc.id}"):
                                st.session_state.current_recipe_id = post_doc.id
                                st.switch_page("pages/recipe_detail.py")
                        
                        with col2:
                            if st.button("Edit", key=f"edit_{post_doc.id}"):
                                st.session_state.edit_recipe_id = post_doc.id
                                st.switch_page("pages/post_meal.py")
        
        except Exception as e:
            st.error(f"Error fetching your posted recipes: {e}")
    
    with tab3:
        # Fetch favorite recipes (different from saved)
        try:
            favorites = db.collection('users').document(st.session_state.user_id).collection('favorites').get()
            
            if not favorites:
                st.info("You haven't favorited any recipes yet.")
            else:
                st.subheader(f"You have {len(favorites)} favorite recipes")
                
                # Similar layout as above tabs
                cols = st.columns(3)
                
                for i, fav_doc in enumerate(favorites):
                    fav = fav_doc.to_dict()
                    
                    with cols[i % 3]:
                        # Basic recipe card display
                        if 'image' in fav:
                            st.image(fav['image'], use_column_width=True)
                        else:
                            st.image("https://api.placeholder.com/400/300", use_column_width=True)
                        
                        st.markdown(f"#### {fav.get('name', 'Untitled Recipe')}")
                        
                        # Action button
                        if st.button("View Recipe", key=f"view_fav_{fav_doc.id}"):
                            st.session_state.current_recipe_id = fav_doc.id
                            st.switch_page("pages/recipe_detail.py")
        
        except Exception as e:
            st.error(f"Error fetching your favorite recipes: {e}")