from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- FRONTEND ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

frontend_path = os.path.join(
    BASE_DIR,
    "..",
    "frontend"
)

@app.get("/")
def serve_frontend():
    file_path = os.path.join(frontend_path, "index.html")

    if os.path.exists(file_path):
        return FileResponse(file_path)

    return {
        "error": "Frontend file not found"
    }
# ---------------- LOAD MODEL ----------------
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

resume_text = ""

# ---------------- UPLOAD ----------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global resume_text

    try:
        text = ""

        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()

                if content:
                    text += content

        resume_text = text

        return {
            "message": "Resume Uploaded"
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# ---------------- MATCH ----------------
@app.post("/match")
def match(data: dict = Body(...)):
    global resume_text

    try:
        if resume_text.strip() == "":
            return {
                "error": "Upload resume first"
            }

        jd = data.get("job_description", "")

        if jd.strip() == "":
            return {
                "error": "Enter job description"
            }

        resume_emb = model.encode(resume_text)
        jd_emb = model.encode(jd)

        score = cosine_similarity(
            [resume_emb],
            [jd_emb]
        )[0][0]

        return {
            "score": float(round(score * 100, 2))
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# ---------------- EVALUATE ----------------
@app.post("/evaluate")
def evaluate(data: dict = Body(...)):
    try:
        answer = data.get("answer", "")

        if answer.strip() == "":
            return {
                "error": "Enter answer"
            }

        ideal = "Machine learning is a method where systems learn from data."

        user_emb = model.encode(answer)
        ideal_emb = model.encode(ideal)

        score = cosine_similarity(
            [user_emb],
            [ideal_emb]
        )[0][0]

        if score > 0.8:
            result = "Excellent"
        elif score > 0.6:
            result = "Good"
        else:
            result = "Needs Improvement"

        return {
            "score": float(round(score * 10, 2)),
            "result": result
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# ---------------- ATS SCORE ----------------
@app.post("/ats-score")
def ats_score(data: dict = Body(...)):
    global resume_text

    try:
        jd = data.get(
            "job_description",
            ""
        ).lower()

        if resume_text.strip() == "":
            return {
                "error": "Upload resume first"
            }

        resume_lower = resume_text.lower()

        skills = [
            "react",
            "node",
            "express",
            "mongodb",
            "python",
            "java",
            "sql",
            "aws",
            "docker",
            "kubernetes",
            "machine learning",
            "deep learning",
            "html",
            "css",
            "javascript",
            "api",
            "git"
        ]

        match_count = 0
        total = 0

        for skill in skills:
            if skill in jd:
                total += 1

                if skill in resume_lower:
                    match_count += 1

        # Skill Score (60%)
        skill_score = (
            match_count / total * 60
        ) if total > 0 else 0

        # Resume Length Score (20%)
        length_score = (
            20 if len(resume_text) > 500
            else 10
        )

        # Keyword Bonus (20%)
        keyword_score = (
            20 if any(
                word in resume_lower
                for word in [
                    "project",
                    "experience",
                    "internship"
                ]
            )
            else 10
        )

        final_score = round(
            skill_score +
            length_score +
            keyword_score,
            2
        )

        suggestions = []

        if match_count < total:
            suggestions.append(
                "Add missing skills from job description"
            )

        if len(resume_text) < 500:
            suggestions.append(
                "Increase resume content (add projects/experience)"
            )

        if "project" not in resume_lower:
            suggestions.append(
                "Add project section"
            )

        if "experience" not in resume_lower:
            suggestions.append(
                "Add experience or internship"
            )

        return {
            "ats_score": final_score,
            "matched_skills": match_count,
            "total_skills": total,
            "suggestions": (
                suggestions
                if suggestions
                else ["Your resume is strong!"]
            )
        }

    except Exception as e:
        return {
            "error": str(e)
        }