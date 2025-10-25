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
# Questions
# -----------------------------
questions = [
    {"q": "5 + 7 =", "a": "12"},
    {"q": "Capital of India?", "a": "New Delhi"},
    {"q": "10 * 3 =", "a": "30"},
]

score = 0
answers = []

for q in questions:
    ans = st.text_input(f"{q['q']}")
    answers.append(ans)
    if ans.strip().lower() == q['a'].strip().lower():
        score += 1

# -----------------------------
# Submit Button
# -----------------------------
if st.button("Submit"):
    if not name or not roll:
        st.warning("⚠️ Please enter both Name and Roll Number before submitting.")
    else:
        total = len(questions)
        try:
            # Store result in Firestore collection
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
# 📥 Admin / Export Section (ADD THIS AT THE END)
# -----------------------------
st.subheader("📥 Export All Responses (Admin Use)")

if st.button("Download All Responses as CSV"):
    try:
        # Fetch all documents from Firestore
        docs = db.collection("aptitude_results").stream()
        data = []
        for doc in docs:
            d = doc.to_dict()
            data.append(d)

        # Convert to DataFrame and offer as CSV
        if data:
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
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
