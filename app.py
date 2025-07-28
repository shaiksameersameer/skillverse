from flask import Flask, render_template, request, send_file, session
import fitz  # PyMuPDF
import os
import pdfkit
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Needed for session usage
app.secret_key = "skillverse-secret"

# wkhtmltopdf path setup (update if your path is different)
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# ----------------- Utility Functions -----------------
def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()

def get_match_percent(resume_text, jd_text):
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    common = resume_words.intersection(jd_words)
    if len(jd_words) == 0:
        return 0, 0, 0
    return round(len(common) / len(jd_words) * 100, 2), len(common), len(jd_words)

def get_match_skills(resume_text, jd_text):
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    return list(resume_words.intersection(jd_words))

def get_missing_skills(resume_text, jd_text):
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    return list(jd_words - resume_words)[:5]

# ----------------- Main Routes -----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume = request.files["resume"]
        jd = request.files["jd"]
        if resume and jd:
            if not os.path.exists("uploads"):
                os.makedirs("uploads")

            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], "resume.pdf")
            jd_path = os.path.join(app.config["UPLOAD_FOLDER"], "jd.pdf")
            resume.save(resume_path)
            jd.save(jd_path)

            resume_text = extract_text_from_pdf(resume_path)
            jd_text = extract_text_from_pdf(jd_path)

            match_percent, common_count, jd_total = get_match_percent(resume_text, jd_text)
            common_skills = get_match_skills(resume_text, jd_text)
            missing_skills = get_missing_skills(resume_text, jd_text)

            # Save data in session for report download
            session["report_data"] = {
                "match": match_percent,
                "common": common_count,
                "total": jd_total,
                "skills": common_skills,
                "missing": missing_skills
            }

            return render_template("index.html",
                                   match=match_percent,
                                   common=common_count,
                                   total=jd_total,
                                   skills=common_skills,
                                   missing=missing_skills)

    return render_template("index.html", match=None)

@app.route("/download_report")
def download_report():
    data = session.get("report_data")
    if not data:
        return "No report data found. Please upload resume and JD again.", 400

    html = render_template("report.html",
                           match=data["match"],
                           common=data["common"],
                           total=data["total"],
                           skills=data["skills"],
                           missing=data["missing"])

    pdf = pdfkit.from_string(html, False, configuration=PDFKIT_CONFIG)
    return send_file(BytesIO(pdf), download_name="match_report.pdf", as_attachment=True)

# ----------------- Run App -----------------
if __name__ == "__main__":
    app.run(debug=True)
