from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF
import os
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Define technical, soft, and tool-based skills
TECH_SKILLS = [
    'python', 'java', 'c', 'c++', 'javascript', 'typescript',
    'html', 'css', 'react', 'angular', 'vue', 'flask', 'django',
    'mysql', 'postgresql', 'mongodb', 'sqlite', 'rest', 'api',
    'docker', 'git', 'github', 'fastapi', 'node', 'express'
]

SOFT_SKILLS = [
    'communication', 'leadership', 'teamwork', 'creativity',
    'adaptability', 'problem-solving', 'time management'
]

TOOLS_SKILLS = [
    'excel', 'tableau', 'powerbi', 'figma', 'canva',
    'jupyter', 'vscode', 'postman', 'jira', 'notion'
]

ALL_SKILLS = TECH_SKILLS + SOFT_SKILLS + TOOLS_SKILLS

# For global report data
global_data = {
    "match": 0,
    "common": 0,
    "total": 0,
    "skills": {},
    "missing": {},
    "unmatched": {},
    "tips": [],
    "ats_score": 0,
    "resume_role": "",
    "jd_role": ""
}


def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()


def detect_role(text):
    text = text.lower()
    roles = {
        "frontend developer": ["html", "css", "javascript", "react", "vue", "frontend"],
        "backend developer": ["flask", "django", "api", "sql", "backend", "fastapi"],
        "full stack developer": ["full stack", "frontend", "backend", "javascript", "flask", "django"],
        "python developer": ["python", "flask", "django"],
        "java developer": ["java", "spring", "hibernate"],
        "data scientist": ["machine learning", "pandas", "numpy", "scikit", "model", "predictive", "ml"],
        "data analyst": ["excel", "visualization", "tableau", "powerbi", "sql", "pandas"],
        "software tester": ["manual testing", "automation", "selenium", "test case"],
        "ui/ux designer": ["figma", "wireframe", "prototype", "ux", "ui"],
        "cloud engineer": ["aws", "azure", "gcp", "devops", "infrastructure", "docker", "kubernetes"],
        "devops engineer": ["docker", "kubernetes", "ci/cd", "jenkins", "pipeline", "github actions"]
    }

    scores = {role: sum(word in text for word in keywords) for role, keywords in roles.items()}
    best_match = max(scores, key=scores.get)
    return best_match.title() if scores[best_match] > 0 else "General Software Developer"


def get_skills_by_category(text_words):
    categorized = {
        "Technical": [s for s in TECH_SKILLS if s in text_words],
        "Soft": [s for s in SOFT_SKILLS if s in text_words],
        "Tools": [s for s in TOOLS_SKILLS if s in text_words]
    }
    return categorized


def get_missing_skills(jd_words, resume_words):
    categorized = {
        "Technical": [s for s in TECH_SKILLS if s in jd_words and s not in resume_words],
        "Soft": [s for s in SOFT_SKILLS if s in jd_words and s not in resume_words],
        "Tools": [s for s in TOOLS_SKILLS if s in jd_words and s not in resume_words]
    }
    return categorized


def get_unmatched_skills(jd_words, resume_words):
    return {
        "Technical": [s for s in TECH_SKILLS if s not in jd_words and s in resume_words],
        "Soft": [s for s in SOFT_SKILLS if s not in jd_words and s in resume_words],
        "Tools": [s for s in TOOLS_SKILLS if s not in jd_words and s in resume_words]
    }


def get_match_percent(resume_words, jd_words):
    common = resume_words.intersection(jd_words)
    total = len(jd_words)
    match = round(len(common) / total * 100, 2) if total > 0 else 0
    return match, len(common), total


def get_resume_tips(missing, ats_score):
    tips = []

    if ats_score < 60:
        tips.append("Improve your resume formatting. Avoid tables, graphics, and use standard fonts.")

    if any(missing.values()):
        tips.append("Add more skills from the job description to increase match %.")

    if len(missing["Technical"]) >= 3:
        tips.append("Consider learning the top missing technical skills to align better with this role.")

    return tips


def calculate_ats_score(text):
    score = 100
    if "table" in text:
        score -= 30
    if "graphic" in text or "image" in text:
        score -= 20
    if "header" in text or "footer" in text:
        score -= 10
    return max(score, 0)


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

            resume_words = set(resume_text.split())
            jd_words = set(jd_text.split())

            match, common, total = get_match_percent(resume_words, jd_words)
            matched = get_skills_by_category(resume_words.intersection(jd_words))
            missing = get_missing_skills(jd_words, resume_words)
            unmatched = get_unmatched_skills(jd_words, resume_words)

            ats_score = calculate_ats_score(resume_text)
            tips = get_resume_tips(missing, ats_score)

            resume_role = detect_role(resume_text)
            jd_role = detect_role(jd_text)

            global_data.update({
                "match": match,
                "common": common,
                "total": total,
                "skills": matched,
                "missing": missing,
                "unmatched": unmatched,
                "tips": tips,
                "ats_score": ats_score,
                "resume_role": resume_role,
                "jd_role": jd_role
            })

            return render_template("index.html", **global_data)

    return render_template("index.html", match=None)


@app.route("/download_report")
def download_report():
    html = render_template("report.html", **global_data)
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=pdf)
    pdf.seek(0)
    return send_file(pdf, download_name="match_report.pdf", as_attachment=True)


if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
