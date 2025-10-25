import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # We'll fix this in Step 3
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("🧠 Aptitude Quiz")

name = st.text_input("Enter your name")
roll = st.text_input("Enter your Roll No")

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

if st.button("Submit"):
    total = len(questions)
    doc_ref = db.collection("responses").document(roll)
    doc_ref.set({
        "Name": name,
        "Roll": roll,
        "Score": score,
        "Total": total
    })
    st.success(f"✅ Your response has been recorded! Score: {score}/{total}")
