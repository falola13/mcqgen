import os
import PyPDF2
import json
import traceback


def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            file.seek(0)
            pdf_reader=PyPDF2.PdfReader(file)          
            text=""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text+=extracted + "\n"
            if not text.strip():
                raise Exception("This PDF appears to be a scanned image. Please upload a PDF with selectable text.")
            
            return text
        except Exception as e:
           raise Exception(f"Error reading the PDF file: {str(e)}")
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        raise Exception(
            "unsupported file format: only pdf and text file supported"
        )

def get_table_data(quiz_str):
    try:
        quiz_dict=json.loads(quiz_str)
        quiz_table_data=[]

        for key,value in quiz_dict.items():
            mcq = value["mcq"]
            options=" || ".join(
                [
                    f"{option} -> {option_value}" 
                    for option,option_value in value["options"].items()
                ]
            )

            correct = value["correct"]
            quiz_table_data.append({"MCQ":mcq, "Choices":options,"Correct": correct})
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e),e,e.__traceback__)
        return None


def clean_quiz(quiz):

    try:
        start = quiz.index('{')
        end = quiz.rindex('}') + 1
        return quiz[start:end]
    except ValueError:
        cleaned_quiz = quiz.strip()
        if cleaned_quiz.startswith("```json"):
            cleaned_quiz=cleaned_quiz[7:]
        elif cleaned_quiz.startswith("```"):
            cleaned_quiz = cleaned_quiz[3:]

        if cleaned_quiz.endswith("```"):
            cleaned_quiz = cleaned_quiz[:-3]

        
        
        return cleaned_quiz.strip()

def convert_for_download(df):
    return df.to_csv().encode("utf-8")