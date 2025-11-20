import pandas as pd
import json
from datetime import datetime

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def is_valid_timestamp(value):
    if pd.isna(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", ""))
        return True
    except:
        return False

def fail(reason):
    return {"valid": False, "reason": reason}

def ok():
    return {"valid": True, "reason": ""}
    
# -------------------------------------------------------------------
# VALIDATION FUNCTIONS
# -------------------------------------------------------------------
def validate_recipes(df):
    results = []

    for _, row in df.iterrows():
        # Required fields
        required = ["recipeId", "title", "description", "authorId", 
                    "difficulty", "prepTimeMinutes", "cookTimeMinutes", 
                    "totalTimeMinutes", "servings"]

        for col in required:
            if pd.isna(row[col]):
                results.append(fail(f"Missing required field: {col}"))
                break
        else:
            # Difficulty check
            if row["difficulty"] not in ["easy", "medium", "hard"]:
                results.append(fail("Invalid difficulty value"))
                continue

            # Time checks
            if row["prepTimeMinutes"] <= 0:
                results.append(fail("prepTimeMinutes must be > 0"))
                continue
            if row["cookTimeMinutes"] < 0:
                results.append(fail("cookTimeMinutes must be >= 0"))
                continue
            if row["prepTimeMinutes"] + row["cookTimeMinutes"] != row["totalTimeMinutes"]:
                results.append(fail("totalTimeMinutes mismatch"))
                continue

            # Servings
            if row["servings"] <= 0:
                results.append(fail("servings must be > 0"))
                continue

            # Timestamp checks
            if not is_valid_timestamp(row["createdAt"]):
                results.append(fail("Invalid createdAt timestamp"))
                continue
            if not is_valid_timestamp(row["updatedAt"]):
                results.append(fail("Invalid updatedAt timestamp"))
                continue

            results.append(ok())

    return results

def validate_ingredients(df):
    results = []
    for _, row in df.iterrows():
        if pd.isna(row["recipeId"]):
            results.append(fail("Missing recipeId"))
            continue
        if pd.isna(row["ingredientId"]):
            results.append(fail("Missing ingredientId"))
            continue
        if pd.isna(row["name"]) or row["name"].strip() == "":
            results.append(fail("Invalid ingredient name"))
            continue
        if row["quantity"] < 0:
            results.append(fail("quantity must be >= 0"))
            continue

        results.append(ok())
    return results

def validate_steps(df):
    results = []
    for _, row in df.iterrows():
        if row["stepNumber"] < 1:
            results.append(fail("stepNumber must be >= 1"))
            continue
        if pd.isna(row["instruction"]) or row["instruction"].strip() == "":
            results.append(fail("Invalid instruction"))
            continue
        if not pd.isna(row["approxMinutes"]) and row["approxMinutes"] < 0:
            results.append(fail("approxMinutes must be >= 0"))
            continue

        results.append(ok())
    return results

def validate_interactions(df):
    results = []
    valid_types = ["view", "like", "cook_attempt", "rating"]

    for _, row in df.iterrows():
        if row["type"] not in valid_types:
            results.append(fail("Invalid interaction type"))
            continue

        if not is_valid_timestamp(row["createdAt"]):
            results.append(fail("Invalid createdAt timestamp"))
            continue

        # rating rules
        if row["type"] == "rating":
            if pd.isna(row["rating"]) or not (1 <= row["rating"] <= 5):
                results.append(fail("rating must be 1–5 for type=rating"))
                continue
        else:
            if not pd.isna(row["rating"]):
                results.append(fail("rating present but type != rating"))
                continue

        # difficultyRating rules
        if row["type"] == "cook_attempt":
            if pd.isna(row["difficultyRating"]) or not (1 <= row["difficultyRating"] <= 5):
                results.append(fail("difficultyRating must be 1–5 for cook_attempt"))
                continue
        else:
            if not pd.isna(row["difficultyRating"]):
                results.append(fail("difficultyRating present but type != cook_attempt"))
                continue

        results.append(ok())

    return results

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    report = {}

    recipes = pd.read_csv("data/recipe.csv")
    ingredients = pd.read_csv("data/ingredients.csv")
    steps = pd.read_csv("data/steps.csv")
    interactions = pd.read_csv("data/interactions.csv")

    r1 = validate_recipes(recipes)
    r2 = validate_ingredients(ingredients)
    r3 = validate_steps(steps)
    r4 = validate_interactions(interactions)

    def summarize(results):
        valid = sum(1 for r in results if r["valid"])
        invalid = len(results) - valid
        return valid, invalid, results

    report["recipes"] = summarize(r1)
    report["ingredients"] = summarize(r2)
    report["steps"] = summarize(r3)
    report["interactions"] = summarize(r4)

    # Create JSON-friendly structure
    final = {
        "recipes": {"valid": report["recipes"][0], "invalid": report["recipes"][1]},
        "ingredients": {"valid": report["ingredients"][0], "invalid": report["ingredients"][1]},
        "steps": {"valid": report["steps"][0], "invalid": report["steps"][1]},
        "interactions": {
            "valid": report["interactions"][0],
            "invalid": report["interactions"][1],
            "invalid_records": [
                r
                for r in report["interactions"][2]
                if not r["valid"]
            ]
        }
    }

    with open("validation_report.json", "w") as f:
        json.dump(final, f, indent=4)

    print("Validation complete! See validation_report.json.")
