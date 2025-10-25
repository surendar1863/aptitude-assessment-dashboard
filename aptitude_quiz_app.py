import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

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
    
    result = {"Name": name, "Roll": roll, "Score": score, "Total": len(questions_df)}
    
    # Authorize with Google Sheets
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = gspread.authorize(creds)

    # Open your Google Sheet by name or URL
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1mEHO0N4lF1O_DrJVVpronS9x_iF8Y66Sg7V7nLv6Tx0/edit?usp=sharing").sheet1  # 👈 paste your sheet link here

    # Append data to the next row
    sheet.append_row(list(result.values()))

    st.success("✅ Your responses have been submitted successfully!")




