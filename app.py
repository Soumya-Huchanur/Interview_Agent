import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables (local use only)
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"])

# ---------------------------------------------
# Initialize Firebase safely
# ---------------------------------------------
firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON") or st.secrets["FIREBASE_CREDENTIALS_JSON"]

try:
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        db = firestore.client()
    else:
        db = None
except Exception as e:
    st.warning(f"Firebase initialization error: {e}")
    db = None


# ---------------------------------------------
# Session State Initialization
# ---------------------------------------------
default_values = {
    "step": 0,
    "job_description": "",
    "candidate_profile": {},
    "questions": [],
    "answers": [],
    "evaluations": [],
    "answer_input": ""  # <-- important for clearing answer box
}

for k, v in default_values.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------
# Generate Questions
# ---------------------------------------------
def generate_questions(job_desc, candidate_profile):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Based on the job description and candidate profile below, generate 5-8 interview questions.

    Job Description: {job_desc}
    Candidate Profile: {candidate_profile}

    Number them like:
    1. ...
    2. ...
    """

    try:
        response = model.generate_content(prompt)
        questions = re.findall(r'\d+\.\s*(.+)', response.text)
        return [q.strip() for q in questions][:8]
    except:
        return []


# ---------------------------------------------
# Evaluate Answer (JSON structured format)
# ---------------------------------------------
def evaluate_answer(question, answer):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Evaluate the following answer strictly in JSON format:

    {{
      "score": <1-5 integer>,
      "assessment": "<40-word summary>",
      "fit": "<Poor/Fair/Good/Excellent>"
    }}

    Question: {question}
    Answer: {answer}
    """

    try:
        response = model.generate_content(prompt).text
        json_match = re.search(r"\{.*\}", response, re.DOTALL)

        if json_match:
            return json.loads(json_match.group())

        return {"score": 0, "assessment": "Invalid output", "fit": "Poor"}

    except:
        return {"score": 0, "assessment": "Error in evaluation", "fit": "Poor"}


# ---------------------------------------------
# Step 1 — Job Description
# ---------------------------------------------
def step_job_description():
    st.header("Step 1: Job Description")

    jd = st.text_area("Paste job description:", st.session_state.job_description, height=250)

    if st.button("Next"):
        if jd.strip():
            st.session_state.job_description = jd
            st.session_state.step = 1
            st.rerun()
        else:
            st.error("Job description cannot be empty.")


# ---------------------------------------------
# Step 2 — Candidate Profile
# ---------------------------------------------
def step_candidate_profile():
    st.header("Step 2: Candidate Profile")

    name = st.text_input("Candidate Name")
    exp = st.text_area("Experience")
    skills = st.text_area("Skills")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.step = 0
            st.rerun()

    with col2:
        if st.button("Generate Questions"):
            if name.strip() and skills.strip():
                st.session_state.candidate_profile = {
                    "name": name,
                    "experience": exp,
                    "skills": skills
                }
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Name & skills are required.")


# ---------------------------------------------
# Step 3 — Generate Questions
# ---------------------------------------------
def step_generate_questions():
    st.header("Step 3: Generate Interview Questions")

    if st.button("Generate"):
        with st.spinner("Generating..."):
            qs = generate_questions(
                st.session_state.job_description,
                st.session_state.candidate_profile
            )

        if qs:
            st.session_state.questions = qs
            st.session_state.step = 3
            st.rerun()
        else:
            st.error("Could not generate questions.")

    if st.session_state.questions:
        st.subheader("Generated Questions")
        for i, q in enumerate(st.session_state.questions):
            st.write(f"**{i+1}. {q}**")

    if st.button("Back"):
        st.session_state.step = 1
        st.rerun()


# ---------------------------------------------
# Step 4 — Conduct Interview (WITH answer clearing)
# ---------------------------------------------
def step_conduct_interview():
    st.header("Step 4: Interview")

    questions = st.session_state.questions
    answered = len(st.session_state.answers)

    st.progress(answered / len(questions))

    if answered < len(questions):
        q = questions[answered]

        st.subheader(f"Question {answered + 1}")
        st.info(q)

        # Always show a fresh empty text_area
        answer = st.text_area(
            "Your Answer",
            value="",            # <-- answer box always empty
            key=f"answer_box_{answered}"
        )

        if st.button("Submit Answer"):
            if answer.strip():
                with st.spinner("Evaluating..."):
                    evaluation = evaluate_answer(q, answer)

                st.session_state.answers.append(answer)
                st.session_state.evaluations.append(evaluation)

                st.rerun()
            else:
                st.error("Answer cannot be empty.")

    else:
        st.success("All questions answered!")
        if st.button("View Summary"):
            st.session_state.step = 4
            st.rerun()

    if st.button("Back"):
        st.session_state.step = 2
        st.rerun()


# ---------------------------------------------
# Step 5 — Summary + AI Recommendation
# ---------------------------------------------
def step_interview_summary():
    st.header("Step 5: Interview Summary")

    scores = [e["score"] for e in st.session_state.evaluations]
    avg = sum(scores) / len(scores)

    if avg >= 4.5:
        verdict = "Strong Hire"
    elif avg >= 3.5:
        verdict = "Hire"
    elif avg >= 2.5:
        verdict = "Needs Improvement"
    else:
        verdict = "Not Suitable"

    st.write(f"### Average Score: **{avg:.2f} / 5**")
    st.write(f"### Final Hiring Decision: **{verdict}**")

    summary_prompt = f"""
    Generate a detailed interview summary for {st.session_state.candidate_profile['name']}.

    Average Score: {avg:.2f}
    Hiring Verdict: {verdict}

    Include:
    - Strengths
    - Weaknesses
    - Areas for Improvement
    - Final Verdict Explanation
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        summary = model.generate_content(summary_prompt).text
    except:
        summary = "Summary generation failed."

    st.subheader("AI Summary")
    st.write(summary)

    if st.button("Restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ---------------------------------------------
# Main App Controller
# ---------------------------------------------
def main():
    st.title("Interview Agent")

    steps = [
        step_job_description,
        step_candidate_profile,
        step_generate_questions,
        step_conduct_interview,
        step_interview_summary
    ]

    steps[st.session_state.step]()


if __name__ == "__main__":
    main()
