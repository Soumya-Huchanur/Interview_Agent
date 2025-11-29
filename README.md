# Interview Agent

A web-based application that automates job interview processes using AI to generate questions, conduct interviews, and evaluate responses.

## Features

- Personalized question generation based on job descriptions and candidate profiles
- Text-based interview interface with sequential Q&A
- AI-powered response evaluation with scoring (1-5 scale)
- Automated feedback summary with hire recommendations
- Data persistence for reviewing past interviews

## Tech Stack

- **Frontend/UI**: Streamlit (Python-based web app framework)
- **Backend**: Python scripts for AI processing and database interactions
- **AI Models**: Google Gemini API for question generation and evaluation
- **Database**: Firebase Firestore for storing interview data
- **Hosting**: Streamlit Cloud (recommended for deployment)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Interview_Agent
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   call venv\Scripts\activate.bat  # On Windows
   # Or activate venv in your terminal
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your actual API keys and credentials:
     - `GEMINI_API_KEY`: Obtain from Google AI Studio
     - `FIREBASE_CREDENTIALS_JSON`: Copy the full JSON content from your Firebase service account key (download from Firebase Console > Project Settings > Service Accounts > Generate new private key). Note: Put the entire JSON on one line in the .env file to avoid parsing errors.

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   - Open the provided local URL in your browser

## Usage

1. Enter job description in the text area
2. Provide candidate profile (name, experience, skills)
3. Click "Generate Questions" to create personalized questions
4. Conduct the interview by answering questions one by one
5. View evaluation for each answer
6. Review overall summary and hire recommendation
7. Interviews are automatically saved to Firebase if configured

## Deployment

- **Streamlit Cloud:**
  - Fork/clone to GitHub
  - Connect GitHub to Streamlit Cloud
  - Set environment variables in Streamlit Cloud secrets
  - Deploy

- **Other options:** Heroku, AWS, etc., but requires slightly different setup.

## Architecture

- Built with Python for both frontend (Streamlit) and backend logic
- Uses Google Gemini for AI-powered question generation and evaluations
- Stores data in Firebase Firestore
- No audio/video - focused on text-based interviewing

## Improvements

- Add resume parsing for better personalization
- Implement audio/video integration if requirements change
- Add more advanced evaluation metrics
- Include scheduling with Google Calendar API
- Support multiple interviewers/roles

## Contributing

Feel free to submit issues or pull requests for improvements.

## License

This project is for demonstration purposes.
