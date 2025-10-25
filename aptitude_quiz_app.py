import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json

# -----------------------------
# Initialize Firebase using Streamlit Secrets
# -----------------------------
if not firebase_admin._apps:
    try:
        firebase_credentials = json.loads(st.secrets["firebase_key"])
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"❌ Firebase initialization failed: {e}")
        st.stop()
else:
    db = firestore.client()

# -----------------------------
# App Title
# -----------------------------
st.title("🧠 Aptitude Quiz")

# -----------------------------
# User Details
# -----------------------------
name = st.text_input("Enter your name")
roll = st.text_input("Enter your Roll No")

# -----------------------------
# Load Questions from CSV
# -----------------------------
try:
    df = pd.read_csv("aptitude_questions.csv")  # your uploaded CSV file
except Exception as e:
    st.error(f"⚠️ Could not load questions file: {e}")
    st.stop()

# -----------------------------
# Display Questions
# -----------------------------
st.subheader("Answer the following questions:")

user_answers = {}
for i, row in df.iterrows():
    q = row["Question"]
    options = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
    user_choice = st.radio(f"{i+1}. {q}", options, key=f"q_{i}")
    user_answers[q] = user_choice

# -----------------------------
# Submit Answers
# -----------------------------
if st.button("Submit"):
    if not name or not roll:
        st.warning("⚠️ Please enter both Name and Roll Number before submitting.")
    else:
        score = 0
        total = len(df)

        for i, row in df.iterrows():
            correct = str(row["Correct"]).strip().lower()
            given = str(user_answers[row["Question"]]).strip().lower()
            if correct == given:
                score += 1

        try:
            # Save result to Firestore
            db.collection("aptitude_results").document(roll).set({
                "Name": name,
                "Roll": roll,
                "Score": score,
                "Total": total
            })
            st.success(f"✅ Your response has been recorded successfully! Score: {score}/{total}")
        except Exception as e:
            st.error(f"❌ Error saving your result: {e}")

# -----------------------------
# 📥 Admin / Export Section
# -----------------------------
st.subheader("📥 Export All Responses (Admin Use)")

if st.button("Download All Responses as CSV"):
    try:
        docs = db.collection("aptitude_results").stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())

        if data:
            df_results = pd.DataFrame(data)
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV File",
                data=csv,
                file_name="aptitude_responses.csv",
                mime="text/csv"
            )
        else:
            st.info("No records found yet.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
