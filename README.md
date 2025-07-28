 SkillVerse: AI-Powered Resume Matcher
SkillVerse is a smart resume vs job description (JD) matcher built using Python and Flask. It calculates the match percentage between your resume and job description, highlights matched keywords, suggests missing skills, and allows PDF download of the report — all with a clean UI and pie chart visualization.

 Live Demo
👉 https://skillverse-exc0.onrender.com

Features
✅ Upload Resume & JD (PDF)
✅ Match % Calculation
✅ Matched Keywords Highlight
✅ Skills Suggestions to Improve Match
✅ Pie Chart Visualization (Chart.js)
✅ Download PDF Report
✅ Mobile-Responsive Design (TailwindCSS)
✅ Hosted Live on Render

Technologies Used
Python (Flask)
PyMuPDF (fitz)
Chart.js
TailwindCSS
xhtml2pdf
HTML5 + Jinja2 Templates
Render.com (Hosting)

Screenshots

 1. Upload Page
[Upload Page](screenshots/upload.png)

 2. Match Result Page
[Result Page](screenshots/result.png)

How to Run Locally
1.Clone the Repo
git clone https://github.com/your-username/skillverse.git
cd skillverse

2.(Optional) Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux

3.Install Requirements
pip install -r requirements.txt

4.Run the App
python app.py

5.Go to
http://localhost:5000

Folder Structure
skillverse/
│
├── templates/
│   ├── index.html
│   └── report.html
│
├── static/
│   └── style.css
│
├── screenshots/
│   ├── upload.png
│   └── result.png
│
├── uploads/ ← auto-created
├── app.py
├── requirements.txt
├── Procfile
└── README.md

Credits
Project built by [KAGITALA SAMEER] – Inspired by real-world HR tech needs.
Drop a ⭐ if you find it helpful!

