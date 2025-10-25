import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="Aptitude Dashboard", layout="wide")
st.title("📊 Aptitude Test Dashboard")

# -----------------------------
# Firebase Initialization
# -----------------------------
try:
    firebase_credentials = json.loads(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_credentials)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()

except Exception as e:
    st.error(f"❌ Firebase initialization failed: {e}")
    st.stop()

# -----------------------------
# Load Data from Firestore
# -----------------------------
try:
    docs = db.collection("aptitude_results").stream()
    data = [doc.to_dict() for doc in docs]

    if not data:
        st.warning("No data found in Firestore collection 'aptitude_results'.")
        st.stop()

    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"❌ Failed to load data from Firestore: {e}")
    st.stop()

# -----------------------------
# Summary Section
# -----------------------------
st.markdown("### 📈 Summary Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Students", len(df))
col2.metric("Average Score", f"{df['Score'].mean():.2f}")
col3.metric("Highest Score", df['Score'].max())

# -----------------------------
# Search and Filter Section
# -----------------------------
st.markdown("---")
st.subheader("🔍 Search Students")

search = st.text_input("Enter student name or roll number").strip().lower()

if search:
    filtered_df = df[df.apply(
        lambda row: search in str(row.get("Name", "")).lower() or search in str(row.get("Roll", "")).lower(),
        axis=1)]
else:
    filtered_df = df

if filtered_df.empty:
    st.warning("No matching students found.")
else:
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1
    st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# Individual Visualization
# -----------------------------
if not filtered_df.empty:
    st.markdown("---")
    st.subheader("🎯 Individual Student Visualization")

    # Quick search box for student name or roll
    search_name = st.text_input("Enter student name or roll number to locate quickly").strip().lower()

    if search_name:
        matched_students = filtered_df[
            filtered_df.apply(
                lambda row: search_name in str(row.get("Name", "")).lower() or
                            search_name in str(row.get("Roll", "")).lower(),
                axis=1)]
    else:
        matched_students = filtered_df

    if matched_students.empty:
        st.warning("No matching student found.")
    else:
        selected = st.selectbox(
            "Select a student to visualize",
            matched_students["Name"].unique(),
            index=0
        )
        student = df[df["Name"] == selected].iloc[0]

        st.success(f"Showing results for **{student['Name']}** ({student['Roll']})")

        # Charts
        fig_pie = go.Figure(
            go.Pie(
                labels=["Correct", "Incorrect"],
                values=[student["Score"], student["Total"] - student["Score"]],
                hole=0.5,
                marker_colors=["#4CAF50", "#E74C3C"]
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

        # Display charts
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig_pie, config={"displayModeBar": False})
        col2.plotly_chart(fig_gauge, config={"displayModeBar": False})
