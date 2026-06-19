from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import Base, engine, Session_local
from ai import analyze_resume
import models
import PyPDF2
import docx
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

Base.metadata.create_all(bind=engine)


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = Session_local()
    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            existing_user = db.query(models.User).filter_by(email=email).first()
            if existing_user:
                return "User already exists"

            hashed_password = generate_password_hash(password)
            user = models.User(email=email, password=hashed_password)
            db.add(user)
            db.commit()

            return redirect(url_for("login"))

        return render_template("signup.html")
    finally:
        db.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    db = Session_local()
    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = db.query(models.User).filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                session["user"] = user.email
                return redirect(url_for("dashboard"))

            return "Invalid Credentials"

        return render_template("login.html")
    finally:
        db.close()


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role", "").strip()
        resume_text = request.form.get("resume", "").strip()
        file = request.files.get("file")

        if file and file.filename:
            filename = file.filename.lower()

            if filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text.strip()
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}

            elif filename.endswith(".docx"):
                try:
                    docx_reader = docx.Document(file)
                    text = ""
                    for para in docx_reader.paragraphs:
                        text += para.text + "\n"
                    resume_text = text.strip()
                except Exception as e:
                    result = {"error": f"DOCX error: {str(e)}"}

            else:
                result = {"error": "Only PDF and DOCX files are supported."}

        if not resume_text and not result:
            result = {"error": "Please paste resume text or upload a file."}

        if not user_goal and not result:
            result = {"error": "Please enter your target role."}

        if resume_text and user_goal and not result:
            try:
                result = analyze_resume(resume_text, user_goal)

                db = Session_local()
                try:
                    user = db.query(models.User).filter_by(email=session["user"]).first()

                    report = models.Report(
                        user_id=user.id,
                        resume_text=resume_text,
                        result=json.dumps(result)
                    )
                    db.add(report)
                    db.commit()
                finally:
                    db.close()

            except Exception as e:
                result = {"error": str(e)}

    return render_template("dashboard.html", result=result, user=session["user"])


@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    db = Session_local()
    try:
        user = db.query(models.User).filter_by(email=session["user"]).first()
        if not user:
            session.pop("user", None)
            return redirect(url_for("login"))

        reports = db.query(models.Report).filter_by(user_id=user.id).all()

        parsed_reports = []
        for r in reports:
            try:
                parsed_result = json.loads(r.result)
            except Exception:
                parsed_result = {}

            parsed_reports.append({
                "resume_text": r.resume_text,
                "result": parsed_result
            })

        return render_template("history.html", reports=parsed_reports, user=session["user"])
    finally:
        db.close()


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        return f"Reset link logic pending for: {email}"
    return render_template("forgot.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)