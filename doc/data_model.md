# 📐 Data Model – Firebase Recipe Analytics Pipeline

This document describes the data model used in the **Recipe Analytics Pipeline**, including:

- Firestore collections and their schemas
- Relationships between entities
- How the model maps to normalized CSV tables

The source of truth is **Firebase Firestore**, and the analytics pipeline exports data into:

- `data/recipe.csv`
- `data/ingredients.csv`
- `data/steps.csv`
- `data/interactions.csv`

---

## 1. High-Level Overview

The system tracks:

- **Users** – people using the app
- **Recipes** – cooking instructions with ingredients and steps
- **Interactions** – how users view, like, rate, and attempt recipes

At a conceptual level:

- A **user** can author many recipes.
- A **recipe** belongs to a single author.
- A **user** can interact with many recipes.
- A **recipe** can receive interactions from many users.

---

## 2. ERD-Style Diagram

```mermaid
erDiagram
    USERS {
      string userId
      string displayName
      string email
      string skillLevel
      string[] dietPreferences
      datetime createdAt
    }

    RECIPES {
      string recipeId
      string title
      string description
      string authorId
      string cuisine
      string category
      string difficulty
      int prepTimeMinutes
      int cookTimeMinutes
      int totalTimeMinutes
      int servings
      string[] tags
      datetime createdAt
      datetime updatedAt
      bool isPublic
    }

    INTERACTIONS {
      string interactionId
      string userId
      string recipeId
      string type
      int rating
      int difficultyRating
      string successStatus
      string comment
      string source
      datetime createdAt
    }

    USERS ||--o{ RECIPES : "authors"
    USERS ||--o{ INTERACTIONS : "performs"
    RECIPES ||--o{ INTERACTIONS : "receives"
