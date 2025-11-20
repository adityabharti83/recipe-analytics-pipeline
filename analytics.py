import os
import pandas as pd
import matplotlib.pyplot as plt


DATA_DIR = "data"
IMAGES_DIR = "images"


def load_data():
    recipes = pd.read_csv(os.path.join(DATA_DIR, "recipe.csv"))
    ingredients = pd.read_csv(os.path.join(DATA_DIR, "ingredients.csv"))
    steps = pd.read_csv(os.path.join(DATA_DIR, "steps.csv"))
    interactions = pd.read_csv(os.path.join(DATA_DIR, "interactions.csv"))
    return recipes, ingredients, steps, interactions


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    recipes, ingredients, steps, interactions = load_data()

    insights = []

    # -----------------------------------------------------------------
    # 1. Top 5 Most Viewed Recipes
    # -----------------------------------------------------------------
    views = interactions[interactions["type"] == "view"]
    views_count = views.groupby("recipeId").size().sort_values(ascending=False)
    top_5_views = views_count.head(5)
    insights.append(("Top 5 Most Viewed Recipes", top_5_views.to_dict()))

    # -----------------------------------------------------------------
    # 2. Top 5 Most Liked Recipes
    # -----------------------------------------------------------------
    likes = interactions[interactions["type"] == "like"]
    likes_count = likes.groupby("recipeId").size().sort_values(ascending=False)
    top_5_likes = likes_count.head(5)
    insights.append(("Top 5 Most Liked Recipes", top_5_likes.to_dict()))

    # -----------------------------------------------------------------
    # 3. Average Rating Per Recipe
    # -----------------------------------------------------------------
    ratings = interactions[interactions["type"] == "rating"]
    if not ratings.empty:
        avg_rating = ratings.groupby("recipeId")["rating"].mean().sort_values(ascending=False)
        insights.append(("Average Rating Per Recipe", avg_rating.to_dict()))
    else:
        insights.append(("Average Rating Per Recipe", {}))

    # -----------------------------------------------------------------
    # 4. Difficulty Distribution Across Recipes
    # -----------------------------------------------------------------
    difficulty_dist = recipes["difficulty"].value_counts().to_dict()
    insights.append(("Difficulty Distribution", difficulty_dist))

    # -----------------------------------------------------------------
    # 5. Average Preparation Time
    # -----------------------------------------------------------------
    avg_prep = recipes["prepTimeMinutes"].mean()
    insights.append(("Average Preparation Time (minutes)", float(avg_prep)))

    # -----------------------------------------------------------------
    # 6. Most Common Ingredients
    # -----------------------------------------------------------------
    ingredient_counts = ingredients["name"].value_counts()
    top_10_ingredients = ingredient_counts.head(10)
    insights.append(("Most Common Ingredients (Top 10)", top_10_ingredients.to_dict()))

    # -----------------------------------------------------------------
    # 7. Correlation Between Prep Time and Likes
    # -----------------------------------------------------------------
    likes_per_recipe = likes.groupby("recipeId").size().reset_index(name="likeCount")
    merged_prep_likes = recipes.merge(likes_per_recipe, on="recipeId", how="left").fillna(0)
    if merged_prep_likes["likeCount"].nunique() > 1:
        corr = merged_prep_likes["prepTimeMinutes"].corr(merged_prep_likes["likeCount"])
    else:
        corr = 0.0
    insights.append(("Correlation between prep time and likes", float(corr)))

    # -----------------------------------------------------------------
    # 8. Average Number of Ingredients Per Recipe
    # -----------------------------------------------------------------
    ing_per_recipe = ingredients.groupby("recipeId").size().mean()
    insights.append(("Average number of ingredients per recipe", float(ing_per_recipe)))

    # -----------------------------------------------------------------
    # 9. Recipes with the Longest Total Cooking Time
    # -----------------------------------------------------------------
    longest_times = recipes.sort_values("totalTimeMinutes", ascending=False).head(5)
    insights.append(
        (
            "Top 5 Longest Recipes by Total Time",
            longest_times[["recipeId", "title", "totalTimeMinutes"]].to_dict(orient="records"),
        )
    )

    # -----------------------------------------------------------------
    # 10. View-to-Like Conversion Rate
    # -----------------------------------------------------------------
    view_like = pd.merge(
        views.groupby("recipeId").size().reset_index(name="views"),
        likes.groupby("recipeId").size().reset_index(name="likes"),
        on="recipeId",
        how="outer",
    ).fillna(0)

    view_like["conversion_rate"] = view_like["likes"] / view_like["views"].replace(0, 1)
    top_conv = view_like.sort_values("conversion_rate", ascending=False).head(5)
    insights.append(
        (
            "View-to-Like Conversion Rate (Top 5)",
            top_conv.to_dict(orient="records"),
        )
    )

    # -----------------------------------------------------------------
    # 11. Ingredients associated with high engagement (avg likes)
    # -----------------------------------------------------------------
    likes_per_recipe = likes.groupby("recipeId").size().reset_index(name="likeCount")
    recipe_ing = ingredients[["recipeId", "name"]]
    ing_likes = recipe_ing.merge(likes_per_recipe, on="recipeId", how="left").fillna(0)
    ing_engagement = (
        ing_likes.groupby("name")["likeCount"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    insights.append(
        (
            "Ingredients associated with high engagement (avg likes)",
            ing_engagement.to_dict(),
        )
    )

    # -----------------------------------------------------------------
    # PRINT INSIGHTS
    # -----------------------------------------------------------------
    print("\n=== RECIPE ANALYTICS REPORT ===\n")
    for title, data in insights:
        print(f"\n{title}:")
        print(data)

    # -----------------------------------------------------------------
    # VISUALIZATIONS
    # -----------------------------------------------------------------

    # 1) Top 5 Most Viewed Recipes (bar)
    if not top_5_views.empty:
        plt.figure(figsize=(8, 4))
        top_5_views.plot(kind="bar")
        plt.title("Top 5 Most Viewed Recipes")
        plt.ylabel("Views")
        plt.xlabel("Recipe ID")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "views_top5.png"))
        plt.close()

    # 2) Top 5 Most Liked Recipes (bar)
    if not top_5_likes.empty:
        plt.figure(figsize=(8, 4))
        top_5_likes.plot(kind="bar")
        plt.title("Top 5 Most Liked Recipes")
        plt.ylabel("Likes")
        plt.xlabel("Recipe ID")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "likes_top5.png"))
        plt.close()

    # 3) Rating distribution (histogram)
    if not ratings.empty:
        plt.figure(figsize=(6, 4))
        ratings["rating"].plot(kind="hist", bins=5)
        plt.title("Rating Distribution")
        plt.xlabel("Rating")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "rating_distribution.png"))
        plt.close()

    # 4) Difficulty distribution (pie)
    plt.figure(figsize=(6, 6))
    recipes["difficulty"].value_counts().plot(kind="pie", autopct="%1.1f%%")
    plt.title("Recipe Difficulty Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "difficulty_distribution.png"))
    plt.close()

    # 5) Prep time vs likes (scatter)
    if not merged_prep_likes.empty:
        plt.figure(figsize=(6, 4))
        plt.scatter(merged_prep_likes["prepTimeMinutes"], merged_prep_likes["likeCount"])
        plt.title("Prep Time vs Likes")
        plt.xlabel("Prep Time (minutes)")
        plt.ylabel("Likes")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "prep_vs_likes.png"))
        plt.close()

    # 6) Top 10 most common ingredients (bar)
    if not top_10_ingredients.empty:
        plt.figure(figsize=(10, 4))
        top_10_ingredients.plot(kind="bar")
        plt.title("Top 10 Most Common Ingredients")
        plt.ylabel("Count")
        plt.xlabel("Ingredient")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "ingredient_frequency_top10.png"))
        plt.close()

    # 7) Interactions by type (bar)
    inter_type_counts = interactions["type"].value_counts()
    if not inter_type_counts.empty:
        plt.figure(figsize=(6, 4))
        inter_type_counts.plot(kind="bar")
        plt.title("Interactions by Type")
        plt.ylabel("Count")
        plt.xlabel("Type")
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "interactions_by_type.png"))
        plt.close()

    print(
        "\nCharts saved in the 'images' folder:\n"
        " - views_top5.png\n"
        " - likes_top5.png\n"
        " - rating_distribution.png\n"
        " - difficulty_distribution.png\n"
        " - prep_vs_likes.png\n"
        " - ingredient_frequency_top10.png\n"
        " - interactions_by_type.png\n"
    )


if __name__ == "__main__":
    main()
