import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import os

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
PROJECT_ID = "fir-data-lab-a6307"
SERVICE_ACCOUNT_PATH = r"serviceAccountKey.json" 
OUTPUT_DIR = "data"

# -------------------------------------------------------------------
# INIT FIRESTORE
# -------------------------------------------------------------------
def init_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
    return firestore.client()

# -------------------------------------------------------------------
# HELPER: SAFE DATETIME → STRING
# -------------------------------------------------------------------
def to_iso(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt  # if it's already string or None, just return

# -------------------------------------------------------------------
# EXTRACT & TRANSFORM: RECIPES → recipe.csv, ingredients.csv, steps.csv
# -------------------------------------------------------------------
def export_recipes(db):
    recipes_ref = db.collection("recipes")
    docs = list(recipes_ref.stream())

    recipe_rows = []
    ingredient_rows = []
    step_rows = []

    for doc in docs:
        data = doc.to_dict()
        recipe_id = data.get("recipeId", doc.id)

        # -----------------------
        # recipe.csv row
        # -----------------------
        recipe_rows.append({
            "recipeId": recipe_id,
            "title": data.get("title"),
            "description": data.get("description"),
            "authorId": data.get("authorId"),
            "cuisine": data.get("cuisine"),
            "category": data.get("category"),
            "difficulty": data.get("difficulty"),
            "prepTimeMinutes": data.get("prepTimeMinutes"),
            "cookTimeMinutes": data.get("cookTimeMinutes"),
            "totalTimeMinutes": data.get("totalTimeMinutes"),
            "servings": data.get("servings"),
            "tags": ",".join(data.get("tags", [])) if data.get("tags") else "",
            "createdAt": to_iso(data.get("createdAt")),
            "updatedAt": to_iso(data.get("updatedAt")),
            "isPublic": data.get("isPublic"),
        })

        # -----------------------
        # ingredients.csv rows
        # -----------------------
        ingredients = data.get("ingredients", [])
        for ing in ingredients:
            ingredient_rows.append({
                "recipeId": recipe_id,
                "ingredientId": ing.get("ingredientId"),
                "name": ing.get("name"),
                "quantity": ing.get("quantity"),
                "unit": ing.get("unit"),
                "notes": ing.get("notes"),
            })

        # -----------------------
        # steps.csv rows
        # -----------------------
        steps = data.get("steps", [])
        for s in steps:
            step_rows.append({
                "recipeId": recipe_id,
                "stepNumber": s.get("stepNumber"),
                "instruction": s.get("instruction"),
                "approxMinutes": s.get("approxMinutes"),
            })

    # Convert to DataFrames
    recipes_df = pd.DataFrame(recipe_rows)
    ingredients_df = pd.DataFrame(ingredient_rows)
    steps_df = pd.DataFrame(step_rows)

    # Ensure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save CSVs
    recipes_path = os.path.join(OUTPUT_DIR, "recipe.csv")
    ingredients_path = os.path.join(OUTPUT_DIR, "ingredients.csv")
    steps_path = os.path.join(OUTPUT_DIR, "steps.csv")

    recipes_df.to_csv(recipes_path, index=False)
    ingredients_df.to_csv(ingredients_path, index=False)
    steps_df.to_csv(steps_path, index=False)

    print(f" Exported recipes to {recipes_path}")
    print(f" Exported ingredients to {ingredients_path}")
    print(f" Exported steps to {steps_path}")

# -------------------------------------------------------------------
# EXTRACT & TRANSFORM: INTERACTIONS → interactions.csv
# -------------------------------------------------------------------
def export_interactions(db):
    interactions_ref = db.collection("interactions")
    docs = list(interactions_ref.stream())

    rows = []

    for doc in docs:
        data = doc.to_dict()
        interaction_id = data.get("interactionId", doc.id)

        rows.append({
            "interactionId": interaction_id,
            "userId": data.get("userId"),
            "recipeId": data.get("recipeId"),
            "type": data.get("type"),
            "createdAt": to_iso(data.get("createdAt")),
            "rating": data.get("rating"),
            "difficultyRating": data.get("difficultyRating"),
            "successStatus": data.get("successStatus"),
            "comment": data.get("comment"),
            "source": data.get("source"),
        })

    df = pd.DataFrame(rows)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    interactions_path = os.path.join(OUTPUT_DIR, "interactions.csv")
    df.to_csv(interactions_path, index=False)

    print(f" Exported interactions to {interactions_path}")

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    db = init_firestore()
    export_recipes(db)
    export_interactions(db)
    print(" ETL export complete.")
