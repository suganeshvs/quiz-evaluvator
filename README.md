# AI Quiz Analyzer in Google Classroom

A web application designed for educational environments. The platform enables teachers to share PDF/PPT learning materials with students, tracks student reading progress in real time, allows students to confirm their precise reading boundary (Page, Paragraph, Line), and generates Multiple Choice Questions (MCQs) **strictly** from the confirmed portion of the material.

> **IMPORTANT**: The Quick Quiz feature is **NOT** a Google Classroom assignment. It is an on-demand self-assessment tool associated with each document via a prominent rectangular **`[ QUICK QUIZ ]`** button in the Document Viewer.

---

## Key Features

1. **Teacher Dashboard & Material Management**:
   - Create and manage Google Classroom classes (e.g. `10A`, Subject: `Science`, Code: `SCI10A`).
   - Upload PDF, PPT, and PPTX documents.
   - Automatic backend text extraction, paragraph/line structuring, and diagram/image analysis.
   - View student activity, reading progress, and quiz performance reports.

2. **Student Document Reader & Real-Time Progress Tracking**:
   - Interactive document reader with page navigation and zoom/read controls.
   - Auto-tracks reading progress (highest page reached, time spent per page, coverage percentage).
   - Top-right prominent rectangular **`[ QUICK QUIZ ]`** button on every document view.

3. **Reading Progress Confirmation & Strict Content Boundary**:
   - Confirmation screen when clicking `[ QUICK QUIZ ]`.
   - Auto-detects progress (e.g., Page 5 of 20).
   - Allows students to confirm or select a more granular cutoff:
     - **Entire Page** (e.g. Page 5)
     - **Paragraph** (e.g. Page 5, Paragraph 2)
     - **Line** (e.g. Page 5, Paragraph 2, Line 3)
   - **STRICT INVARIANT**: The AI engine will **NEVER** generate questions from pages or text beyond the student's confirmed boundary.

4. **Dynamic AI MCQ Engine & Mock AI Fallback**:
   - Modular AI service supporting LLM APIs (OpenAI GPT-4o-mini / Gemini) and built-in **`MOCK_AI`** mode.
   - Operates 100% offline out-of-the-box without requiring external API keys.
   - Generates 4-option MCQs with source page tags, explanations, and visual diagram questions.

5. **Unlimited Questions & Accurate Scoring**:
   - Students can answer as many questions as they wish.
   - Clicking **`[ END QUIZ ]`** calculates score strictly on **attempted questions** (e.g., 14 correct / 18 attempted = 77.78%). Score is NOT calculated out of total document pages or total generated bank.
   - Full Quiz Attempt History logging for student review.

---

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, Google Fonts (Outfit).
- **Backend**: Python 3, Django 6.x.
- **Database**: SQLite3 (Development & Demonstration).
- **Document Processing**: `pypdf`, `python-pptx`, `Pillow`.
- **AI Integration**: Modular `AIService` (`OpenAI`, `Gemini`, or `MockAIService`).

---

## Quick Automated 1-Click Setup (Recommended for New Machines)

Double-click **`install_and_run.bat`** (or run `.\setup_installer.ps1` in PowerShell).

This installer will automatically:
1. Create Python virtual environment (`venv`).
2. Install all Python dependencies from `requirements.txt`.
3. Run database migrations & seed demo data.
4. Auto-install Ollama (`irm https://ollama.com/install.ps1 | iex`).
5. Pull the `llama3.2:1b` model (`ollama pull llama3.2:1b`).
6. Launch the server at `http://127.0.0.1:8000/` and open your browser automatically.

---

## Manual Installation & Setup

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Setup Virtual Environment & Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Migrations & Seed Demo Data
```bash
python manage.py migrate
python manage.py seed_demo
```

### 4. Start Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to: `http://127.0.0.1:8000/`

---

## Demo Credentials & Scenario

### Seeded Credentials
- **Teacher Account**:
  - Username: `teacher1`
  - Password: `password123`
- **Student Account**:
  - Username: `student1`
  - Password: `password123`

---

### Step-by-Step Demonstration Scenario

1. **Teacher Upload**:
   - Log in as `teacher1`.
   - View Class `10A` (Subject: `Science`, Code: `SCI10A`).
   - Upload `Light_Chapter_1.pdf` (20 Pages).
   - System automatically extracts pages, text, paragraphs, and visual diagram information.

2. **Student Reading & Progress**:
   - Log in as `student1`.
   - Open `Light_Chapter_1.pdf`.
   - Read through Pages 1, 2, 3, 4, and 5.
   - Reading tracker logs: *"Highest page reached: Page 5 of 20 (25%)"*.

3. **Click Quick Quiz**:
   - Click the prominent top-right rectangular **`[ QUICK QUIZ ]`** button.

4. **Confirm Progress Cutoff**:
   - Confirmation screen displays: *"Detected reading progress: Page 5 of 20"*.
   - Confirm Page 5, Paragraph 2, Line 3.

5. **Take Unlimited Quiz**:
   - AI generates MCQs strictly from Pages 1-5 up to Paragraph 2, Line 3.
   - Answer 18 questions.
   - Click **`[ END QUIZ ]`**.

6. **View Score Report & History**:
   - Summary displays:
     - Questions Attempted: 18
     - Correct: 14 | Wrong: 4
     - Score: `14/18`
     - Percentage: `77.78%`
     - Reading Boundary: Page 5, Paragraph 2, Line 3
   - Attempt saved in Quiz History.

---

## AI Service Configuration & Mock AI Mode

The application operates in `MOCK_AI = True` mode by default in `ai_quiz_analyzer/settings.py`.

To use OpenAI or Gemini APIs:
1. Edit `ai_quiz_analyzer/settings.py` or set environment variables:
   ```python
   MOCK_AI = False
   OPENAI_API_KEY = "your-openai-api-key"
   ```
2. The system automatically switches to LLM API generation while maintaining strict reading boundary enforcement.

---

## Running Automated Test Suite

To run all automated tests (covering authentication, class creation, document analysis, reading progress, content boundary enforcement, score calculation, and history):

```bash
python manage.py test quiz_app
```
