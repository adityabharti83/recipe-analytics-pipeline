import gradio as gr
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------------------------------------------------------------
# Firebase initialization
# ------------------------------------------------------------------------------

def init_firebase():
    """
    Initializes Firebase Admin SDK and returns a Firestore client.
    Edit the credentials part to match your setup:
    - Service Account JSON
    - or Application Default Credentials
    """
    if not firebase_admin._apps:
        # Initialize with your service account key
        cred = credentials.Certificate("serviceAccountKey.json")  # Update this path
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# ------------------------------------------------------------------------------
# Firestore-backed recipe + event helpers
# ------------------------------------------------------------------------------

def load_recipes():
    """
    Reads recipes from Firestore collection: `recipes`

    Expected document structure:
    - name (string)
    - difficulty (string)
    - avg_rating (number)
    - total_cook_time_min (number)
    - tags (array<string>)
    """
    recipes = []
    docs = db.collection("recipes").stream()
    for doc in docs:
        data = doc.to_dict() or {}
        recipes.append({
            "id": doc.id,
            "name": data.get("name"),
            "difficulty": data.get("difficulty", "Unknown"),
            "avg_rating": data.get("avg_rating"),
            "total_cook_time_min": data.get("total_cook_time_min"),
            "tags": data.get("tags"),
        })
    return recipes

# Loaded once at startup
RECIPES = load_recipes()

def get_recipe_by_name(name: str):
    for r in RECIPES:
        if r["name"] == name:
            return r
    return None

def fetch_recipe_events(recipe_id: str, days: int) -> pd.DataFrame:
    """
    Reads events from Firestore collection: `recipe_events`

    Expected document structure:
    - user_id (string)
    - recipe_id (string)
    - event_type (string: view/favorite/start_cook/complete_cook)
    - timestamp (Firestore Timestamp)
    - source (string)
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)

    # Query recipe events
    q = (db.collection("recipe_events")
           .where("recipe_id", "==", recipe_id)
           .where("timestamp", ">=", cutoff))

    events = []
    for doc in q.stream():
        data = doc.to_dict() or {}
        ts = data.get("timestamp")

        # Convert Firestore Timestamp -> Python datetime
        # If already a datetime (e.g. from emulator), keep as is.
        if hasattr(ts, "to_datetime"):
            ts = ts.to_datetime()

        events.append({
            "user_id": data.get("user_id"),
            "recipe_id": data.get("recipe_id"),
            "event_type": data.get("event_type"),
            "timestamp": ts,
            "source": data.get("source"),
        })

    if not events:
        return pd.DataFrame(columns=["user_id", "recipe_id", "event_type", "timestamp", "source"])

    return pd.DataFrame(events)

# ------------------------------------------------------------------------------
# Analytics logic
# ------------------------------------------------------------------------------

def compute_recipe_analytics(recipe_name: str, time_window: str):
    """
    Core analytics function using REAL Firestore data.
    time_window: 'Last 7 days' | 'Last 14 days' | 'Last 30 days'
    """
    if not RECIPES:
        return (
            "No recipes found in Firestore collection `recipes`.",
            None,
            "Make sure your `recipes` collection has documents."
        )

    recipe = get_recipe_by_name(recipe_name)
    if recipe is None:
        return (
            f"Recipe **{recipe_name}** not found in `recipes` collection.",
            None,
            "Check the recipe name or Firestore data."
        )

    days_map = {"Last 7 days": 7, "Last 14 days": 14, "Last 30 days": 30}
    days = days_map.get(time_window, 7)

    df = fetch_recipe_events(recipe["id"], days)

    if df.empty:
        return (
            f"No events for **{recipe_name}** in the selected window from `recipe_events`.",
            None,
            "No matching documents in `recipe_events` for this filter."
        )

    # Aggregate counts per event type
    counts = df.groupby("event_type").size().reset_index(name="count")

    # Basic funnel metrics
    total_views = int(counts[counts["event_type"] == "view"]["count"].sum())
    favorites = int(counts[counts["event_type"] == "favorite"]["count"].sum())
    starts = int(counts[counts["event_type"] == "start_cook"]["count"].sum())
    completes = int(counts[counts["event_type"] == "complete_cook"]["count"].sum())

    completion_rate = (completes / starts * 100) if starts > 0 else 0
    fav_rate = (favorites / total_views * 100) if total_views > 0 else 0

    summary_md = f"""
### 📊 Analytics for **{recipe_name}** ({time_window})

**From Firestore collections: `recipes` + `recipe_events`**

- **Total Views**: `{total_views}`
- **Times Marked Favorite**: `{favorites}`  
- **Cooking Sessions Started**: `{starts}`  
- **Cooking Sessions Completed**: `{completes}`  
- **Completion Rate**: `{completion_rate:.1f}%`  
- **Favorite / View Rate**: `{fav_rate:.1f}%`

**Recipe Meta (from `recipes/{recipe['id']}`)**

- Difficulty: **{recipe['difficulty']}**
- Avg. Rating: **{recipe['avg_rating']} ⭐**
- Total Cook Time: **{recipe['total_cook_time_min']} mins**
- Tags: `{", ".join(recipe['tags']) if recipe['tags'] else "—"}`
"""

    # Bar chart
    fig = px.bar(
        counts,
        x="event_type",
        y="count",
        title=f"Event Breakdown for {recipe_name} ({time_window})",
    )

    # Sample table preview (10 latest events)
    df_sorted = df.sort_values("timestamp", ascending=False).head(10)
    df_preview_str = df_sorted.to_markdown(index=False)

    return summary_md, fig, df_preview_str

# ------------------------------------------------------------------------------
# Project Overview + Data Flow text (updated to mention collections)
# ------------------------------------------------------------------------------

def project_overview():
    return """
# 🍽️ Recipe Analytics Pipeline (Firebase + Gradio)

This UI sits on top of your **Firebase Recipe Analytics Pipeline** and reads data
directly from:

- **`recipes`** collection (recipe definitions)
- **`recipe_events`** collection (user interaction events)

**What the pipeline does:**

- Captures recipe interactions: `view`, `favorite`, `start_cook`, `complete_cook`
- Stores raw events in **Firestore** (`recipe_events`)
- Aggregates them (views, favorites, funnels, completion rate)
- Serves metrics to this Gradio dashboard for:
  - Instant analytics exploration
  - Stakeholder demo
  - Portfolio / interview showcase

**Tech Stack**

- **Data Source**: Firebase Firestore (`recipes`, `recipe_events`)
- **Processing**: Python + Pandas (can extend to Spark / Beam)
- **Orchestration**: Cloud Functions / cron / Airflow (depending on version)
- **Visualization**: Gradio + Plotly
"""

def data_flow_description():
    return """
## 🔄 Data Flow (Collection-level View)

1. **Client Apps → Firestore (`recipe_events`)**
   - User opens recipe → write doc to **`recipe_events`**:
     ```json
     {
       "user_id": "uid_123",
       "recipe_id": "white_sauce_pasta",
       "event_type": "view",
       "timestamp": "2025-11-24T10:30:00Z",
       "source": "android_app"
     }
     ```
   - Similar docs for `favorite`, `start_cook`, `complete_cook`.

2. **Recipe Metadata → Firestore (`recipes`)**
   - Each recipe is a document in **`recipes`**:
     ```json
     {
       "name": "White Sauce Pasta",
       "difficulty": "Easy",
       "avg_rating": 4.6,
       "total_cook_time_min": 30,
       "tags": ["Italian", "Creamy", "Quick Dinner"]
     }
     ```

3. **Batch / Near-Real-Time Aggregations**
   - (Optional) Cloud Functions / scheduled jobs:
     - Aggregate by `recipe_id` and time window
     - Compute:
       - total views
       - favorites
       - start → complete funnel
       - completion & favorite rates
   - You can store aggregates in an `recipe_analytics` collection
     or compute on the fly (like this demo).

4. **Serving Layer → Gradio Dashboard**
   - This UI:
     - Reads recipe list from `recipes`
     - Filters events from `recipe_events` by `recipe_id` + time window
     - Computes metrics with Pandas
     - Displays:
       - Summary KPIs
       - Event breakdown chart
       - Sample raw events table

👉 To match your **exact** schema, just update:
- Collection names: `recipes`, `recipe_events`
- Field names in `load_recipes()` and `fetch_recipe_events()`.
"""

# ------------------------------------------------------------------------------
# Build Gradio UI
# ------------------------------------------------------------------------------

with gr.Blocks(title="Recipe Analytics Pipeline Demo") as demo:
    gr.Markdown("# 🍽️ Recipe Analytics Dashboard\nFirebase collections: `recipes` + `recipe_events`")

    with gr.Tab("Project Overview"):
        gr.Markdown(project_overview())
        gr.Markdown("Use the other tabs to explore the data flow and live analytics.")

    with gr.Tab("Data Flow"):
        gr.Markdown(data_flow_description())

    with gr.Tab("Analytics Demo"):
        if RECIPES:
            recipe_names = [r["name"] for r in RECIPES]
            default_recipe = recipe_names[0]
        else:
            recipe_names = ["No recipes found"]
            default_recipe = "No recipes found"

        with gr.Row():
            with gr.Column(scale=1):
                recipe_dropdown = gr.Dropdown(
                    recipe_names,
                    label="Select Recipe (from `recipes`)",
                    value=default_recipe,
                )
                time_window_dropdown = gr.Dropdown(
                    ["Last 7 days", "Last 14 days", "Last 30 days"],
                    label="Time Window",
                    value="Last 7 days",
                )
                run_btn = gr.Button("Run Analytics")

            with gr.Column(scale=2):
                summary_output = gr.Markdown(label="Summary")
                chart_output = gr.Plot(label="Event Breakdown")
                table_output = gr.Markdown(label="Sample Events Preview (latest 10)")

        def on_run(recipe_name, time_window):
            return compute_recipe_analytics(recipe_name, time_window)

        run_btn.click(
            fn=on_run,
            inputs=[recipe_dropdown, time_window_dropdown],
            outputs=[summary_output, chart_output, table_output],
        )

if __name__ == "__main__":
    demo.launch()
