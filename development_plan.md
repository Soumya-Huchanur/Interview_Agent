# Development Plan for Interview Agent

## Project Overview
The Interview Agent will be a web-based application that automates job interview processes. It will:
- Generate personalized interview questions based on a job description and candidate profile
- Conduct text-based interviews by asking questions sequentially
- Evaluate candidate responses using AI scoring and provide feedback
- Store interview sessions and evaluations for later review

The agent focuses on HR efficiency by reducing manual interview scheduling and initial screening efforts.

## Core Features
1. **Job Description Input**: Users (HR interviewers) can paste job descriptions to generate relevant questions
2. **Candidate Profile Setup**: Basic info input (name, experience, skills) for personalization
3. **Question Generation**: AI-powered creation of 5-8 technical and behavioral questions
4. **Interactive Interview**: Text-based Q&A interface with real-time question progression
5. **Response Evaluation**: Automated scoring of answers with criteria like relevance, detail, and job-fit (1-5 scale)
6. **Feedback Summary**: AI-generated summary report with recommendations (hire/interview again/pass)
7. **Session Persistence**: Store completed interviews in a database for review

Note: No audio/video integration to keep scope manageable for 48 hours. No Google Calendar API needed as scheduling isn't core to Q&A evaluation.

## Technical Architecture
```
User (HR/Interviewer)
    ↓
Streamlit Frontend
    ↓
Python Backend Logic
    ↓
Gemini API (via Google Generative AI SDK)
    ↓
Firebase Database
    ↓
Store Interview Sessions & Evaluations
```

Components:
- **Frontend**: Streamlit web app for interview interface
- **Backend**: Python scripts for AI processing and database interactions
- **AI Layer**: Integration with Gemini API for question generation and evaluation
- **Database**: Firebase for storing interview data
- **Hosting**: Streamlit Cloud for deployment

## Tech Stack Selection
Based on preferences and suitability:
- **UI/Frontend**: Streamlit (Python-based web app framework for rapid development and prototyping)
- **Backend**: Python (for AI logic, API integrations, and backend processing)
- **AI Models**: Gemini (via Google's Generative AI Python SDK for natural language generation and evaluation)
- **Database**: Firebase (easy-to-setup NoSQL via python-firebase-admin; from allowed options)
- **Other Tools**: None from advanced frameworks (LangChain/CrewAI not needed for simple chaining; LlamaIndex if expanding)
- **APIs**: None additional required (Google Calendar skipped as not core)
- **Vector DB**: None needed for this scope (could use ChromaDB if implementing resume-based personalization later)

## Development Plan & Timeline (48 Hours)
**Phase 1: Setup & Infrastructure (Hours 1-8)**
- Set up Python virtual environment and install dependencies (streamlit, firebase-admin, google-generativeai)
- Set up Firebase project and configure database schema
- Obtain Google AI API key and test basic Gemini calls in Python
- Set up Git repository and initial README

**Phase 2: Core AI Integration (Hours 9-24)**
- Implement question generation logic using Gemini (prompt engineering for different question types)
- Add response evaluation function with scoring criteria
- Create sequential question-answering flow
- Integrate Gemini API calls in Python scripts

**Phase 3: Frontend Development (Hours 25-36)**
- Build Streamlit interface: forms for job description input, question display, answer submission
- Add logic for dynamic UI updates and backend integrations
- Implement interview flow: start → questions → evaluation → summary
- Style the Streamlit app for professional look

**Phase 4: Database & Backend Integration (Hours 37-44)**
- Implement Firebase integration in Python for storing interview sessions
- Add data persistence: save candidate info, questions, responses, scores
- Ensure data retrieval for viewing past interviews

**Phase 5: Testing & Polish (Hours 45-48)**
- Test end-to-end interview flow
- Add error handling and input validation
- Create demo script and final README with setup instructions
- Deploy to Streamlit Cloud for demo link

## Required Resources & Setup
- Google Cloud Console: Enable Generative AI API, get API key (~15 min setup)
- Firebase Console: Create project, enable Firestore (~10 min)
- Python Environment: Install Python, set up virtual env, pip install requirements
- GitHub: Create public repo for submission
- Hosting: Use Streamlit Cloud (free for demos, Python-based)

## Potential Challenges & Mitigations
- Gemini API rate limits: Implement retry logic and user feedback
- API costs: Test with minimal calls; Gemini has generous free tier
- Time constraints: Focus on MVP (core Q&A flow); add features like resume upload if time allows
- Security: Store API keys securely (use environment variables); do not hardcode in code
- Dependencies: Ensure virtual environment is set up correctly to avoid version conflicts

## Submission Deliverables
- **Demo Link**: Hosted Streamlit app on Streamlit Cloud
- **Git Repository**: Complete source code with Python scripts
- **README**: Overview, features, techstack, setup instructions (including pip install), improvements
- **Architecture Diagram**: Simple diagram as described above
