import streamlit as st
import pandas as pd
import os

st.title("Aptitude Test Assessment")

name = st.text_input("Enter your name")
roll = st.text_input("Enter your roll number")

# Load questions from CSV
questions_df = pd.read_csv("aptitude_questions.csv")

st.subheader("Answer the following:")

score = 0
for i, row in questions_df.iterrows():
    q = row["Question"]
    options = [row["Option1"], row["Option2"], row["Option3"], row["Option4"]]
    correct = row["Correct"]
    ans = st.radio(f"{i+1}. {q}", options, key=i)
    if ans == correct:
        score += 1

if st.button("Submit"):
if st.button("Submit"):
    
    # Prepare the result dictionary
    result = {
        "Name": name,
        "Roll": roll,
        "Score": score,
        "Total": len(questions_df)
    }

    # ✅ Save to Google Sheet instead of local CSV
    import gspread

    try:
        # Connect to Google Sheets using Streamlit Secrets
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open("aptitude_results")  # your Google Sheet name
        worksheet = sh.sheet1

        # Append the student's record
        worksheet.append_row([name, roll, score, len(questions_df)])

        st.success("✅ Result submitted successfully to cloud!")
    except Exception as e:
        st.error(f"⚠️ Error saving to Google Sheet: {e}")


