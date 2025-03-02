# pages/post_meal.py
import streamlit as st
import pandas as pd
from datetime import datetime
from firebase_config import db
import uuid
import base64
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Share Your Meal - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")

# Check if user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in to share your meals.")
    if st.button("Go to Login"):
        st.switch_page("pages/auth.py")
else:
    # Function to handle image upload and convert to base64
    def get_image_base64(uploaded_file):
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            b64 = base64.b64encode(bytes_data).decode()
            return f"data:image/{uploaded_file.type.split('/')[-1]};base64,{b64}"
        return None
    
    # Check if we're editing an existing recipe
    editing = False
    recipe_data = {}
    
    if 'edit_recipe_id' in st.session_state and st.session_state.edit_recipe_id:
        editing = True
        try:
            recipe_doc = db.collection('recipes').document(st.session_state.edit_recipe_id).get()
            if recipe_doc.exists:
                recipe_data = recipe_doc.to_dict()
                st.title(f"Edit Recipe: {recipe_data.get('name', '')}")
            else:
                st.error("Recipe not found. Creating a new recipe instead.")
                editing = False
                st.session_state.edit_recipe_id = None
        except Exception as e:
            st.error(f"Error fetching recipe for editing: {e}")
            editing = False
            st.session_state.edit_recipe_id = None
    
    if not editing:
        st.title("Share Your Meal 📝")
        st.write("Fill out the form below to share your meal with the community!")

    with st.form("meal_form"):
        # Basic meal information
        col1, col2 = st.columns(2)
        
        with col1:
            meal_name = st.text_input("Meal Name", value=recipe_data.get('name', ''), 
                                      placeholder="e.g., Protein-Packed Breakfast Bowl")
            
            meal_category = st.selectbox("Category", 
                                        ["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"],
                                        index=["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"].index(recipe_data.get('category', 'Breakfast')) if 'category' in recipe_data else 0)
            
            meal_tags = st.text_input("Tags (comma separated)", 
                                     value=', '.join(recipe_data.get('tags', [])) if 'tags' in recipe_data else '',
                                     placeholder="e.g., high-protein, keto, vegan")
        
        with col2:
            meal_description = st.text_area("Description", 
                                           value=recipe_data.get('description', ''),
                                           placeholder="Describe your meal in a few sentences...")
            
            recipe_url = st.text_input("Recipe URL (optional)", 
                                      value=recipe_data.get('recipe_url', ''),
                                      placeholder="Link to full recipe if available")
        
        # Image upload
        st.subheader("Meal Image")
        uploaded_image = st.file_uploader("Upload an image of your meal", type=["jpg", "jpeg", "png"])
        
        # Show a preview if image is uploaded or if editing a recipe with an image
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Image Preview", use_column_width=True)
        elif 'image' in recipe_data and recipe_data['image']:
            st.image(recipe_data['image'], caption="Current Image", use_column_width=True)
            st.info("Upload a new image to replace the current one, or leave empty to keep it.")
        
        # Nutrition information
        st.subheader("Nutrition Information")
        
        macro_col1, macro_col2, macro_col3, macro_col4 = st.columns(4)
        
        with macro_col1:
            protein = st.number_input("Protein (g)", min_value=0, 
                                     value=int(recipe_data.get('protein', 20)) if 'protein' in recipe_data else 20)
        
        with macro_col2:
            carbs = st.number_input("Carbs (g)", min_value=0, 
                                   value=int(recipe_data.get('carbs', 30)) if 'carbs' in recipe_data else 30)
        
        with macro_col3:
            fat = st.number_input("Fat (g)", min_value=0, 
                                 value=int(recipe_data.get('fat', 10)) if 'fat' in recipe_data else 10)
        
        with macro_col4:
            default_calories = protein*4 + carbs*4 + fat*9
            calories = st.number_input("Calories", min_value=0, 
                                      value=int(recipe_data.get('calories', default_calories)) if 'calories' in recipe_data else default_calories)
        
        # Additional macros (collapsible)
        with st.expander("Additional Nutrition Info (Optional)"):
            add_col1, add_col2, add_col3 = st.columns(3)
            
            with add_col1:
                fiber = st.number_input("Fiber (g)", min_value=0, 
                                       value=int(recipe_data.get('fiber', 0)) if 'fiber' in recipe_data else 0)
                
                sugar = st.number_input("Sugar (g)", min_value=0, 
                                       value=int(recipe_data.get('sugar', 0)) if 'sugar' in recipe_data else 0)
            
            with add_col2:
                sodium = st.number_input("Sodium (mg)", min_value=0, 
                                        value=int(recipe_data.get('sodium', 0)) if 'sodium' in recipe_data else 0)
                
                cholesterol = st.number_input("Cholesterol (mg)", min_value=0, 
                                             value=int(recipe_data.get('cholesterol', 0)) if 'cholesterol' in recipe_data else 0)
            
            with add_col3:
                saturated_fat = st.number_input("Saturated Fat (g)", min_value=0, 
                                               value=float(recipe_data.get('saturated_fat', 0)) if 'saturated_fat' in recipe_data else 0)
                
                trans_fat = st.number_input("Trans Fat (g)", min_value=0, 
                                           value=float(recipe_data.get('trans_fat', 0)) if 'trans_fat' in recipe_data else 0)
        
        # Ingredients and Instructions
        st.subheader("Ingredients")
        default_ingredients = '\n'.join(recipe_data.get('ingredients', [])) if 'ingredients' in recipe_data else ''
        ingredients = st.text_area("List your ingredients (one per line)", height=150, 
                                  value=default_ingredients,
                                  placeholder="1 cup oats\n2 scoops protein powder\n1 tbsp peanut butter")
        
        st.subheader("Instructions")
        default_instructions = '\n'.join(recipe_data.get('instructions', [])) if 'instructions' in recipe_data else ''
        instructions = st.text_area("Recipe instructions", height=150,
                                   value=default_instructions,
                                   placeholder="1. Mix oats and protein powder\n2. Add water and microwave for 2 minutes\n3. Top with peanut butter")
        
        # Submit button
        if editing:
            submitted = st.form_submit_button("Update Recipe")
        else:
            submitted = st.form_submit_button("Share Your Meal")

    if submitted:
        try:
            # Calculate actual calories from macros
            calculated_calories = protein * 4 + carbs * 4 + fat * 9
            
            # Process the image
            image_url = None
            if uploaded_image:
                image_url = get_image_base64(uploaded_image)
            elif 'image' in recipe_data and recipe_data['image']:
                image_url = recipe_data['image']
            
            # Process tags
            tags = [tag.strip() for tag in meal_tags.split(',') if tag.strip()]
            
            # Process ingredients and instructions as lists
            ingredients_list = [line.strip() for line in ingredients.split('\n') if line.strip()]
            instructions_list = [line.strip() for line in instructions.split('\n') if line.strip()]
            
            # Prepare data for Firestore
            recipe_data = {
                'name': meal_name,
                'category': meal_category,
                'tags': tags,
                'description': meal_description,
                'recipe_url': recipe_url,
                'image': image_url,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'calories': calories,
                'fiber': fiber,
                'sugar': sugar,
                'sodium': sodium,
                'cholesterol': cholesterol,
                'saturated_fat': saturated_fat,
                'trans_fat': trans_fat,
                'ingredients': ingredients_list,
                'instructions': instructions_list,
                'user_id': st.session_state.user_id,
                'username': st.session_state.username,
                'updated_at': datetime.now().isoformat()
            }
            
            if editing:
                # Update existing recipe
                db.collection('recipes').document(st.session_state.edit_recipe_id).update(recipe_data)
                st.success("Your recipe has been updated successfully!")
                # Clear edit state
                st.session_state.edit_recipe_id = None
            else:
                # Add new fields for new recipes
                recipe_data.update({
                    'date_posted': datetime.now().isoformat(),
                    'likes': 0,
                    'comments': 0,
                    'rating': 0,
                    'reviews': 0,
                    'saved_count': 0
                })
                
                # Add to Firestore
                new_recipe_ref = db.collection('recipes').document()
                new_recipe_ref.set(recipe_data)
                
                st.success("Your meal has been shared successfully!")
            
            # Show a preview of how it will appear in the feed
            st.subheader("Preview:")
            
            preview_col1, preview_col2 = st.columns([1, 2])
            
            with preview_col1:
                if image_url:
                    st.image(image_url, use_column_width=True)
                else:
                    st.image("https://api.placeholder.com/400/300", use_column_width=True)
            
            with preview_col2:
                st.markdown(f"### {meal_name}")
                st.markdown(f"**Category:** {meal_category}")
                st.markdown(f"**Description:** {meal_description}")
                
                st.markdown("#### Nutrition Facts")
                st.markdown(f"**Protein:** {protein}g | **Carbs:** {carbs}g | **Fat:** {fat}g | **Calories:** {calories}")
                
                if recipe_url:
                    st.markdown(f"[View Full Recipe]({recipe_url})")
            
            # Button to view all recipes
            if st.button("View All Recipes"):
                st.switch_page("pages/my_recipes.py")
            
            # Button to create another recipe
            if st.button("Share Another Meal"):
                st.rerun()
                
        except Exception as e:
            st.error(f"Error saving your recipe: {e}")