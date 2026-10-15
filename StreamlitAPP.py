import os
import json
import traceback
import pandas as pd
import certifi
from dotenv import load_dotenv
from src.mcqgenerator.utils import get_table_data,read_file,clean_quiz
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

os.environ["SSL_CERT_FILE"] = certifi.where()
file_path = r"C:\Users\PRECISION\Desktop\Projects\mcqgen\Response.json"
with open(file_path,'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQs Creator Application with LangChain 🕊️ ⛓️")

# Create a form using st.form
with st.form("user_inputs"):
    uploaded_file=st.file_uploader("Upload a PDF or txt file")

    mcq_count = st.number_input("No. of MCQs", min_value=3,max_value=50)

    subject=st.text_input("Insert Subject",max_chars=20)

    tone=st.text_input("Complexity Level of Questions",max_chars=20,placeholder="Simple")

    button=st.form_submit_button("Create MCQs")

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
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")
            else:
                print(f" Total Tokens: {cb.total_tokens}")
                print(f" Prompt Tokens: {cb.prompt_tokens}")
                print(f" Completion Tokens: {cb.completion_tokens}")
                print(f" Total Cost: {cb.total_cost}")
                if isinstance(response,dict):
                    quiz = response.get("quiz",None)
                    raw_quiz = response["quiz"]
                    quiz_dict = clean_quiz(raw_quiz)
                    if quiz is not None:
                        table_data = get_table_data(quiz_dict)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index +1
                            st.table(df)
                            st.text_area(label="Review", value=response["review"])
                            
                            st.text(f"Total Tokens: {cb.total_tokens}")
                        else:
                            st.error("Error in the table data")

                else:
                    st.write(response)