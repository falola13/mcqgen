import os
import json
import traceback
import pandas as pd
import re
from dotenv import load_dotenv
from src.mcqgenerator.utils import get_table_data, read_file, clean_quiz
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

if "quiz_df" not in st.session_state:
    st.session_state.quiz_df = pd.DataFrame()
if "last_subject" not in st.session_state:
    st.session_state.last_subject = ""
if "last_count" not in st.session_state:
    st.session_state.last_count = 3
if "last_tone" not in st.session_state:
    st.session_state.last_tone = ""
if "review_text" not in st.session_state:
    st.session_state.review_text = ""
if "token_count" not in st.session_state:
    st.session_state.token_count = 0

file_path = r"C:\Users\PRECISION\Desktop\Projects\mcqgen\Response.json"
with open(file_path, 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQs Creator Application with LangChain 🕊️ ⛓️")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or txt file")
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity Level of Questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain.invoke(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error during generation")
            else:
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        cleaned_quiz_str = clean_quiz(quiz)
                        table_data = get_table_data(cleaned_quiz_str)

                        if table_data:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1

                            
                            st.session_state.quiz_df = df
                            st.session_state.last_subject = subject
                            st.session_state.last_count = mcq_count
                            st.session_state.last_tone = tone
                            st.session_state.review_text = response.get("review", "")
                            st.session_state.token_count = cb.total_tokens
                        else:
                            st.error("Error: The model failed to return valid JSON for the quiz table. Please try generating again.")
                    else:
                        st.error("No quiz found in the response")
                else:
                    st.write(response)

# --- 2. DISPLAY RESULTS & DOWNLOAD BUTTONS ---
if not st.session_state.quiz_df.empty:
    st.divider()
    st.subheader("Generated Quiz")
    st.table(st.session_state.quiz_df)
    
    st.text_area(label="Review", value=st.session_state.review_text)
    st.text(f"Total Tokens: {st.session_state.token_count}")
    
    st.subheader("📥 Export Quiz")
    
    raw_name = f"{st.session_state.last_count} {st.session_state.last_tone} MCQs on {st.session_state.last_subject}"
    safe_name = sanitize_filename(raw_name)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = st.session_state.quiz_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"{safe_name}.csv",
            mime="text/csv",
            icon="📊"
        )
        
    with col2:
        json_data = st.session_state.quiz_df.to_json(orient="index", indent=4)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name=f"{safe_name}.json",
            mime="application/json",
            icon="📁"
        )