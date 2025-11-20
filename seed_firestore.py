import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import random

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
PROJECT_ID = "fir-data-lab-a6307"
SERVICE_ACCOUNT_PATH = r"serviceAccountKey.json"

# -------------------------------------------------------------------
# INIT FIRESTORE
# -------------------------------------------------------------------
def init_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
    return firestore.client()

# -------------------------------------------------------------------
# SEED USERS
# -------------------------------------------------------------------
def seed_users(db):
    now = datetime.utcnow()

    users = [
        {
            "userId": "user_adi",
            "displayName": "Adi",
            "email": "adi@example.com",
            "createdAt": now,
            "skillLevel": "intermediate",
            "dietPreferences": ["vegetarian"],
        },
        {
            "userId": "user_chef_1",
            "displayName": "Home Chef 1",
            "email": "chef1@example.com",
            "createdAt": now - timedelta(days=10),
            "skillLevel": "beginner",
            "dietPreferences": ["non-veg"],
        },
        {
            "userId": "user_chef_2",
            "displayName": "Home Chef 2",
            "email": "chef2@example.com",
            "createdAt": now - timedelta(days=20),
            "skillLevel": "expert",
            "dietPreferences": ["vegan"],
        },
        {
            "userId": "user_taster_1",
            "displayName": "Food Lover 1",
            "email": "food1@example.com",
            "createdAt": now - timedelta(days=5),
            "skillLevel": "beginner",
            "dietPreferences": [],
        },
        {
            "userId": "user_taster_2",
            "displayName": "Food Lover 2",
            "email": "food2@example.com",
            "createdAt": now - timedelta(days=2),
            "skillLevel": "intermediate",
            "dietPreferences": ["vegetarian"],
        },
    ]

    for user in users:
        db.collection("users").document(user["userId"]).set(user)

    print(f" Seeded {len(users)} users.")

# -------------------------------------------------------------------
# SEED RECIPES (YOUR RECIPE + SYNTHETIC)
# -------------------------------------------------------------------
def create_white_sauce_pasta_recipe(now):
    return {
        "recipeId": "recipe_white_sauce_pasta",
        "title": "Creamy White Sauce Pasta",
        "description": "A simple, creamy white sauce pasta made with milk, butter, and herbs.",
        "authorId": "user_adi",
        "cuisine": "Italian",
        "category": "Main Course",
        "difficulty": "easy",
        "prepTimeMinutes": 15,
        "cookTimeMinutes": 20,
        "totalTimeMinutes": 35,
        "servings": 2,
        "ingredients": [
            { "ingredientId": "WSP-ING-01", "name": "Penne pasta", "quantity": 200, "unit": "grams", "notes": "or any short pasta" },
            { "ingredientId": "WSP-ING-02", "name": "Butter", "quantity": 2, "unit": "tbsp", "notes": "" },
            { "ingredientId": "WSP-ING-03", "name": "All-purpose flour (maida)", "quantity": 2, "unit": "tbsp", "notes": "" },
            { "ingredientId": "WSP-ING-04", "name": "Milk", "quantity": 1.5, "unit": "cups", "notes": "room temperature" },
            { "ingredientId": "WSP-ING-05", "name": "Garlic", "quantity": 3, "unit": "cloves", "notes": "finely chopped" },
            { "ingredientId": "WSP-ING-06", "name": "Mixed herbs", "quantity": 1, "unit": "tsp", "notes": "oregano + chilli flakes" },
            { "ingredientId": "WSP-ING-07", "name": "Black pepper", "quantity": 0.5, "unit": "tsp", "notes": "freshly crushed" },
            { "ingredientId": "WSP-ING-08", "name": "Salt", "quantity": 1, "unit": "tsp", "notes": "adjust to taste" },
            { "ingredientId": "WSP-ING-09", "name": "Cheese (optional)", "quantity": 0.25, "unit": "cup", "notes": "grated" }
        ],
        "steps": [
            {
                "stepNumber": 1,
                "instruction": "Boil pasta in salted water until al dente. Drain and keep aside.",
                "approxMinutes": 10
            },
            {
                "stepNumber": 2,
                "instruction": "In a pan, melt butter on low flame and sauté garlic until fragrant.",
                "approxMinutes": 3
            },
            {
                "stepNumber": 3,
                "instruction": "Add flour and cook, stirring continuously, until the raw smell goes away.",
                "approxMinutes": 2
            },
            {
                "stepNumber": 4,
                "instruction": "Slowly add milk while whisking to avoid lumps. Cook until the sauce thickens.",
                "approxMinutes": 5
            },
            {
                "stepNumber": 5,
                "instruction": "Season with salt, black pepper, and mixed herbs. Add cheese if using.",
                "approxMinutes": 2
            },
            {
                "stepNumber": 6,
                "instruction": "Add boiled pasta to the sauce, toss well, and cook for a couple of minutes.",
                "approxMinutes": 3
            }
        ],
        "tags": ["pasta", "vegetarian", "quick", "white sauce"],
        "createdAt": now - timedelta(days=3),
        "updatedAt": now - timedelta(days=1),
        "isPublic": True,
    }

def create_synthetic_recipe(recipe_id_suffix, title, cuisine, category, difficulty,
                            prep_time, cook_time, servings, author_id, now):
    total_time = prep_time + cook_time
    ingredients = [
        {
            "ingredientId": f"{recipe_id_suffix}-ING-01",
            "name": "Onion",
            "quantity": 1,
            "unit": "piece",
            "notes": "finely chopped"
        },
        {
            "ingredientId": f"{recipe_id_suffix}-ING-02",
            "name": "Tomato",
            "quantity": 2,
            "unit": "piece",
            "notes": "pureed"
        },
        {
            "ingredientId": f"{recipe_id_suffix}-ING-03",
            "name": "Oil",
            "quantity": 2,
            "unit": "tbsp",
            "notes": ""
        },
    ]
    steps = [
        {
            "stepNumber": 1,
            "instruction": "Heat oil in a pan and sauté onions until golden.",
            "approxMinutes": 5
        },
        {
            "stepNumber": 2,
            "instruction": "Add tomatoes and cook until soft.",
            "approxMinutes": 7
        },
        {
            "stepNumber": 3,
            "instruction": "Add spices and cook the mixture.",
            "approxMinutes": 5
        },
    ]

    return {
        "recipeId": f"recipe_{recipe_id_suffix}",
        "title": title,
        "description": f"A simple {title} recipe for everyday cooking.",
        "authorId": author_id,
        "cuisine": cuisine,
        "category": category,
        "difficulty": difficulty,
        "prepTimeMinutes": prep_time,
        "cookTimeMinutes": cook_time,
        "totalTimeMinutes": total_time,
        "servings": servings,
        "ingredients": ingredients,
        "steps": steps,
        "tags": [cuisine.lower(), category.lower()],
        "createdAt": now - timedelta(days=random.randint(1, 30)),
        "updatedAt": now - timedelta(days=random.randint(0, 5)),
        "isPublic": True,
    }

def seed_recipes(db):
    now = datetime.utcnow()

    recipes = []
    recipes.append(create_white_sauce_pasta_recipe(now))

    synthetic_specs = [
        ("paneer_butter_masala", "Paneer Butter Masala", "Indian", "Main Course", "medium", 20, 25, 3, "user_chef_1"),
        ("veg_pulao", "Veg Pulao", "Indian", "Main Course", "easy", 15, 20, 2, "user_chef_1"),
        ("masala_omelette", "Masala Omelette", "Indian", "Breakfast", "easy", 10, 5, 1, "user_chef_2"),
        ("choco_brownie", "Chocolate Brownie", "American", "Dessert", "medium", 20, 30, 4, "user_chef_2"),
        ("grilled_sandwich", "Grilled Veg Sandwich", "Global", "Snack", "easy", 10, 10, 2, "user_adi"),
        ("veg_maggi", "Masala Veg Maggi", "Indian", "Snack", "easy", 5, 7, 1, "user_adi"),
        ("salad_bowl", "Rainbow Salad Bowl", "Global", "Salad", "easy", 15, 0, 2, "user_taster_1"),
        ("dal_tadka", "Dal Tadka", "Indian", "Main Course", "easy", 15, 20, 3, "user_chef_1"),
        ("fried_rice", "Veg Fried Rice", "Chinese", "Main Course", "medium", 20, 15, 2, "user_chef_2"),
        ("pancakes", "Soft Pancakes", "American", "Breakfast", "easy", 10, 10, 2, "user_taster_2"),
        ("smoothie", "Berry Banana Smoothie", "Global", "Beverage", "easy", 5, 0, 1, "user_taster_2"),
        ("garlic_bread", "Garlic Bread", "Italian", "Snack", "easy", 10, 12, 2, "user_adi"),
        ("tomato_soup", "Tomato Soup", "Global", "Starter", "easy", 10, 15, 2, "user_chef_1"),
        ("veg_wrap", "Veg Wrap", "Global", "Snack", "medium", 15, 10, 1, "user_chef_2"),
        ("lemon_rice", "Lemon Rice", "Indian", "Main Course", "easy", 10, 10, 2, "user_taster_1"),
    ]

    for spec in synthetic_specs:
        recipes.append(
            create_synthetic_recipe(
                recipe_id_suffix=spec[0],
                title=spec[1],
                cuisine=spec[2],
                category=spec[3],
                difficulty=spec[4],
                prep_time=spec[5],
                cook_time=spec[6],
                servings=spec[7],
                author_id=spec[8],
                now=now,
            )
        )

    for recipe in recipes:
        db.collection("recipes").document(recipe["recipeId"]).set(recipe)

    print(f" Seeded {len(recipes)} recipes.")

# -------------------------------------------------------------------
# SEED INTERACTIONS
# -------------------------------------------------------------------
def seed_interactions(db):
    now = datetime.utcnow()

    user_ids = ["user_adi", "user_chef_1", "user_chef_2", "user_taster_1", "user_taster_2"]
    interaction_types = ["view", "like", "cook_attempt", "rating"]

    recipes_stream = db.collection("recipes").stream()
    recipe_ids = [r.id for r in recipes_stream]

    count = 0
    for recipe_id in recipe_ids:
        for user_id in user_ids:
            for _ in range(random.randint(1, 4)):
                interaction_type = random.choice(interaction_types)
                created_at = now - timedelta(days=random.randint(0, 30), minutes=random.randint(0, 1440))

                data = {
                    "userId": user_id,
                    "recipeId": recipe_id,
                    "type": interaction_type,
                    "createdAt": created_at,
                    "source": random.choice(["web", "mobile"])
                }

                if interaction_type == "rating":
                    data["rating"] = random.randint(3, 5)
                if interaction_type == "cook_attempt":
                    data["difficultyRating"] = random.randint(1, 5)
                    data["successStatus"] = random.choice(["success", "failed", "partial"])
                    data["comment"] = random.choice([
                        "Turned out great!",
                        "A bit too spicy.",
                        "Nice and easy recipe.",
                        ""
                    ])

                doc_ref = db.collection("interactions").document()
                data["interactionId"] = doc_ref.id
                doc_ref.set(data)
                count += 1

    print(f" Seeded {count} interactions.")

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    db = init_firestore()
    seed_users(db)
    seed_recipes(db)
    seed_interactions(db)
    print(" Seeding complete.")
