# pages/recipe_detail.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from firebase_config import db  # Import Firestore client

# Page configuration
st.set_page_config(page_title="Recipe Details - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")

# Get recipe ID from query parameters
# For actual implementation, we would use st.experimental_get_query_params()
# For demonstration, let's use a URL parameter or session state
recipe_id = st.experimental_get_query_params().get("recipe_id", ["1"])[0]

# Function to fetch recipe from Firestore
def get_recipe_from_firestore(recipe_id):
    try:
        # Get document reference
        recipe_ref = db.collection('recipes').document(recipe_id)
        recipe_doc = recipe_ref.get()
        
        if recipe_doc.exists:
            # Convert Firestore document to dictionary
            recipe = recipe_doc.to_dict()
            recipe['id'] = recipe_id  # Add the ID to the recipe
            return recipe
        else:
            st.error(f"Recipe with ID {recipe_id} not found")
            return get_sample_recipe()  # Fallback to sample recipe
    except Exception as e:
        st.error(f"Error fetching recipe: {e}")
        return get_sample_recipe()  # Fallback to sample recipe

# Sample recipe for fallback
def get_sample_recipe():
    return {
        "id": "1",
        "name": "Protein-Packed Overnight Oats",
        "user": "@HealthyChef",
        "user_profile_pic": "https://api.placeholder.com/100/100",
        "date_posted": "February 28, 2025",
        "image": "https://api.placeholder.com/800/600",
        "category": "Breakfast",
        "description": "A delicious high-protein breakfast that you can prepare the night before. Perfect for busy mornings when you need a nutritious start to your day without spending time cooking.",
        "rating": 4.8,
        "reviews": 124,
        "protein": 32,
        "carbs": 45,
        "fat": 12,
        "calories": 420,
        "fiber": 8,
        "sugar": 6,
        "sodium": 120,
        "prep_time": "5 min",
        "cook_time": "0 min",
        "total_time": "5 min + overnight",
        "servings": 1,
        "ingredients": [
            "1/2 cup rolled oats",
            "1 scoop vanilla protein powder",
            "1 tablespoon chia seeds",
            "1 tablespoon almond butter",
            "1/2 cup almond milk",
            "1/4 cup Greek yogurt",
            "1/2 banana, sliced",
            "1/4 cup berries",
            "1 teaspoon honey or maple syrup (optional)"
        ],
        "instructions": [
            "In a jar or container, mix oats, protein powder, and chia seeds.",
            "Add almond milk and Greek yogurt, then stir until well combined.",
            "Stir in almond butter and sweetener if using.",
            "Seal the container and refrigerate overnight or for at least 4 hours.",
            "Before serving, top with sliced banana and berries."
        ],
        "tags": ["high-protein", "meal-prep", "vegetarian", "quick", "no-cook"],
        "saved_count": 342,
        "likes": 518,
        "similar_recipes": [
            {"id": "2", "name": "Protein Pancakes", "image": "https://api.placeholder.com/150/150"},
            {"id": "3", "name": "Greek Yogurt Bowl", "image": "https://api.placeholder.com/150/150"},
            {"id": "4", "name": "Protein Smoothie", "image": "https://api.placeholder.com/150/150"}
        ]
    }

# Function to update likes and saves
def update_recipe_stats(recipe_id, field, increment=1):
    try:
        recipe_ref = db.collection('recipes').document(recipe_id)
        recipe_ref.update({
            field: firestore.Increment(increment)
        })
        st.success(f"Recipe {field} updated successfully!")
        return True
    except Exception as e:
        st.error(f"Error updating recipe: {e}")
        return False

# Function to add comment to recipe
def add_comment_to_recipe(recipe_id, user_id, username, comment_text):
    try:
        # Create comment document
        comment_data = {
            'recipe_id': recipe_id,
            'user_id': user_id,
            'username': username,
            'text': comment_text,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Add to comments collection
        db.collection('comments').add(comment_data)
        st.success("Comment posted successfully!")
        return True
    except Exception as e:
        st.error(f"Error posting comment: {e}")
        return False

# Function to get comments for a recipe
def get_recipe_comments(recipe_id, limit=10):
    try:
        comments_ref = db.collection('comments').where('recipe_id', '==', recipe_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        comments = [doc.to_dict() for doc in comments_ref.stream()]
        return comments
    except Exception as e:
        st.error(f"Error fetching comments: {e}")
        return []

# Fetch the recipe data
recipe = get_recipe_from_firestore(recipe_id)

# --- RECIPE DETAIL PAGE ---

# Top section: Image and basic info
col_img, col_info = st.columns([3, 2], gap="large")

with col_img:
    st.image(recipe["image"], use_column_width=True)
    
    # Action buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    with btn_col1:
        if st.button("❤️ Like", key="like_btn"):
            if st.session_state.get('authenticated', False):
                update_recipe_stats(recipe_id, 'likes')
                # Also add to user's liked recipes
                user_id = st.session_state.get('user_id')
                if user_id:
                    db.collection('users').document(user_id).collection('liked_recipes').document(recipe_id).set({
                        'recipe_id': recipe_id,
                        'liked_at': firestore.SERVER_TIMESTAMP
                    })
            else:
                st.warning("Please log in to like recipes")
    
    with btn_col2:
        if st.button("🔖 Save", key="save_btn"):
            if st.session_state.get('authenticated', False):
                update_recipe_stats(recipe_id, 'saved_count')
                # Also add to user's saved recipes
                user_id = st.session_state.get('user_id')
                if user_id:
                    db.collection('users').document(user_id).collection('saved_recipes').document(recipe_id).set({
                        'recipe_id': recipe_id,
                        'saved_at': firestore.SERVER_TIMESTAMP
                    })
            else:
                st.warning("Please log in to save recipes")
    
    with btn_col3:
        st.button("📤 Share", key="share_btn")
    
    with btn_col4:
        st.button("🖨️ Print", key="print_btn")

with col_info:
    st.title(recipe["name"])
    
    # User and date info
    st.markdown(f"Posted by {recipe['user']} on {recipe['date_posted']}")
    
    # Rating
    st.markdown(f"⭐ {recipe['rating']} ({recipe['reviews']} ratings)")
    
    # Description
    st.markdown(recipe["description"])
    
    # Tags
    st.markdown("**Tags:** " + ", ".join([f"#{tag}" for tag in recipe["tags"]]))
    
    # Recipe stats
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.markdown(f"**Prep time:**  \n{recipe['prep_time']}")
    with stats_col2:
        st.markdown(f"**Cook time:**  \n{recipe['cook_time']}")
    with stats_col3:
        st.markdown(f"**Servings:**  \n{recipe['servings']}")

# Nutrition information
st.subheader("Nutrition Information")
macro_cols = st.columns(4)

with macro_cols[0]:
    st.metric("Protein", f"{recipe['protein']}g")
with macro_cols[1]:
    st.metric("Carbs", f"{recipe['carbs']}g")
with macro_cols[2]:
    st.metric("Fat", f"{recipe['fat']}g")
with macro_cols[3]:
    st.metric("Calories", f"{recipe['calories']}")

# Macro pie chart
nutrition_data = pd.DataFrame({
    'Nutrient': ['Protein', 'Carbs', 'Fat'],
    'Grams': [recipe['protein'], recipe['carbs'], recipe['fat']],
    'Calories': [recipe['protein'] * 4, recipe['carbs'] * 4, recipe['fat'] * 9]
})

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig = px.pie(nutrition_data, values='Grams', names='Nutrient', 
                 title='Macronutrient Distribution (grams)',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    fig = px.pie(nutrition_data, values='Calories', names='Nutrient', 
                 title='Calorie Distribution',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
    st.plotly_chart(fig, use_container_width=True)

# Ingredients and Instructions
ingredients_col, instructions_col = st.columns(2)

with ingredients_col:
    st.subheader("Ingredients")
    for item in recipe["ingredients"]:
        st.checkbox(item)

with instructions_col:
    st.subheader("Instructions")
    for i, step in enumerate(recipe["instructions"]):
        st.markdown(f"{i+1}. {step}")

# Comments section
st.subheader("Comments")

# Add new comment
with st.form("comment_form"):
    comment_text = st.text_area("Leave a comment", placeholder="Share your thoughts or ask a question...")
    submit_comment = st.form_submit_button("Post Comment")

if submit_comment and comment_text:
    if st.session_state.get('authenticated', False):
        user_id = st.session_state.get('user_id')
        username = st.session_state.get('username', 'Anonymous')
        add_comment_to_recipe(recipe_id, user_id, username, comment_text)
    else:
        st.warning("Please log in to comment")

# Display existing comments
comments = get_recipe_comments(recipe_id)
if comments:
    for comment in comments:
        st.markdown(f"**{comment['username']}** • {comment.get('created_at', 'Just now')}  \n{comment['text']}")
else:
    # Display sample comments if no actual comments found
    st.markdown("**@FitnessFoodie** • 2 days ago  \nMade this yesterday and loved it! I added a tablespoon of cocoa powder for a chocolate version. Delicious!")
    st.markdown("**@ProteinQueen** • 5 days ago  \nThis has become my go-to breakfast! So convenient and keeps me full until lunch.")

# Function to get similar recipes
def get_similar_recipes(recipe_id, category, tags, limit=3):
    try:
        # Query recipes with the same category and at least one matching tag
        similar_ref = db.collection('recipes').where('category', '==', category).limit(limit+1)
        similar_recipes = []
        
        # Process results and exclude the current recipe
        for doc in similar_ref.stream():
            recipe_data = doc.to_dict()
            if doc.id != recipe_id:
                similar_recipes.append({
                    'id': doc.id,
                    'name': recipe_data.get('name', 'Recipe'),
                    'image': recipe_data.get('image', 'https://api.placeholder.com/150/150')
                })
            
            if len(similar_recipes) >= limit:
                break
                
        return similar_recipes
    except Exception as e:
        st.error(f"Error fetching similar recipes: {e}")
        return recipe.get('similar_recipes', [])

# Similar recipes section
similar_recipes = get_similar_recipes(recipe_id, recipe['category'], recipe.get('tags', []))
if not similar_recipes:
    similar_recipes = recipe.get('similar_recipes', [])

st.subheader("You might also like")
similar_cols = st.columns(3)

for i, similar in enumerate(similar_recipes):
    with similar_cols[i]:
        st.image(similar["image"], use_column_width=True)
        st.markdown(f"**{similar['name']}**")
        if st.button("View Recipe", key=f"similar_{i}"):
            # Redirect to the recipe page with the new recipe_id
            new_recipe_id = similar['id']
            st.experimental_set_query_params(recipe_id=new_recipe_id)
            st.rerun()