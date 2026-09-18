# Gradually AI

**This project became [lifeOS](https://github.com/bryan-lolordo/lifeos).**

Gradually was a personal AI habit-tracking platform: you told it your
baseline routine, it generated each day's schedule, you logged what you
actually did and when, and it proposed adjustments to the routine based
on your record. The pitch, in its own words from the mobile app's
manifest: *"A habit-tracking app with AI-powered adjustments."*

Work here ran from **February 9 to February 18, 2025** (the four commits
below this one). The idea kept going, and widened: instead of an app that
helps someone improve habits, an assistant that understands the whole day
and helps them run it. Habits became routines and check-ins, the daily
schedule became an agenda, adjustments became proposals the person
confirms. That continuation is lifeOS, whose repository begins in August
2026. The lineage, and why the dates matter, is written up in
[`docs/LINEAGE.md`](https://github.com/bryan-lolordo/lifeos/blob/main/docs/LINEAGE.md)
there.

This repository is kept as it was. Nothing below this README has been
changed since February 2025, on purpose: the history is the record.

One more piece exists off `main`: the branch
[`march-2025-frontend`](https://github.com/bryan-lolordo/gradually_ai/tree/march-2025-frontend)
holds the work from **February 28 to March 2, 2025**, uncommitted until
September 2026. It restructures the backend into packages, drops
`crewai_dev/`, and adds a React + Vite + TypeScript `frontend/`. That is
the last thing built as Gradually before it became lifeOS.

## What is here

| Folder | What it is |
|---|---|
| `backend/` | A FastAPI service over SQLAlchemy (`DATABASE_URL` from `.env`). Users with a stored timezone; a baseline schedule; a generated daily schedule that keeps the previous time beside the new one and records when a task was actually completed; task logging; and endpoints that return AI habit adjustments and record the user's response to each. |
| `crewai_dev/` | A CrewAI crew of five agents (code analyzer, optimization engineer, habit analyst, security, API extender) that read `backend/api.py` and `backend/models.py` and propose improvements to the habit-scheduling logic. An early experiment in having agents build the product. |
| `mobile/` | A Flutter app with four screens: Today's Improvements, Upcoming Tasks, Daily Agenda, Calendar. |

Two ideas from here survived unchanged into lifeOS: a completion is
recorded with the time it actually happened, and a suggested change is
something the person answers, not something applied to them.

## Running it

It was a personal prototype and was never packaged. The backend expects a
`.env` with `DATABASE_URL`; the crew expects `OPENAI_API_KEY`; the mobile
app is a standard Flutter project. No support is offered and none is
intended.

MIT licence, as it was.

---

*README added September 18, 2026. Everything else is February 2025.*
