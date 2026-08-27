# Group AI Mini Hackathon — Facilitation Guide
### Plan → Prompt → Review → Ship | 2–3 Hour Session

---

## 1. Team Role Allocation & Hackathon Schedule

Assign these four roles before touching a keyboard. Every member drives the AI assistant during their cycle — no single "prompt driver" for the whole session.

| Role | Owns | Deliverables |
|---|---|---|
| **Product & Prompt Lead** | Scope & Specification | Writes `SPEC.md`, crafts the prompts for each cycle, enforces MVP boundaries (says "no" to scope creep) |
| **Backend & AI Engineer** | API & Model Logic | Drives Cursor/Claude for FastAPI routes and the LLM integration |
| **Frontend & UX Lead** | Interface | Builds the Streamlit UI, wires it to backend endpoints |
| **QA & Git Lead** (4th member) | Testing & Hygiene | Owns commits, `.gitignore`, edge-case testing, final README |

If your team only has 3 members, the Product & Prompt Lead absorbs QA & Git duties.

### Schedule (2.5 hr target — compress proportionally if you only have 2 hr)

| Time | Block |
|---|---|
| 0:00–0:15 | Ideation lock-in + role assignment (use the idea below to skip debate) |
| 0:15–0:35 | Phase 1 — Repo init + `SPEC.md` |
| 0:35–1:35 | Phase 2 — Cycles 1–4 (15 min each, **timebox strictly**) |
| 1:35–1:55 | Phase 3 — Defensive code review |
| 1:55–2:15 | Phase 4 — README + demo prep |
| 2:15–2:30 | Live demo to instructor |

**Rule:** if a cycle overruns 15 minutes, stop, commit what works, and move on. A working 80% beats a broken 100%.

---

## 2. Project Idea & MVP Scope

To save your Ideation slot, here's a project that's genuinely buildable in the timebox, uses every required library (`fastapi`, `streamlit`, `google-genai`, `python-dotenv`), and is portfolio-worthy — a real recruiter can understand what it does in one glance.

### **QuickQuiz AI** — paste any text, get a summary and an auto-generated quiz

**Problem statement:** Students and self-learners paste long articles or notes into ChatGPT to "understand" them, but reading a summary alone doesn't confirm retention. QuickQuiz AI turns any block of text into (1) a concise summary and (2) a short multiple-choice quiz, so the user immediately tests whether they absorbed it.

**MVP scope — exactly 3 features, nothing else:**
1. Text input with validation (reject empty input, cap length e.g. 8,000 chars)
2. `/summarize` endpoint — LLM returns a 3–4 sentence summary
3. `/quiz` endpoint — LLM returns 3 structured MCQs (question, 4 options, correct answer index), validated with Pydantic

**Explicitly out of scope for this session:** file/PDF upload, user accounts, quiz scoring history, multiple languages. Write these under a "Future Work" heading in the README — don't build them.

### `SPEC.md` template

```markdown
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
```

---

## 3. Step-by-Step Prompt Cycles (Cycles 1–4)

Each cycle is **15 minutes, timeboxed**. The Product & Prompt Lead reads the prompt aloud (or pastes it) to the AI assistant; the assigned driver reviews every line before accepting.

### Cycle 1 — Architecture Setup (Backend & AI Engineer drives)
```
Set up a FastAPI project skeleton for "QuickQuiz AI".
Requirements:
- Folder structure: /backend (main.py, requirements.txt), /frontend (app.py), .env.example, .gitignore
- requirements.txt: fastapi, uvicorn, google-genai, python-dotenv, pydantic, requests
- .gitignore must exclude .env, __pycache__/, .venv/
- main.py: basic FastAPI app with a GET /health endpoint returning {"status": "ok"}
- Load GEMINI_API_KEY from .env using python-dotenv but do NOT hardcode any key
Do not implement any LLM logic yet — just the skeleton.
```
**Checkpoint before moving on:** `.env` is in `.gitignore`. Run `git status` — `.env` must NOT appear as trackable.

### Cycle 2 — Core LLM Logic & Validation (Backend & AI Engineer drives)
```
In main.py, add two endpoints using Pydantic models for request/response validation:

1. POST /summarize
   - Request body: { "text": str } (reject if empty or > 8000 chars, return 422)
   - Calls Gemini via google-genai to produce a 3-4 sentence summary
   - Response: { "summary": str }

2. POST /quiz
   - Request body: { "text": str } (same validation)
   - Calls Gemini and returns exactly 3 multiple-choice questions
   - Response model: { "questions": [ { "question": str, "options": list[str] (len 4), "correct_index": int } ] }
   - Prompt Gemini to return strict JSON so you can parse it into the Pydantic model; handle parse failures with a 502 error, not a crash.

Wrap the Gemini call in a try/except and return a clean 500 error with a message if the API call fails.
```
**Checkpoint:** test both endpoints with `curl` or the FastAPI `/docs` Swagger UI before moving to frontend.

### Cycle 3 — Streamlit UI (Frontend & UX Lead drives)
```
Build frontend/app.py in Streamlit:
- Text area for pasting input text
- Two buttons: "Summarize" and "Generate Quiz"
- On click, POST to BACKEND_URL (from .env) /summarize or /quiz using requests
- Display the summary as plain text
- Display quiz questions as st.radio widgets showing the 4 options, with a "Check Answer" button that reveals whether the selection matches correct_index
- Add a loading spinner (st.spinner) while waiting on the API call
```
**Checkpoint:** manually click through the happy path once — paste real text, get a real summary and quiz.

### Cycle 4 — Defensive UI/UX Error Handling (QA & Git Lead + Frontend drive together)
```
Harden frontend/app.py and backend/main.py for these failure cases:
1. Empty text submitted -> Streamlit shows a clear warning, does not call the API
2. Backend unreachable (connection error) -> Streamlit shows "Backend is not responding, please check the server" instead of a raw traceback
3. Gemini API failure or malformed JSON response -> backend returns a clean error message, frontend displays it instead of crashing
4. Oversized input (>8000 chars) -> truncate with a warning, or reject with a clear message, don't silently fail
Add a loading state and disable the buttons while a request is in-flight to prevent double-submission.
```
**Checkpoint:** actually trigger each of these 4 failure cases and confirm nothing throws a raw stack trace to the user.

---

## 4. Pre-Flight Security & Quality Verification Checklist

Run through this **before** declaring the app done. QA & Git Lead owns sign-off.

- [ ] **Secret Leak Audit** — `.env` is listed in `.gitignore`; run `git log --all -p | grep -i "api_key"` and confirm nothing returns. Only `.env.example` (with placeholder values) is committed.
- [ ] **Happy Path Test** — paste a real article, click Summarize then Generate Quiz, confirm end-to-end flow completes with no console errors.
- [ ] **Edge Case Test** — test: empty input, whitespace-only input, an 8,000+ character paste, and a rapid double-click on the submit button.
- [ ] **Diff Audit** — every team member can explain, in one sentence each, what every AI-generated function does. If someone can't explain a function, that's a sign to re-review it, not skip it.
- [ ] **Dependency sanity** — `pip install -r requirements.txt` works cleanly in a fresh virtual environment.
- [ ] **No dead code** — remove any commented-out AI-generated attempts that didn't make the final cut.

---

## 5. Final Delivery & Presentation

### README.md must include
- **Title & one-line description** of QuickQuiz AI
- **Screenshot or short GIF** of the app in action
- **Setup instructions**, copy-pasteable:
  ```bash
  git clone <repo-url>
  cd quickquiz-ai
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env   # then fill in your GEMINI_API_KEY
  uvicorn backend.main:app --reload
  streamlit run frontend/app.py
  ```
- **Tech stack** list
- **Future Work** section (the features you deliberately cut, from the SPEC)

### 2-Minute Live Demo Structure
1. **(15s)** State the problem in one sentence — no one confirms they understood what they read.
2. **(60s)** Live demo: paste a real article, show the summary, show the quiz, answer a question live.
3. **(30s)** Show one deliberate failure case handled gracefully (e.g., empty input warning) — this is what proves defensive engineering, not just a happy-path demo.
4. **(15s)** Name one thing the team would build next (from Future Work) and one thing they learned about AI pair-programming discipline.

---

**Instructor note for teams:** the grade in this lab isn't "did the app work" — it's whether your team can explain every line an AI wrote and whether your git history shows disciplined, incremental commits rather than one giant dump at the end. Commit after every cycle.
