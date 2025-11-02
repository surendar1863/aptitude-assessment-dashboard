import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_autorefresh import st_autorefresh
import datetime as dt

# -------------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------------
st.set_page_config(page_title="Aptitude Dashboard", layout="wide")
st.title("📊 Aptitude Test Dashboard")

# -------------------------------------------------------
# Auto Refresh Every 10 seconds
# -------------------------------------------------------
st_autorefresh(interval=10000, key="datarefresh")
st.caption(f"🔄 Last auto-update: {dt.datetime.now().strftime('%H:%M:%S')}")

# -------------------------------------------------------
# Initialize Firebase using Streamlit Secrets
# -------------------------------------------------------
# ---------------- FIREBASE INIT (drop-in) ----------------
def init_firestore():
    """Initialize Firebase from Streamlit secrets (supports [firebase_key] or [firebase]).
    Falls back to local firebase_key.json if present."""
    if firebase_admin._apps:
        return firestore.client()

    cfg = None
    try:
        raw = st.secrets.get("firebase_key", None)
        if raw is None:
            raw = st.secrets.get("firebase", None)

        if raw is not None:
            # st.secrets returns a Mapping (TOML table) or str (JSON) depending on how you saved it
            cfg = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except Exception:
        cfg = None

    if cfg:
        cred = credentials.Certificate(cfg)
        firebase_admin.initialize_app(cred)
        return firestore.client()

    # Local fallback for development
    import os
    if os.path.exists("firebase_key.json"):
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
        return firestore.client()

    st.error("Firebase configuration not found in secrets or local file.")
    st.stop()

# Call it BEFORE any Firestore usage
db = init_firestore()
st.success(f"Connected to Firestore project: {firebase_admin.get_app().project_id}")


# -------------------------------------------------------
# Load Firestore Data
# -------------------------------------------------------
try:
    docs = db.collection("aptitude_results").stream()
    data = [doc.to_dict() for doc in docs]
    if not data:
        st.info("⚠️ No student records found yet.")
        st.stop()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Error fetching data from Firestore: {e}")
    st.stop()

# -------------------------------------------------------
# Summary Metrics
# -------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("👩‍🎓 Total Students", len(df))
col2.metric("📈 Average Score", f"{df['Score'].mean():.2f}")
col3.metric("🏆 Max Score", df['Score'].max())

# -------------------------------------------------------
# Search Bar
# -------------------------------------------------------
st.subheader("🔍 Search Student")
search = st.text_input("Enter student name or roll number to filter:", "").strip().lower()

if search:
    filtered_df = df[df.apply(
        lambda row: search in str(row['Name']).lower() or search in str(row['Roll']).lower(),
        axis=1
    )]
else:
    filtered_df = df.copy()

filtered_df = filtered_df.reset_index(drop=True)
filtered_df.index = filtered_df.index + 1

# -------------------------------------------------------
# Display Table
# -------------------------------------------------------
st.write("### 🧾 Student Results")
st.dataframe(filtered_df, use_container_width=True)

# -------------------------------------------------------
# Individual Student Visualization
# -------------------------------------------------------
if not filtered_df.empty:
    st.write("### 🎯 Individual Student Visualization")

    search_name = st.text_input("Enter student name or roll number to locate quickly", "").strip().lower()

    if search_name:
        matched = filtered_df[
            filtered_df.apply(
                lambda row: search_name in str(row["Name"]).lower() or search_name in str(row["Roll"]).lower(),
                axis=1,
            )
        ]
    else:
        matched = filtered_df

    if matched.empty:
        st.warning("No matching student found.")
    else:
        selected = st.selectbox("Select a student to visualize", matched["Name"].unique(), index=0)
        student = df[df["Name"] == selected].iloc[0]

        st.success(f"Showing results for **{student['Name']}** ({student['Roll']})")

        # -------------------------------------------------------
        # Charts
        # -------------------------------------------------------
        fig_pie = go.Figure(
            go.Pie(
                labels=["Correct", "Incorrect"],
                values=[student["Score"], student["Total"] - student["Score"]],
                hole=0.5,
                marker_colors=["#4CAF50", "#E74C3C"],
            )
        )
        fig_pie.update_layout(title_text="Score Distribution", width=420, height=350)

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=student["Score"],
                title={"text": "Student Score"},
                gauge={
                    "axis": {"range": [0, student["Total"]]},
                    "bar": {"color": "#4CAF50"},
                    "steps": [
                        {"range": [0, student["Total"] * 0.5], "color": "#FFDDDD"},
                        {"range": [student["Total"] * 0.5, student["Total"]], "color": "#D4EFDF"},
                    ],
                },
            )
        )
        fig_gauge.update_layout(width=420, height=350)

        col1, col2 = st.columns(2)
        col1.plotly_chart(fig_pie, config={"displayModeBar": False})
        col2.plotly_chart(fig_gauge, config={"displayModeBar": False})

# -------------------------------------------------------
# Manual Refresh Button
# -------------------------------------------------------
st.divider()
if st.button("🔄 Manual Refresh Now"):
    st.experimental_rerun()

