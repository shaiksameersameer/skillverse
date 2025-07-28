from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF
import os
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Global variables for PDF report
global_match = 0
global_common = 0
global_total = 0
global_skills = []
global_missing = []

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
    common = list(resume_words.intersection(jd_words))
    return common

def get_missing_skills(resume_text, jd_text):
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    missing = list(jd_words - resume_words)
    return missing[:5]  # Only top 5 suggestions

@app.route("/", methods=["GET", "POST"])
def index():
    global global_match, global_common, global_total, global_skills, global_missing

    if request.method == "POST":
        resume = request.files["resume"]
        jd = request.files["jd"]
        if resume and jd:
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], "resume.pdf")
            jd_path = os.path.join(app.config["UPLOAD_FOLDER"], "jd.pdf")
            resume.save(resume_path)
            jd.save(jd_path)

            resume_text = extract_text_from_pdf(resume_path)
            jd_text = extract_text_from_pdf(jd_path)

            match_percent, common_count, jd_total = get_match_percent(resume_text, jd_text)
            common_skills = get_match_skills(resume_text, jd_text)
            missing_skills = get_missing_skills(resume_text, jd_text)

            # Save global values for PDF
            global_match = match_percent
            global_common = common_count
            global_total = jd_total
            global_skills = common_skills
            global_missing = missing_skills

            return render_template("index.html",
                                   match=match_percent,
                                   common=common_count,
                                   total=jd_total,
                                   skills=common_skills,
                                   missing=missing_skills)
    return render_template("index.html", match=None)

@app.route("/download_report")
def download_report():
    html = render_template("report.html", match=global_match, common=global_common,
                           total=global_total, skills=global_skills, missing=global_missing)
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=pdf)
    pdf.seek(0)
    return send_file(pdf, download_name="match_report.pdf", as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
