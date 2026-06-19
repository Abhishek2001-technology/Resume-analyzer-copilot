# Resume Analyzer Co-Pilot

**Resume Analyzer Co-Pilot is a web application built with Flask to help users evaluate their resumes against a target role. It extracts text from uploaded resumes, generates structured AI-based feedback, highlights skill gaps, suggests a learning roadmap, and produces targeted interview questions. The application also includes user authentication and stores past analysis results for progress tracking.**

## 🚀 Features

- **User Authentication:** Secure user signup, login, and logout capabilities.
- **Document Parsing:** Automatically reads and extracts text from uploaded PDF and DOCX resumes.
- **AI-Powered Evaluation:** Generates structured feedback tailored to the user's target role.
- **Structured Insights:** Evaluates the resume and outputs:
  - Relevant skills extracted for the specific role
  - Genuine missing skills (skill gaps)
  - A tailored learning roadmap for missing areas
  - Targeted interview questions
- **Analysis History:** Saves past resume analyses to a database so users can track their progress over time.

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** TiDB (MySQL compatible) using SQLAlchemy and PyMySQL
- **AI & LLM:** Google Generative AI (via LangChain)
- **Frontend:** HTML/CSS with Jinja2 templates
- **Document Processing:** PyPDF2, python-docx

## 📋 Prerequisites

To run this project, install the required dependencies listed in `requirements.txt`:

- Flask
- SQLAlchemy
- PyMySQL
- python-dotenv
- langchain-google-genai
- PyPDF2
- python-docx

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/resume-analyzer-copilot.git
   cd resume-analyzer-copilot
   ```