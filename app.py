from flask import Flask, render_template, request
import fitz  # PyMuPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
        return 0
    return round(len(common) / len(jd_words) * 100, 2), len(common), len(jd_words)

def get_match_skills(resume_text, jd_text):
    resume_words = set(resume_text.split())
    jd_words = set(jd_text.split())
    common = list(resume_words.intersection(jd_words))
    return common

@app.route("/", methods=["GET", "POST"])
def index():
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

            return render_template("index.html", match=match_percent, common=common_count, total=jd_total, skills=common_skills)
    return render_template("index.html", match=None)

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
