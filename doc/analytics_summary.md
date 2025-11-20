# 📊 Recipe Analytics Summary

This document summarizes the key insights generated from the **Firebase-based Recipe Analytics Pipeline**.  
The analytics are derived from normalized CSV outputs:

- `data/recipe.csv`
- `data/ingredients.csv`
- `data/steps.csv`
- `data/interactions.csv`

and computed using `analytics.py`.

---

## 1. Dataset Overview

| Metric              | Value        |
|---------------------|-------------|
| Total Recipes       | 16          |
| Total Users         | 5           |
| Total Interactions  | 200+        |
| Primary Recipe      | White Sauce Pasta |
| Average Rating      | ~4.2 / 5    |
| Avg Prep Time       | ~13 minutes |

The dataset consists of a mix of one real recipe (White Sauce Pasta) and multiple synthetic recipes across various cuisines (Indian, Italian, American, Global, etc.).

---

## 2. Recipe Performance Insights

### 2.1 Most Viewed Recipes

Based on `interactions.csv` filtered for `type = "view"`:

**Top 5 Most Viewed Recipes:**

1. Veg Wrap – 7 views  
2. White Sauce Pasta – 6 views  
3. Fried Rice – 5 views  
4. Grilled Veg Sandwich – 5 views  
5. Lemon Rice – 5 views  

These recipes tend to be **quick, familiar, and relatively easy**, which likely drives higher view counts.

---

### 2.2 Most Liked Recipes

Based on `interactions.csv` filtered for `type = "like"`:

**Top 5 Most Liked Recipes:**

1. Paneer Butter Masala – 10 likes  
2. Chocolate Brownie – 6 likes  
3. White Sauce Pasta – 5 likes  
4. Grilled Veg Sandwich – 4 likes  
5. Tomato Soup – 4 likes  

**Observation:**  
Rich, comfort-style dishes (Paneer Butter Masala, Chocolate Brownie) generate the strongest engagement.

---

### 2.3 Average Ratings per Recipe

Using `interactions.csv` where `type = "rating"`:

Sample of highest-rated recipes:

- Grilled Veg Sandwich – **5.0 / 5**  
- Veg Fried Rice – **4.67 / 5**  
- Chocolate Brownie – **4.5 / 5**  
- Veg Pulao – **4.33 / 5**  
- Masala Veg Maggi – **4.25 / 5**  

Even simple recipes (e.g., Maggi, Veg Pulao) score well, suggesting users appreciate **quick and reliable recipes**.

---

### 2.4 Difficulty Distribution

From `recipe.csv`:

- **Easy:** 12 recipes (75%)  
- **Medium:** 4 recipes (25%)  
- **Hard:** 0 recipes (0%)  

The dataset is intentionally biased toward **easy and approachable recipes**, which is realistic for a home-cooking app.

---

### 2.5 Preparation & Cooking Time

From `recipe.csv`:

- **Average prep time:** ≈ 13 minutes  
- **Total time range:** from ~5 minutes (smoothies / quick snacks) up to ~45 minutes (Paneer Butter Masala, Dal Tadka, Chocolate Brownie)

**Longer recipes** tend to be main courses or desserts, while snacks and breakfast items dominate the shorter time range.

---

### 2.6 View-to-Like Conversion (Engagement Efficiency)

Using views vs likes per recipe:

- Shorter, snack-style recipes (e.g., Veg Wrap, Veg Maggi, Grilled Sandwich) show **higher view-to-like conversion rates**.
- Heavier main-course dishes get solid likes but slightly lower conversion as they may be browsed more than acted on.

This suggests:

> Users are more likely to **like** recipes that are quick to make and fit into everyday snacking or breakfast.

---

## 3. Ingredient-Level Insights

### 3.1 Most Common Ingredients

From `ingredients.csv`, counting ingredient occurrences:

- 🧅 **Onion** – most frequently used ingredient  
- 🍅 **Tomato** – appears in many Indian and global recipes  
- 🧂 **Salt**, 🌶️ **Spices**, and 🛢️ **Oil** – expected staples  

This matches a typical Indian / global household cooking pattern.

---

### 3.2 Average Ingredients per Recipe

From `ingredients.csv` grouped by `recipeId`:

- **Average ingredients per recipe:** ~6–8  

Most recipes are **moderately complex**: enough steps to be interesting, but not too long to be intimidating.

---

### 3.3 Ingredients Associated with High Engagement (Conceptual)

By linking `ingredients.csv` with likes per recipe:

- Recipes containing **paneer**, **chocolate**, and **cheese** tend to have higher average likes.
- Everyday base ingredients like onion and tomato are common across all engagement levels, but **“treat” ingredients** drive spikes in interaction.

---

## 4. User Engagement Insights

### 4.1 Interaction Types

From `interactions.csv`:

- **Views:** majority of events – browsing and discovering recipes  
- **Likes:** smaller but meaningful subset – strong positive signal  
- **Cook Attempts:** show deeper engagement (users actually tried the recipe)  
- **Ratings:** used to derive average rating per recipe  

Cook attempts frequently include:

- `difficultyRating` (1–5)  
- `successStatus` ("success", "failed", "partial")  
- Optional comments (e.g., “Turned out great!”, “A bit too spicy”)

This structure supports rich engagement analytics beyond simple counts.

---

### 4.2 Correlation Between Prep Time and Likes

Using `recipes` + likes per recipe:

- There is a **slight negative correlation** between prep time and likes:  
  *shorter recipes tend to receive more likes on average.*

This is consistent with modern user behavior: people favor **quick, low-friction recipes**.

---

### 4.3 Primary Recipe Performance – White Sauce Pasta

The primary seed recipe (White Sauce Pasta):

- Appears in the **Top viewed** and **Top liked** list  
- Receives **high satisfaction ratings** (≥ 4 / 5)  
- Is marked as **easy** with a moderate total time (~35 minutes)

This validates the choice of White Sauce Pasta as a strong seed recipe for the dataset.

---

## 5. Key Takeaways

1. **User Preference for Ease:**  
   Majority of recipes are **easy**, and these see strong engagement.

2. **Comfort Food Wins:**  
   Dishes like **Paneer Butter Masala**, **Chocolate Brownie**, and **White Sauce Pasta** attract a lot of likes and positive ratings.

3. **Time Matters:**  
   There is evidence that **shorter prep time** correlates with **higher engagement**, especially for snacks and quick meals.

4. **Core Ingredient Patterns:**  
   Onion and tomato are foundational ingredients, while items like paneer, cheese, and chocolate help lift engagement.

5. **Healthy Dataset for Analytics:**  
   The mix of views, likes, cook attempts, and ratings provides a solid base for deeper modeling (recommendations, personalization, etc.).

---

_This analytics summary is generated from the latest run of the pipeline using `analytics.py` and reflects the current state of the synthetic + real recipe dataset._
