import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
# from src.mcqgenerator.utils import read_file,get_table_data,clean_quiz
# from src.mcqgenerator.logger import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough 
from langchain_core.output_parsers import StrOutputParser

from langchain_core.globals import set_debug
import certifi

# Fixes the missing SSL certificate bundle error on Windows
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()
set_debug(True)

key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model=os.getenv("MODEL")

errors = []
if not key:
    errors.append("API_KEY is required: copy .env.example and fill the key")

if not base_url:
    errors.append("BASE_URL is required")
if not model:
    errors.append("MODEL is required")
if errors:
    raise ValueError("\n".join(errors))

llm = ChatOpenAI(api_key=key,base_url=base_url,model="gemini-3.5-flash-lite",temperature=0.5)

template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text","number","subject","tone","response_json"],template=template
)

quiz_chain = RunnablePassthrough.assign(quiz=quiz_generation_prompt | llm | StrOutputParser())

template2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity.
If the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the students abilities \
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

review_generation_prompt = PromptTemplate(input_variables=["subject","quiz"],template=template2)

review_chain = RunnablePassthrough.assign(review=review_generation_prompt | llm | StrOutputParser())

generate_evaluate_chain = quiz_chain | review_chain

