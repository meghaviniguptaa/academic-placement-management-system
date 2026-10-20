# Placement Cell – Frontend

Plain HTML/CSS/JavaScript (no build step) for the Academic Placement Management System.
It talks to the Flask backend in `../Backend` and has three portals:

| Role      | Login page             | Portal        | What it does |
|-----------|------------------------|---------------|--------------|
| Student   | `login-student.html`   | `/student/`   | Dashboard, browse/search open jobs & apply, my applications, interview rounds/results, offers, edit profile |
| Recruiter | `login-recruiter.html` | `/recruiter/` | Dashboard, review applications & change status, manage drives, jobs, interview rounds, offers, company profile |
| Admin     | `login-admin.html`     | `/admin/`     | Full CRUD for students, companies, drives, jobs, rounds, applications, interview results, offers and user accounts |

`index.html` is a landing page linking to the three logins.

## Run it

1. Start the backend (Python 3.12, see the root Readme):
   `cd Backend && python app.py`  → http://127.0.0.1:5000
2. Start the frontend server (standard library only):
   `cd Frontend && python server.py`  → http://127.0.0.1:8080

`server.py` serves the pages and proxies `/api/*` to Flask, so the session cookie stays
same-origin and the backend needs no CORS changes. Use `PORT=3000 BACKEND_URL=http://host:5000 python server.py` to change ports.

## Try it without Oracle

`python dev/mock_backend.py` starts a stand-in API on :5000 with the same routes and sample data.
Logins: `admin / AdminTest@123`, `aarav_student / StudentTest@123`, `technova_hr / RecruiterTest@123`.

## Settings (`js/config.js`)

- `API_BASE`: leave empty when using `server.py`.
- `PLAIN_DATE_STYLE`: `"oracle"` (20-OCT-2026) or `"iso"` (2026-10-20) – how drive/job dates are sent,
  because the backend binds those two as plain strings. Switch to `"iso"` if your DB session uses YYYY-MM-DD.

## Notes

- Oracle returns column names in UPPERCASE; `js/api.js` maps them back to the schema spelling.
- Each portal checks `/api/auth/me` and redirects to the right login when the session is missing or the role is wrong.
