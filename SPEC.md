# QuickQuiz AI — SPEC.md

## Problem Statement
Who: students/self-learners processing long text (articles, notes, docs).
Friction: reading a summary doesn't confirm understanding — no quick self-check exists.
Solution: paste text -> get a summary + a 3-question quiz to self-test.

## MVP Scope (strictly 2–3 features)
1. Text input with validation (non-empty, <= 8000 chars)
2. POST /summarize -> returns { "summary": str }
3. POST /quiz -> returns { "questions": [ { "question": str, "options": [str,str,str,str], "correct_index": int } ] }

## Tech Stack
- Backend: FastAPI + Pydantic
- LLM: google-genai (Gemini)
- Frontend: Streamlit
- Env management: python-dotenv
- HTTP client (Streamlit -> FastAPI): requests

## Environment Setup (.env.example)
GEMINI_API_KEY=your_key_here
BACKEND_URL=http://localhost:8000

## Out of Scope (Future Work)
- File/PDF upload
- User accounts / auth
- Quiz history & scoring persistence
- Multi-language support

## Success Criteria
- Team can paste an article and get back a real summary + quiz in <10s
- No crashes on empty input or 8000+ char input
- Zero secrets committed to git