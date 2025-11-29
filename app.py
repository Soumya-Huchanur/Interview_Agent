import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import json
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Firebase (if credentials are provided)
firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
if firebase_creds_json:
    try:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.warning(f"Firebase initialization error: {e}. Database features disabled.")
        db = None
else:
    db = None  # No DB if not configured

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'candidate_profile' not in st.session_state:
    st.session_state.candidate_profile = {}
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []
if 'interview_id' not in st.session_state:
    st.session_state.interview_id = None

# Functions
def generate_questions(job_desc, candidate_profile):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Based on the job description: {job_desc}\n and candidate profile: {candidate_profile}\n Generate 5-8 technical and behavioral interview questions. Number them as 1. , 2. , etc."
    try:
        response = model.generate_content(prompt)
        # Extract questions starting with numbers like 1. , 2. , etc.
        questions = re.findall(r'\d+\.\s*(.+)', response.text)
        questions = [q.strip() for q in questions if q.strip()][:8]
        return questions
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

def evaluate_answer(question, answer):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Evaluate this answer to the question '{question}': {answer}\n Provide a score 1-5, relevance, detail, job-fit on a 1-5 scale. Give feedback."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error evaluating answer: {e}")
        return "Error in evaluation."

def save_to_db(interview_data):
    if db:
        try:
            doc_ref = db.collection('interviews').document()
            doc_ref.set(interview_data)
            st.session_state.interview_id = doc_ref.id
            st.success("Interview saved successfully!")
        except Exception as e:
            st.error(f"Error saving to database: {e}")
    else:
        st.warning("Database not configured. Interview data not saved.")

# UI
def main():
    st.title("Interview Agent")

    if st.session_state.step == 0:
        st.header("Step 1: Job Description")
        job_desc = st.text_area("Paste the job description:", st.session_state.job_description, height=200)
        if st.button("Next"):
            st.session_state.job_description = job_desc
            st.session_state.step = 1
            st.rerun()

    elif st.session_state.step == 1:
        st.header("Step 2: Candidate Profile")
        name = st.text_input("Candidate Name:")
        experience = st.text_area("Experience (brief):")
        skills = st.text_area("Skills:")
        if st.button("Next"):
            st.session_state.candidate_profile = {"name": name, "experience": experience, "skills": skills}
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        st.header("Step 3: Generate Questions")
        if st.button("Generate Questions"):
            questions = generate_questions(st.session_state.job_description, st.session_state.candidate_profile)
            st.session_state.questions = questions
            st.session_state.step = 3
            st.rerun()
        if st.session_state.questions:
            st.subheader("Generated Questions:")
            for i, q in enumerate(st.session_state.questions):
                st.write(f"{i+1}. {q}")

    elif st.session_state.step == 3:
        st.header("Step 4: Conduct Interview")
        if len(st.session_state.questions) == 0:
            st.error("No questions were generated. Please go back to Step 3 and try generating questions again.")
            if st.button("Go Back"):
                st.session_state.step = 2
                st.rerun()
        elif len(st.session_state.answers) < len(st.session_state.questions):
            current_q_index = len(st.session_state.answers)
            q = st.session_state.questions[current_q_index]
            st.subheader(f"Question {current_q_index + 1}: {q}")
            answer = st.text_area("Your Answer:", key=f"answer_{current_q_index}")
            if st.button("Submit Answer"):
                st.session_state.answers.append(answer)
                evaluation = evaluate_answer(q, answer)
                st.session_state.evaluations.append(evaluation)
                st.success("Answer submitted!")
                st.rerun()
        else:
            st.success("All questions answered!")
            if st.button("View Summary"):
                st.session_state.step = 4
                st.rerun()

    elif st.session_state.step == 4:
        st.header("Step 5: Interview Summary")
        total_score = 0
        for i, (q, a, e) in enumerate(zip(st.session_state.questions, st.session_state.answers, st.session_state.evaluations)):
            st.subheader(f"Question {i+1}")
            st.write(f"**Q:** {q}")
            st.write(f"**A:** {a}")
            st.write(f"**Evaluation:** {e}")
            # Extract score if possible, for simplicity, assume average
            # total_score += float(e.split('score')[1].split('/')[0]) or something, but simple

        # Generate summary feedback
        summary_prompt = f"Overall interview summary for candidate {st.session_state.candidate_profile}. Questions: {st.session_state.questions}\nAnswers: {st.session_state.answers}\nEvaluations: {st.session_state.evaluations}\n Provide hire recommendation."
        model = genai.GenerativeModel('gemini-2.5-flash')
        try:
            summary_response = model.generate_content(summary_prompt)
            st.subheader("AI Summary and Recommendation")
            st.write(summary_response.text)
            summary_text = summary_response.text
        except Exception as e:
            st.error(f"Error generating summary: {e}")
            summary_text = ""

        interview_data = {
            "job_description": st.session_state.job_description,
            "candidate_profile": st.session_state.candidate_profile,
            "questions": st.session_state.questions,
            "answers": st.session_state.answers,
            "evaluations": st.session_state.evaluations,
            "summary": summary_text
        }
        save_to_db(interview_data)

        if st.button("Restart Interview"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
