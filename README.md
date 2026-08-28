# QuickQuiz AI

Paste any topic or article, get an instant summary and a self-test quiz — built for students and self-learners who want to confirm they actually understood what they read.

![QuickQuiz AI Demo](docs/demo-screenshot.png)
> *Replace this with an actual screenshot or GIF of the app in action before final submission.*

---

## 🚀 Problem It Solves

Self-learners often paste long articles or notes into an AI chatbot to "understand" them — but reading a summary alone doesn't confirm retention. **QuickQuiz AI** turns any block of text into:
1. A concise, easy-to-understand summary
2. A short multiple-choice quiz generated from that same text

...so the user can immediately test whether they actually absorbed the material.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Pydantic |
| LLM | google-genai (Gemini) |
| Frontend | Streamlit |
| Env Management | python-dotenv |
| HTTP Client (Frontend → Backend) | requests |

---

## ⚙️ Setup Instructions

```bash
git clone <repo-url>
cd quickquiz-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your GEMINI_API_KEY
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

Once both servers are running, open the Streamlit URL shown in your terminal (usually `http://localhost:8501`) to use the app.

---

## ✨ Features (MVP Scope)

1. **Text input with validation** — rejects empty input, caps length at 8,000 characters
2. **`POST /summarize`** — returns a 3–4 sentence summary of the pasted text
3. **`POST /quiz`** — returns 3 structured multiple-choice questions (question, 4 options, correct answer index) based on the same text
4. **`POST /eval-quiz`** — Evaluates the answers of these multiple-choice questions,

---

## 🧪 How to Test It

Try pasting a real article or a topic explanation (science, history, tech — anything) into the text area, click **Summarize**, then **Generate Quiz**, and answer the questions to see if you understood the material.

---

## 🔒 Security & Quality Notes

- `.env` is excluded via `.gitignore` — no API keys are committed to this repository
- Only `.env.example` (with placeholder values) is tracked in git
- Edge cases handled: empty input, oversized input (>8,000 chars), backend downtime, malformed LLM responses

---

## 🔮 Future Work

The following features were deliberately scoped out of this session to keep the MVP achievable within the timebox:

- File / PDF upload support
- User accounts & authentication
- Quiz history & scoring persistence across sessions
- Multi-language support

---

## 👥 Team & Roles

| Role | Responsibility |
|---|---|
| Product & Prompt Lead | Scope, `SPEC.md`, prompt design |
| Backend & AI Engineer | FastAPI routes, LLM integration |
| Frontend & UX Lead | Streamlit interface |
| QA & Git Lead | Testing, git hygiene, this README |
