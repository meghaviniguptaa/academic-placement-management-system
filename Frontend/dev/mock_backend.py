#!/usr/bin/env python3
"""
OPTIONAL: an in-memory stand-in for the Flask + Oracle backend.

It mimics the real API (same routes, roles, messages, uppercase column names,
RFC-822 dates) and starts with the same data as Database/insert_data.sql, so
you can try the frontend without the database running.

    python dev/mock_backend.py            # listens on 127.0.0.1:5000
    python server.py                      # in another terminal, then open :8080

Demo logins (same as your test accounts):
    admin          / AdminTest@123
    aarav_student  / StudentTest@123
    technova_hr    / RecruiterTest@123

Environment:
    MOCK_TODAY=YYYY-MM-DD    pretend today is this date (default: real date)
    MOCK_DATE_STYLE=oracle   drives/jobs dates must look like 20-OCT-2026 (default)
    MOCK_DATE_STYLE=iso      drives/jobs dates must look like 2026-10-20
Data is reset every time the process starts.
"""
import json
import os
import re
import secrets
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

PORT = int(os.environ.get("MOCK_PORT", "5000"))
TODAY = date.fromisoformat(os.environ["MOCK_TODAY"]) if os.environ.get("MOCK_TODAY") else date.today()
DATE_STYLE = os.environ.get("MOCK_DATE_STYLE", "oracle")
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# ---------------------------------------------------------------- data
DB = {
    "students": [
        dict(Student_ID=101, Name="Aarav Sharma", Email="aarav.sharma@gmail.com", Phone="9876543210", Department="Computer Science", CGPA=8.75, Graduation_Year=2027, Resume_URL="https://resume.example/aarav"),
        dict(Student_ID=102, Name="Ananya Mehta", Email="ananya.mehta@gmail.com", Phone="9876543211", Department="Information Technology", CGPA=9.10, Graduation_Year=2027, Resume_URL="https://resume.example/ananya"),
        dict(Student_ID=103, Name="Rohan Verma", Email="rohan.verma@gmail.com", Phone="9876543212", Department="Computer Science", CGPA=7.85, Graduation_Year=2027, Resume_URL="https://resume.example/rohan"),
        dict(Student_ID=104, Name="Ishita Rao", Email="ishita.rao@gmail.com", Phone="9876543213", Department="Electronics", CGPA=8.45, Graduation_Year=2026, Resume_URL="https://resume.example/ishita"),
        dict(Student_ID=105, Name="Kabir Singh", Email="kabir.singh@gmail.com", Phone="9876543214", Department="Computer Science", CGPA=9.35, Graduation_Year=2026, Resume_URL="https://resume.example/kabir"),
    ],
    "companies": [
        dict(Company_ID=201, Company_Name="TechNova Solutions", Industry="Information Technology", Contact_Email="hr@technova.com", HR_Name="Priya Nair", Location="Bangalore"),
        dict(Company_ID=202, Company_Name="FinEdge Technologies", Industry="FinTech", Contact_Email="careers@finedge.com", HR_Name="Rahul Kapoor", Location="Mumbai"),
        dict(Company_ID=203, Company_Name="CloudMatrix Systems", Industry="Cloud Computing", Contact_Email="hr@cloudmatrix.com", HR_Name="Sneha Iyer", Location="Hyderabad"),
        dict(Company_ID=204, Company_Name="DataSphere Analytics", Industry="Data Analytics", Contact_Email="hr@datasphere.com", HR_Name="Neha Sharma", Location="Pune"),
        dict(Company_ID=205, Company_Name="InnovateX Labs", Industry="Software", Contact_Email="careers@innovatex.com", HR_Name="Arjun Malhotra", Location="Chennai"),
    ],
    "drives": [
        dict(Drive_ID=301, Company_ID=201, Drive_Date="2026-10-15", Venue="Main Auditorium", Drive_Status="UPCOMING"),
        dict(Drive_ID=302, Company_ID=202, Drive_Date="2026-10-20", Venue="Placement Hall", Drive_Status="UPCOMING"),
        dict(Drive_ID=303, Company_ID=203, Drive_Date="2026-09-20", Venue="Tech Block", Drive_Status="COMPLETED"),
        dict(Drive_ID=304, Company_ID=204, Drive_Date="2026-11-05", Venue="Main Auditorium", Drive_Status="UPCOMING"),
        dict(Drive_ID=305, Company_ID=205, Drive_Date="2026-11-15", Venue="Placement Hall", Drive_Status="UPCOMING"),
    ],
    "jobs": [
        dict(Job_ID=401, Drive_ID=301, Job_Title="Software Engineer", Role_Description="Develop and maintain software applications.", Package_LPA=12.5, Min_CGPA_Requirement=8.0, Application_Deadline="2026-10-10"),
        dict(Job_ID=402, Drive_ID=302, Job_Title="FinTech Developer", Role_Description="Build software solutions for financial applications.", Package_LPA=13.0, Min_CGPA_Requirement=8.5, Application_Deadline="2026-10-15"),
        dict(Job_ID=403, Drive_ID=303, Job_Title="Cloud Engineer", Role_Description="Design and maintain cloud infrastructure.", Package_LPA=14.0, Min_CGPA_Requirement=8.5, Application_Deadline="2026-09-10"),
        dict(Job_ID=404, Drive_ID=304, Job_Title="Data Analyst", Role_Description="Analyze business data and generate insights.", Package_LPA=9.0, Min_CGPA_Requirement=7.5, Application_Deadline="2026-10-30"),
        dict(Job_ID=405, Drive_ID=305, Job_Title="Backend Developer", Role_Description="Develop REST APIs and backend services.", Package_LPA=11.0, Min_CGPA_Requirement=8.0, Application_Deadline="2026-11-10"),
    ],
    "applications": [
        dict(Application_ID=501, Student_ID=101, Job_ID=401, Application_Date="2026-10-01", Status="SHORTLISTED"),
        dict(Application_ID=502, Student_ID=102, Job_ID=401, Application_Date="2026-10-01", Status="SELECTED"),
        dict(Application_ID=503, Student_ID=103, Job_ID=404, Application_Date="2026-10-02", Status="REJECTED"),
        dict(Application_ID=504, Student_ID=104, Job_ID=402, Application_Date="2026-10-03", Status="SHORTLISTED"),
        dict(Application_ID=505, Student_ID=105, Job_ID=403, Application_Date="2026-10-01", Status="SELECTED"),
        dict(Application_ID=506, Student_ID=101, Job_ID=404, Application_Date="2026-10-03", Status="APPLIED"),
        dict(Application_ID=507, Student_ID=102, Job_ID=405, Application_Date="2026-10-04", Status="APPLIED"),
        dict(Application_ID=508, Student_ID=105, Job_ID=401, Application_Date="2026-10-02", Status="SHORTLISTED"),
    ],
    "rounds": [
        dict(Round_ID=601, Job_ID=401, Round_Number=0, Round_Type="Online Assessment"),
        dict(Round_ID=602, Job_ID=401, Round_Number=1, Round_Type="Technical Interview"),
        dict(Round_ID=603, Job_ID=402, Round_Number=0, Round_Type="Aptitude Test"),
        dict(Round_ID=604, Job_ID=402, Round_Number=1, Round_Type="Technical Interview"),
        dict(Round_ID=605, Job_ID=403, Round_Number=0, Round_Type="Coding Test"),
    ],
    "results": [
        dict(Round_ID=601, Application_ID=501, Result="PASSED"),
        dict(Round_ID=602, Application_ID=501, Result="PASSED"),
        dict(Round_ID=601, Application_ID=502, Result="PASSED"),
        dict(Round_ID=602, Application_ID=502, Result="PASSED"),
        dict(Round_ID=603, Application_ID=504, Result="PASSED"),
    ],
    "offers": [
        dict(Offer_ID=701, Application_ID=502, Offer_Date="2026-10-25", Offered_Package_LPA=12.5, Offer_Status="ACCEPTED"),
        dict(Offer_ID=702, Application_ID=505, Offer_Date="2026-10-28", Offered_Package_LPA=14.0, Offer_Status="PENDING"),
        dict(Offer_ID=703, Application_ID=508, Offer_Date="2026-10-30", Offered_Package_LPA=12.5, Offer_Status="PENDING"),
        dict(Offer_ID=704, Application_ID=501, Offer_Date="2026-10-27", Offered_Package_LPA=12.5, Offer_Status="REJECTED"),
        dict(Offer_ID=705, Application_ID=504, Offer_Date="2026-10-29", Offered_Package_LPA=13.0, Offer_Status="PENDING"),
    ],
    "users": [
        dict(User_ID=801, Username="aarav_student", Password="StudentTest@123", Role="STUDENT", Student_ID=101, Company_ID=None),
        dict(User_ID=802, Username="ananya_student", Password="StudentTest@123", Role="STUDENT", Student_ID=102, Company_ID=None),
        dict(User_ID=803, Username="technova_hr", Password="RecruiterTest@123", Role="RECRUITER", Student_ID=None, Company_ID=201),
        dict(User_ID=804, Username="finedge_hr", Password="RecruiterTest@123", Role="RECRUITER", Student_ID=None, Company_ID=202),
        dict(User_ID=805, Username="admin", Password="AdminTest@123", Role="ADMIN", Student_ID=None, Company_ID=None),
    ],
}
PK = {"students": ("Student_ID",), "companies": ("Company_ID",), "drives": ("Drive_ID",), "jobs": ("Job_ID",), "applications": ("Application_ID",),
      "rounds": ("Round_ID",), "results": ("Round_ID", "Application_ID"), "offers": ("Offer_ID",), "users": ("User_ID",)}
UNIQUE = {"students": [("Email",)], "companies": [("Contact_Email",)], "applications": [("Student_ID", "Job_ID")],
          "rounds": [("Job_ID", "Round_Number")], "offers": [("Application_ID",)], "users": [("Username",)]}
FK = {"drives": [("Company_ID", "companies")], "jobs": [("Drive_ID", "drives")], "applications": [("Student_ID", "students"), ("Job_ID", "jobs")],
      "rounds": [("Job_ID", "jobs")], "results": [("Round_ID", "rounds"), ("Application_ID", "applications")], "offers": [("Application_ID", "applications")],
      "users": [("Student_ID", "students"), ("Company_ID", "companies")]}
DATE_FIELDS = {"Drive_Date", "Application_Deadline", "Application_Date", "Offer_Date"}
SEQ = {"applications": 600}
SESSIONS = {}


class HttpErr(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


class Oracle500(Exception):
    """An unhandled DB error: Flask answers with its HTML 500 page."""


def parse_date(value, style):
    if value is None:
        raise Oracle500("null date")
    value = str(value)
    if style == "iso":
        return date.fromisoformat(value).isoformat()
    m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})-(\d{2,4})", value)
    if not m or m.group(2).upper() not in MONTHS:
        raise Oracle500("ORA-01861: literal does not match format string")
    year = int(m.group(3))
    year = year + 2000 if year < 100 else year
    return date(year, MONTHS.index(m.group(2).upper()) + 1, int(m.group(1))).isoformat()


def out(row):
    """Uppercase keys + RFC-822 dates, the way Oracle + jsonify produce them."""
    res = {}
    for k, v in row.items():
        if k == "Password":
            continue
        if k in DATE_FIELDS and v:
            v = datetime.strptime(v, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 GMT")
        res[k.upper()] = v
    return res


def find(table, **kw):
    return next((r for r in DB[table] if all(r.get(k) == v for k, v in kw.items())), None)


def check_constraints(table, row, ignore=None):
    for fields in UNIQUE.get(table, []):
        for other in DB[table]:
            if other is not ignore and all(other.get(f) == row.get(f) for f in fields):
                raise Oracle500("unique violated")
    for col, parent in FK.get(table, []):
        if row.get(col) is not None and not find(parent, **{PK[parent][0]: row[col]}):
            raise Oracle500("parent key not found")
    if any(find(table, **{f: row[f]}) is not None for f in PK[table][:1]) and ignore is None and len(PK[table]) == 1:
        raise Oracle500("primary key violated")
    if table == "students" and not (0 <= float(row["CGPA"]) <= 10 and int(row["Graduation_Year"]) >= 2026):
        raise Oracle500("check violated")
    if table == "jobs" and not (row["Package_LPA"] > 0 and 0 <= row["Min_CGPA_Requirement"] <= 10):
        raise Oracle500("check violated")
    if table == "drives" and row["Drive_Status"] not in ("UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"):
        raise Oracle500("check violated")
    if table == "applications" and row["Status"] not in ("APPLIED", "SHORTLISTED", "REJECTED", "SELECTED", "WITHDRAWN"):
        raise Oracle500("check violated")
    if table == "offers" and (row["Offered_Package_LPA"] <= 0 or row["Offer_Status"] not in ("PENDING", "ACCEPTED", "REJECTED")):
        raise Oracle500("check violated")
    if table == "results" and row["Result"] not in ("PENDING", "PASSED", "FAILED"):
        raise Oracle500("check violated")


def has_children(table, row):
    for child, links in FK.items():
        for col, parent in links:
            if parent == table and any(c.get(col) == row[PK[table][0]] for c in DB[child]):
                return True
    return False


def company_drive_ids(cid):
    return {d["Drive_ID"] for d in DB["drives"] if d["Company_ID"] == cid}


def company_job_ids(cid):
    ds = company_drive_ids(cid)
    return {j["Job_ID"] for j in DB["jobs"] if j["Drive_ID"] in ds}


# ---------------------------------------------------------------- routing
ROUTES = []


def route(method, pattern, *roles):
    def deco(fn):
        ROUTES.append((method, re.compile("^" + pattern + "$"), roles, fn))
        return fn
    return deco


def admin_crud(path, table, fields, dates=None, date_style="iso", messages=None):
    """Admin CRUD in the same shape as the real controllers."""
    dates = dates or {}
    idpath = "/".join("(?P<%s>\\d+)" % k for k in PK[table])

    def build(body, existing=None):
        row = {}
        for f in fields:
            row[f] = body[f]  # KeyError -> 500, like the controllers
        for f, style in dates.items():
            row[f] = parse_date(row[f], style)
        return row

    @route("GET", path, "ADMIN")
    def _list(req):
        return 200, [out(r) for r in DB[table]]

    @route("POST", path, "ADMIN")
    def _create(req):
        row = build(req.json)
        check_constraints(table, row)
        DB[table].append(row)
        return 201, {"message": "Created successfully"}

    @route("PUT", path + "/" + idpath, "ADMIN")
    def _update(req, **ids):
        cur = find(table, **{k: int(v) for k, v in ids.items()})
        if not cur:
            return 404, {"message": "Not found"}
        body = dict(req.json)
        for k, v in ids.items():
            body.setdefault(k, int(v))
        row = build(body)
        for k in PK[table]:
            row[k] = cur[k]
        check_constraints(table, row, ignore=cur)
        cur.update(row)
        return 200, {"message": "Updated successfully"}

    @route("DELETE", path + "/" + idpath, "ADMIN")
    def _delete(req, **ids):
        cur = find(table, **{k: int(v) for k, v in ids.items()})
        if not cur:
            return 404, {"message": "Not found"}
        if has_children(table, cur):
            raise Oracle500("child record found")
        DB[table].remove(cur)
        return 200, {"message": "Deleted successfully"}


admin_crud("/api/students", "students", ["Student_ID", "Name", "Email", "Phone", "Department", "CGPA", "Graduation_Year", "Resume_URL"])
admin_crud("/api/companies", "companies", ["Company_ID", "Company_Name", "Industry", "Contact_Email", "HR_Name", "Location"])
admin_crud("/api/drives", "drives", ["Drive_ID", "Company_ID", "Drive_Date", "Venue", "Drive_Status"], {"Drive_Date": DATE_STYLE})
admin_crud("/api/jobs", "jobs", ["Job_ID", "Drive_ID", "Job_Title", "Role_Description", "Package_LPA", "Min_CGPA_Requirement", "Application_Deadline"], {"Application_Deadline": DATE_STYLE})
admin_crud("/api/applications", "applications", ["Application_ID", "Student_ID", "Job_ID", "Application_Date", "Status"], {"Application_Date": "iso"})
admin_crud("/api/interview-rounds", "rounds", ["Round_ID", "Job_ID", "Round_Number", "Round_Type"])
admin_crud("/api/offers", "offers", ["Offer_ID", "Application_ID", "Offer_Date", "Offered_Package_LPA", "Offer_Status"], {"Offer_Date": "iso"})


# interview results (composite key, update only touches Result)
@route("GET", "/api/interview-results", "ADMIN")
def results_list(req):
    return 200, [out(r) for r in DB["results"]]


@route("POST", "/api/interview-results", "ADMIN")
def results_create(req):
    row = {"Round_ID": req.json["Round_ID"], "Application_ID": req.json["Application_ID"], "Result": req.json["Result"]}
    if find("results", Round_ID=row["Round_ID"], Application_ID=row["Application_ID"]):
        raise HttpErr(500, "Unable to create interview result.")
    try:
        check_constraints("results", row, ignore=True)
    except Oracle500:
        raise HttpErr(500, "Unable to create interview result.")
    DB["results"].append(row)
    return 201, {"message": "Interview result created successfully."}


@route("PUT", r"/api/interview-results/(?P<rid>\d+)/(?P<aid>\d+)", "ADMIN")
def results_update(req, rid, aid):
    cur = find("results", Round_ID=int(rid), Application_ID=int(aid))
    if not cur:
        return 404, {"message": "Interview result not found."}
    cur["Result"] = req.json["Result"]
    return 200, {"message": "Interview result updated successfully."}


@route("DELETE", r"/api/interview-results/(?P<rid>\d+)/(?P<aid>\d+)", "ADMIN")
def results_delete(req, rid, aid):
    cur = find("results", Round_ID=int(rid), Application_ID=int(aid))
    if not cur:
        return 404, {"message": "Interview result not found."}
    DB["results"].remove(cur)
    return 200, {"message": "Interview result deleted successfully."}


# users
@route("GET", "/api/users", "ADMIN")
def users_list(req):
    return 200, [out({k: v for k, v in u.items() if k != "Password"}) for u in DB["users"]]


@route("POST", "/api/users", "ADMIN")
def users_create(req):
    b = req.json
    if not all(b.get(k) for k in ("User_ID", "Username", "Password", "Role")):
        return 400, {"message": "User_ID, Username, Password and Role are required."}
    row = dict(User_ID=b["User_ID"], Username=b["Username"], Password=b["Password"], Role=b["Role"], Student_ID=b.get("Student_ID"), Company_ID=b.get("Company_ID"))
    try:
        if row["Role"] not in ("STUDENT", "RECRUITER", "ADMIN"):
            raise Oracle500("check")
        check_constraints("users", row)
    except Oracle500:
        return 400, {"message": "Unable to create user."}
    DB["users"].append(row)
    return 201, {"message": "User created successfully."}


@route("PUT", r"/api/users/(?P<uid>\d+)", "ADMIN")
def users_update(req, uid):
    cur = find("users", User_ID=int(uid))
    if not cur:
        return 404, {"message": "User not found."}
    b = req.json
    new = dict(cur, Username=b["Username"], Role=b["Role"], Student_ID=b.get("Student_ID"), Company_ID=b.get("Company_ID"))
    if b.get("Password"):
        new["Password"] = b["Password"]
    try:
        check_constraints("users", new, ignore=cur)
    except Oracle500:
        return 400, {"message": "Unable to update user."}
    cur.update(new)
    return 200, {"message": "User updated successfully."}


@route("DELETE", r"/api/users/(?P<uid>\d+)", "ADMIN")
def users_delete(req, uid):
    cur = find("users", User_ID=int(uid))
    if not cur:
        return 404, {"message": "User not found."}
    DB["users"].remove(cur)
    return 200, {"message": "User deleted successfully."}


# auth
@route("POST", "/api/auth/login")
def login(req):
    b = req.json
    if not isinstance(b, dict):
        return 400, {"message": "A JSON request body is required."}
    if not isinstance(b.get("Username"), str) or not isinstance(b.get("Password"), str):
        return 400, {"message": "Username and password are required."}
    u = next((x for x in DB["users"] if x["Username"] == b["Username"] and x["Password"] == b["Password"]), None)
    if not u:
        return 401, {"message": "Invalid username or password."}
    req.session.clear()
    req.session.update(user_id=u["User_ID"], username=u["Username"], role=u["Role"], student_id=u["Student_ID"], company_id=u["Company_ID"])
    return 200, {"message": "Login successful.", "user": {"User_ID": u["User_ID"], "Username": u["Username"], "Role": u["Role"], "Student_ID": u["Student_ID"], "Company_ID": u["Company_ID"]}}


@route("GET", "/api/auth/me")
def me(req):
    if "user_id" not in req.session:
        return 401, {"message": "Authentication required."}
    s = req.session
    return 200, {"user_id": s["user_id"], "username": s["username"], "role": s["role"], "student_id": s.get("student_id"), "company_id": s.get("company_id")}


@route("POST", "/api/auth/logout")
def logout(req):
    req.session.clear()
    return 200, {"message": "Logged out successfully."}


# ---- student
def job_row(j, detail=False):
    d = find("drives", Drive_ID=j["Drive_ID"])
    c = find("companies", Company_ID=d["Company_ID"])
    r = dict(Job_ID=j["Job_ID"], Job_Title=j["Job_Title"], Role_Description=j["Role_Description"], Package_LPA=j["Package_LPA"],
             Min_CGPA_Requirement=j["Min_CGPA_Requirement"], Application_Deadline=j["Application_Deadline"], Company_Name=c["Company_Name"])
    if detail:
        r.update(Industry=c["Industry"], Location=c["Location"], Venue=d["Venue"])
    r.update(Drive_Date=d["Drive_Date"], Drive_Status=d["Drive_Status"])
    return r


def open_jobs():
    for j in sorted(DB["jobs"], key=lambda x: (x["Application_Deadline"], x["Job_ID"])):
        d = find("drives", Drive_ID=j["Drive_ID"])
        if date.fromisoformat(j["Application_Deadline"]) >= TODAY and d["Drive_Status"] in ("UPCOMING", "ONGOING"):
            yield j


@route("GET", "/api/student/profile", "STUDENT")
def s_profile(req):
    s = find("students", Student_ID=req.session["student_id"])
    return (200, out(s)) if s else (404, {"message": "Student profile not found."})


@route("PUT", "/api/student/profile", "STUDENT")
def s_profile_put(req):
    b = req.json
    if not isinstance(b, dict):
        return 400, {"message": "A JSON request body is required."}
    if any(not isinstance(b.get(f), str) or not b[f].strip() for f in ("Name", "Email")):
        return 400, {"message": "Name and Email are required."}
    s = find("students", Student_ID=req.session["student_id"])
    if any(o is not s and o["Email"] == b["Email"] for o in DB["students"]):
        return 400, {"message": "Unable to update profile. Check whether the email is already in use."}
    s.update(Name=b["Name"], Email=b["Email"], Phone=b.get("Phone"), Resume_URL=b.get("Resume_URL"))
    return 200, {"message": "Profile updated successfully."}


@route("GET", "/api/student/jobs", "STUDENT")
def s_jobs(req):
    q = req.query
    try:
        lo = float(q["min_package"][0]) if "min_package" in q else None
        hi = float(q["max_package"][0]) if "max_package" in q else None
        if (lo is not None and lo < 0) or (hi is not None and hi < 0):
            raise ValueError
    except ValueError:
        return 400, {"message": "Package filters must be valid non-negative numbers."}
    if lo is not None and hi is not None and lo > hi:
        return 400, {"message": "Minimum package cannot exceed maximum package."}
    search = (q.get("search", [""])[0] or "").strip().lower()
    rows = []
    for j in open_jobs():
        r = job_row(j)
        if search and search not in j["Job_Title"].lower() and search not in r["Company_Name"].lower():
            continue
        if lo is not None and j["Package_LPA"] < lo:
            continue
        if hi is not None and j["Package_LPA"] > hi:
            continue
        rows.append(out(r))
    return 200, rows


@route("GET", r"/api/student/jobs/(?P<jid>\d+)", "STUDENT")
def s_job(req, jid):
    j = next((x for x in open_jobs() if x["Job_ID"] == int(jid)), None)
    return (200, out(job_row(j, True))) if j else (404, {"message": "Job not found or no longer available."})


def app_view(a):
    j = find("jobs", Job_ID=a["Job_ID"])
    d = find("drives", Drive_ID=j["Drive_ID"])
    c = find("companies", Company_ID=d["Company_ID"])
    return dict(Application_ID=a["Application_ID"], Job_ID=a["Job_ID"], Job_Title=j["Job_Title"], Company_Name=c["Company_Name"],
                Application_Date=a["Application_Date"], Status=a["Status"], Package_LPA=j["Package_LPA"], Application_Deadline=j["Application_Deadline"])


@route("GET", "/api/student/applications", "STUDENT")
def s_apps(req):
    mine = [a for a in DB["applications"] if a["Student_ID"] == req.session["student_id"]]
    mine.sort(key=lambda a: (a["Application_Date"], a["Application_ID"]), reverse=True)
    return 200, [out(app_view(a)) for a in mine]


@route("POST", "/api/student/applications", "STUDENT")
def s_apply(req):
    b = req.json
    if not isinstance(b, dict):
        return 400, {"message": "A JSON request body is required."}
    jid = b.get("Job_ID")
    if not isinstance(jid, int) or isinstance(jid, bool) or jid <= 0:
        return 400, {"message": "A valid Job_ID is required."}
    sid = req.session["student_id"]
    s, j = find("students", Student_ID=sid), find("jobs", Job_ID=jid)
    if not s or not j:
        return 404, {"message": "Student or job not found."}
    d = find("drives", Drive_ID=j["Drive_ID"])
    if s["CGPA"] < j["Min_CGPA_Requirement"]:
        return 400, {"message": "You do not meet the minimum CGPA requirement."}
    if date.fromisoformat(j["Application_Deadline"]) < TODAY:
        return 400, {"message": "The application deadline has passed."}
    if d["Drive_Status"] not in ("UPCOMING", "ONGOING"):
        return 400, {"message": "Applications are not open for this drive."}
    if find("applications", Student_ID=sid, Job_ID=jid):
        return 409, {"message": "You have already applied for this job."}
    SEQ["applications"] += 1
    DB["applications"].append(dict(Application_ID=SEQ["applications"], Student_ID=sid, Job_ID=jid, Application_Date=TODAY.isoformat(), Status="APPLIED"))
    return 201, {"message": "Application submitted successfully.", "Application_ID": SEQ["applications"]}


@route("GET", "/api/student/interview-results", "STUDENT")
def s_results(req):
    rows = []
    for a in sorted([x for x in DB["applications"] if x["Student_ID"] == req.session["student_id"]], key=lambda x: x["Application_ID"]):
        v = app_view(a)
        for rd in sorted([r for r in DB["rounds"] if r["Job_ID"] == a["Job_ID"]], key=lambda r: r["Round_Number"]):
            res = find("results", Round_ID=rd["Round_ID"], Application_ID=a["Application_ID"])
            rows.append(out(dict(Application_ID=a["Application_ID"], Job_ID=a["Job_ID"], Job_Title=v["Job_Title"], Company_Name=v["Company_Name"],
                                 Round_ID=rd["Round_ID"], Round_Number=rd["Round_Number"], Round_Type=rd["Round_Type"], Result=res["Result"] if res else "PENDING")))
    return 200, rows


@route("GET", "/api/student/offers", "STUDENT")
def s_offers(req):
    rows = []
    for o in sorted(DB["offers"], key=lambda o: (o["Offer_Date"], o["Offer_ID"]), reverse=True):
        a = find("applications", Application_ID=o["Application_ID"])
        if a["Student_ID"] != req.session["student_id"]:
            continue
        v = app_view(a)
        rows.append(out(dict(Offer_ID=o["Offer_ID"], Application_ID=o["Application_ID"], Job_ID=a["Job_ID"], Job_Title=v["Job_Title"], Company_Name=v["Company_Name"],
                             Offer_Date=o["Offer_Date"], Offered_Package_LPA=o["Offered_Package_LPA"], Offer_Status=o["Offer_Status"])))
    return 200, rows


@route("GET", "/api/student/dashboard", "STUDENT")
def s_dash(req):
    sid = req.session["student_id"]
    apps = [a for a in DB["applications"] if a["Student_ID"] == sid]
    ids = {a["Application_ID"] for a in apps}
    offers = [o for o in DB["offers"] if o["Application_ID"] in ids]
    return 200, {
        "TOTAL_APPLICATIONS": len(apps),
        "SHORTLISTED_APPLICATIONS": sum(a["Status"] == "SHORTLISTED" for a in apps),
        "PASSED_ROUNDS": sum(r["Result"] == "PASSED" and r["Application_ID"] in ids for r in DB["results"]),
        "TOTAL_OFFERS": len(offers),
        "ACCEPTED_OFFERS": sum(o["Offer_Status"] == "ACCEPTED" for o in offers),
    }


# ---- recruiter
def cid(req):
    c = req.session.get("company_id")
    if not c:
        raise HttpErr(400, "No company is associated with this recruiter.")
    return c


@route("GET", "/api/recruiter/company", "RECRUITER")
def r_company(req):
    return 200, out(find("companies", Company_ID=cid(req)))


@route("PUT", "/api/recruiter/company", "RECRUITER")
def r_company_put(req):
    c = find("companies", Company_ID=cid(req))
    allowed = ["Company_Name", "Industry", "Contact_Email", "HR_Name", "Location"]
    upd = {k: req.json[k] for k in allowed if k in (req.json or {})}
    if not upd:
        return 400, {"message": "No valid company fields provided."}
    c.update(upd)
    return 200, {"message": "Company updated successfully."}


@route("GET", "/api/recruiter/drives", "RECRUITER")
def r_drives(req):
    return 200, [out(d) for d in DB["drives"] if d["Company_ID"] == cid(req)]


@route("POST", "/api/recruiter/drives", "RECRUITER")
def r_drive_add(req):
    b = req.json
    row = dict(Drive_ID=b["Drive_ID"], Company_ID=cid(req), Drive_Date=parse_date(b["Drive_Date"], DATE_STYLE), Venue=b["Venue"], Drive_Status=b["Drive_Status"])
    check_constraints("drives", row)
    DB["drives"].append(row)
    return 201, {"message": "Placement drive created successfully"}


@route("PUT", r"/api/recruiter/drives/(?P<did>\d+)", "RECRUITER")
def r_drive_put(req, did):
    d = find("drives", Drive_ID=int(did), Company_ID=cid(req))
    if not d:
        return 404, {"message": "Placement drive not found for your company."}
    new = dict(d, Drive_Date=parse_date(req.json["Drive_Date"], DATE_STYLE), Venue=req.json["Venue"], Drive_Status=req.json["Drive_Status"])
    check_constraints("drives", new, ignore=d)
    d.update(new)
    return 200, {"message": "Placement drive updated successfully"}


@route("DELETE", r"/api/recruiter/drives/(?P<did>\d+)", "RECRUITER")
def r_drive_del(req, did):
    d = find("drives", Drive_ID=int(did), Company_ID=cid(req))
    if not d:
        return 404, {"message": "Placement drive not found for your company."}
    if has_children("drives", d):
        raise Oracle500("child record found")
    DB["drives"].remove(d)
    return 200, {"message": "Placement drive deleted successfully"}


@route("GET", "/api/recruiter/jobs", "RECRUITER")
def r_jobs(req):
    ids = company_job_ids(cid(req))
    return 200, [out(j) for j in sorted(DB["jobs"], key=lambda j: j["Job_ID"]) if j["Job_ID"] in ids]


@route("POST", "/api/recruiter/jobs", "RECRUITER")
def r_job_add(req):
    b = req.json
    if b["Drive_ID"] not in company_drive_ids(cid(req)):
        return 400, {"message": "Drive does not belong to your company."}
    row = dict(Job_ID=b["Job_ID"], Drive_ID=b["Drive_ID"], Job_Title=b["Job_Title"], Role_Description=b["Role_Description"], Package_LPA=b["Package_LPA"],
               Min_CGPA_Requirement=b["Min_CGPA_Requirement"], Application_Deadline=parse_date(b["Application_Deadline"], DATE_STYLE))
    try:
        check_constraints("jobs", row)
    except Oracle500:
        return 500, {"message": "Unable to create job posting."}
    DB["jobs"].append(row)
    return 201, {"message": "Job posting created successfully."}


@route("PUT", r"/api/recruiter/jobs/(?P<jid>\d+)", "RECRUITER")
def r_job_put(req, jid):
    if int(jid) not in company_job_ids(cid(req)):
        return 404, {"message": "Job posting not found for your company."}
    j = find("jobs", Job_ID=int(jid))
    b = req.json
    j.update(Job_Title=b["Job_Title"], Role_Description=b["Role_Description"], Package_LPA=b["Package_LPA"], Min_CGPA_Requirement=b["Min_CGPA_Requirement"],
             Application_Deadline=parse_date(b["Application_Deadline"], DATE_STYLE))
    return 200, {"message": "Job posting updated successfully."}


@route("DELETE", r"/api/recruiter/jobs/(?P<jid>\d+)", "RECRUITER")
def r_job_del(req, jid):
    if int(jid) not in company_job_ids(cid(req)):
        return 404, {"message": "Job posting not found for your company."}
    j = find("jobs", Job_ID=int(jid))
    if has_children("jobs", j):
        return 500, {"message": "Unable to delete job posting."}
    DB["jobs"].remove(j)
    return 200, {"message": "Job posting deleted successfully."}


@route("GET", "/api/recruiter/applications", "RECRUITER")
def r_apps(req):
    ids = company_job_ids(cid(req))
    rows = [a for a in DB["applications"] if a["Job_ID"] in ids]
    rows.sort(key=lambda a: (a["Application_Date"], a["Application_ID"]), reverse=True)
    return 200, [out(dict(Application_ID=a["Application_ID"], Student_ID=a["Student_ID"], Job_ID=a["Job_ID"], Job_Title=find("jobs", Job_ID=a["Job_ID"])["Job_Title"],
                          Application_Date=a["Application_Date"], Status=a["Status"])) for a in rows]


@route("PUT", r"/api/recruiter/applications/(?P<aid>\d+)", "RECRUITER")
def r_app_put(req, aid):
    a = find("applications", Application_ID=int(aid))
    if not a or a["Job_ID"] not in company_job_ids(cid(req)):
        return 404, {"message": "Application not found for your company."}
    status = (req.json or {}).get("Status")
    if not isinstance(status, str) or not status.strip():
        return 400, {"message": "A valid Status is required."}
    if status.strip() not in ("APPLIED", "SHORTLISTED", "REJECTED", "SELECTED", "WITHDRAWN"):
        return 500, {"message": "Unable to update application status."}
    a["Status"] = status.strip()
    return 200, {"message": "Application status updated successfully."}


@route("GET", "/api/recruiter/interview-rounds", "RECRUITER")
def r_rounds(req):
    ids = company_job_ids(cid(req))
    return 200, [out(r) for r in sorted(DB["rounds"], key=lambda r: (r["Job_ID"], r["Round_Number"])) if r["Job_ID"] in ids]


@route("POST", "/api/recruiter/interview-rounds", "RECRUITER")
def r_round_add(req):
    b = req.json
    if b["Job_ID"] not in company_job_ids(cid(req)):
        return 400, {"message": "Job does not belong to your company."}
    row = dict(Round_ID=b["Round_ID"], Job_ID=b["Job_ID"], Round_Number=b["Round_Number"], Round_Type=b["Round_Type"])
    try:
        check_constraints("rounds", row)
    except Oracle500:
        return 500, {"message": "Unable to create interview round."}
    DB["rounds"].append(row)
    return 201, {"message": "Interview round created successfully."}


@route("PUT", r"/api/recruiter/interview-rounds/(?P<rid>\d+)", "RECRUITER")
def r_round_put(req, rid):
    r = find("rounds", Round_ID=int(rid))
    if not r or r["Job_ID"] not in company_job_ids(cid(req)):
        return 404, {"message": "Interview round not found for your company."}
    new = dict(r, Job_ID=req.json["Job_ID"], Round_Number=req.json["Round_Number"], Round_Type=req.json["Round_Type"])
    try:
        check_constraints("rounds", new, ignore=r)
    except Oracle500:
        return 500, {"message": "Unable to update interview round."}
    r.update(new)
    return 200, {"message": "Interview round updated successfully."}


@route("DELETE", r"/api/recruiter/interview-rounds/(?P<rid>\d+)", "RECRUITER")
def r_round_del(req, rid):
    r = find("rounds", Round_ID=int(rid))
    if not r or r["Job_ID"] not in company_job_ids(cid(req)):
        return 404, {"message": "Interview round not found for your company."}
    if has_children("rounds", r):
        return 500, {"message": "Unable to delete interview round."}
    DB["rounds"].remove(r)
    return 200, {"message": "Interview round deleted successfully."}


def company_offer_rows(c):
    ids = company_job_ids(c)
    rows = []
    for o in sorted(DB["offers"], key=lambda o: (o["Offer_Date"], o["Offer_ID"]), reverse=True):
        a = find("applications", Application_ID=o["Application_ID"])
        if a["Job_ID"] in ids:
            rows.append((o, a))
    return rows


@route("GET", "/api/recruiter/offers", "RECRUITER")
def r_offers(req):
    return 200, [out(dict(Offer_ID=o["Offer_ID"], Application_ID=o["Application_ID"], Student_ID=a["Student_ID"], Job_ID=a["Job_ID"], Offer_Date=o["Offer_Date"],
                          Offered_Package_LPA=o["Offered_Package_LPA"], Offer_Status=o["Offer_Status"])) for o, a in company_offer_rows(cid(req))]


@route("POST", "/api/recruiter/offers", "RECRUITER")
def r_offer_add(req):
    b = req.json
    if any(f not in b for f in ("Offer_ID", "Application_ID", "Offer_Date", "Offered_Package_LPA", "Offer_Status")):
        return 400, {"message": "Missing required offer fields."}
    a = find("applications", Application_ID=b["Application_ID"])
    if not a or a["Job_ID"] not in company_job_ids(cid(req)):
        return 400, {"message": "Application does not belong to your company."}
    row = dict(Offer_ID=b["Offer_ID"], Application_ID=b["Application_ID"], Offer_Date=parse_date(b["Offer_Date"], "iso"), Offered_Package_LPA=b["Offered_Package_LPA"], Offer_Status=b["Offer_Status"])
    try:
        check_constraints("offers", row)
    except Oracle500:
        return 500, {"message": "Unable to create offer."}
    DB["offers"].append(row)
    return 201, {"message": "Offer created successfully."}


@route("PUT", r"/api/recruiter/offers/(?P<oid>\d+)", "RECRUITER")
def r_offer_put(req, oid):
    b = req.json
    if any(f not in b for f in ("Offer_Date", "Offered_Package_LPA", "Offer_Status")):
        return 400, {"message": "Missing required offer fields."}
    o = next((o for o, _ in company_offer_rows(cid(req)) if o["Offer_ID"] == int(oid)), None)
    if not o:
        return 404, {"message": "Offer not found."}
    new = dict(o, Offer_Date=parse_date(b["Offer_Date"], "iso"), Offered_Package_LPA=b["Offered_Package_LPA"], Offer_Status=b["Offer_Status"])
    try:
        check_constraints("offers", new, ignore=o)
    except Oracle500:
        return 500, {"message": "Unable to update offer."}
    o.update(new)
    return 200, {"message": "Offer updated successfully."}


@route("DELETE", r"/api/recruiter/offers/(?P<oid>\d+)", "RECRUITER")
def r_offer_del(req, oid):
    o = next((o for o, _ in company_offer_rows(cid(req)) if o["Offer_ID"] == int(oid)), None)
    if not o:
        return 404, {"message": "Offer not found."}
    DB["offers"].remove(o)
    return 200, {"message": "Offer deleted successfully."}


# ---------------------------------------------------------------- http glue
class Req:
    pass


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def _send(self, status, body, ctype="application/json", cookie=None):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    def _handle(self):
        url = urlsplit(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        req = Req()
        try:
            req.json = json.loads(raw) if raw else None
        except ValueError:
            req.json = None
        req.query = parse_qs(url.query)
        m = re.search(r"session=([A-Za-z0-9_\-]+)", self.headers.get("Cookie", ""))
        token = m.group(1) if m else None
        new_cookie = None
        if token not in SESSIONS:
            token = secrets.token_urlsafe(24)
            SESSIONS[token] = {}
            new_cookie = "session=%s; HttpOnly; Path=/; SameSite=Lax" % token
        req.session = SESSIONS[token]

        if url.path == "/":
            return self._send(200, b"Backend is running!", "text/html", new_cookie)
        for method, rx, roles, fn in ROUTES:
            mm = rx.match(url.path)
            if method == self.command and mm:
                try:
                    if roles:
                        if "user_id" not in req.session:
                            return self._send(401, {"message": "Authentication required."}, cookie=new_cookie)
                        if req.session.get("role") not in roles:
                            return self._send(403, {"message": "Access denied."}, cookie=new_cookie)
                    status, body = fn(req, **mm.groupdict())
                    return self._send(status, body, cookie=new_cookie)
                except HttpErr as e:
                    return self._send(e.status, {"message": e.message}, cookie=new_cookie)
                except (Oracle500, KeyError, TypeError, ValueError):
                    return self._send(500, b"<!doctype html><title>500 Internal Server Error</title><h1>Internal Server Error</h1>", "text/html", new_cookie)
        return self._send(404, {"message": "Not found"}, cookie=new_cookie)

    do_GET = do_POST = do_PUT = do_DELETE = _handle


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Mock backend on http://127.0.0.1:%d  (today=%s, drive/job dates=%s)" % (PORT, TODAY, DATE_STYLE))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
