/* Admin console */
(function () {
  const A = window.APMS;
  const { h, fmtDate, fmtLPA, fmtNum, badge, toast, empty, pageHead, stat, breakdown, barRows, titleCase, sendDate, toInputDate, todayISO, nextId, byId, countBy } = A.ui;
  const api = A.api;
  const DATE_STYLE = () => A.config.PLAIN_DATE_STYLE;

  const APP_STATUSES = ["APPLIED", "SHORTLISTED", "SELECTED", "REJECTED", "WITHDRAWN"];
  const DRIVE_STATUSES = ["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"];
  const OFFER_STATUSES = ["PENDING", "ACCEPTED", "REJECTED"];
  const RESULTS = ["PENDING", "PASSED", "FAILED"];
  const ROLES = ["STUDENT", "RECRUITER", "ADMIN"];
  const opts = (list) => list.map((s) => ({ value: s, label: titleCase(s) }));

  const ERR_HINT = "Check that the ID isn't already taken and that every value is valid.";
  const get = (url) => api.get(url);

  /* ---------- Label helpers (turn ids into names) ---------- */
  const L = {
    student: (m) => (id) => (m[id] ? m[id].Name : "Student " + id),
    company: (m) => (id) => (m[id] ? m[id].Company_Name : "Company " + id),
    job: (m) => (id) => (m[id] ? m[id].Job_Title : "Job " + id),
  };
  const idCell = (v) => h("span", { class: "mono" }, v);
  const withSub = (main, sub) => h("div", null, h("div", { class: "cell-main" }, main), sub ? h("div", { class: "cell-sub" }, sub) : null);

  /* ---------- Dashboard ---------- */
  async function dashboard(c) {
    const [students, companies, drives, jobs, applications, offers, users] = await Promise.all([
      get("/api/students"), get("/api/companies"), get("/api/drives"), get("/api/jobs"), get("/api/applications"), get("/api/offers"), get("/api/users"),
    ]);
    c.appendChild(pageHead("Placement overview", "Live totals across all records."));

    const appById = byId(applications, "Application_ID");
    const jobById = byId(jobs, "Job_ID");
    const driveById = byId(drives, "Drive_ID");
    const companyById = byId(companies, "Company_ID");
    const accepted = offers.filter((o) => o.Offer_Status === "ACCEPTED");
    const placedIds = new Set(accepted.map((o) => (appById[o.Application_ID] || {}).Student_ID).filter((x) => x !== undefined));
    const pkgs = accepted.map((o) => Number(o.Offered_Package_LPA)).filter((n) => !isNaN(n));
    const avg = pkgs.length ? pkgs.reduce((a, b) => a + b, 0) / pkgs.length : null;
    const top = pkgs.length ? Math.max.apply(null, pkgs) : null;
    const rate = students.length ? Math.round((placedIds.size / students.length) * 100) : 0;
    const active = drives.filter((d) => d.Drive_Status === "UPCOMING" || d.Drive_Status === "ONGOING").length;

    c.appendChild(
      h(
        "div",
        { class: "stats" },
        stat(students.length, "Students"),
        stat(companies.length, "Companies"),
        stat(active, "Active drives"),
        stat(jobs.length, "Job postings"),
        stat(applications.length, "Applications"),
        stat(offers.length, "Offers")
      )
    );
    c.appendChild(
      h(
        "div",
        { class: "stats" },
        stat(placedIds.size + " / " + students.length, "Students placed (accepted offer)", true),
        stat(rate + "%", "Placement rate"),
        stat(top === null ? "—" : fmtLPA(top), "Highest accepted package"),
        stat(avg === null ? "—" : fmtLPA(avg.toFixed(2)), "Average accepted package")
      )
    );

    const perCompany = {};
    applications.forEach((a) => {
      const job = jobById[a.Job_ID];
      const drive = job && driveById[job.Drive_ID];
      const co = drive && companyById[drive.Company_ID];
      const name = co ? co.Company_Name : "Unknown";
      perCompany[name] = (perCompany[name] || 0) + 1;
    });
    const companyBars = Object.keys(perCompany).map((k) => ({ label: k, value: perCompany[k] })).sort((a, b) => b.value - a.value).slice(0, 6);
    const deptBars = Object.entries(countBy(students, "Department")).map(([k, v]) => ({ label: k || "Unspecified", value: v })).sort((a, b) => b.value - a.value);

    c.appendChild(
      h(
        "div",
        { class: "grid-2" },
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Applications by status"), breakdown(countBy(applications, "Status"), APP_STATUSES)),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Offers by status"), breakdown(countBy(offers, "Offer_Status"), OFFER_STATUSES)),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Drives by status"), breakdown(countBy(drives, "Drive_Status"), DRIVE_STATUSES)),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "User accounts"), breakdown(countBy(users, "Role"), ROLES.map((r) => r))),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Most applications by company"), companyBars.length ? barRows(companyBars) : h("p", { class: "muted" }, "No applications yet.")),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Students by department"), deptBars.length ? barRows(deptBars) : h("p", { class: "muted" }, "No students yet."))
      )
    );
  }

  /* ---------- Students ---------- */
  const studentsPage = A.crudPage({
    title: "Students", subtitle: "Student records and academic details.", singular: "student", createLabel: "New student",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    deleteHint: "A student with applications or a linked user account can't be deleted until those are removed.",
    load: async () => ({ rows: await get("/api/students"), lookups: {} }),
    columns: () => [
      { label: "ID", render: (r) => idCell(r.Student_ID) },
      { label: "Student", render: (r) => withSub(r.Name, r.Email) },
      { label: "Department", render: (r) => r.Department || "—" },
      { label: "CGPA", num: true, render: (r) => fmtNum(r.CGPA, 2) },
      { label: "Grad. year", num: true, render: (r) => r.Graduation_Year || "—" },
      { label: "Phone", render: (r) => r.Phone || "—" },
    ],
    searchText: (r) => [r.Student_ID, r.Name, r.Email, r.Department, r.Phone].join(" "),
    filters: (lk) => [],
    fields: (lk, mode) => [
      { name: "Student_ID", label: "Student ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
      { name: "Name", label: "Full name", required: true },
      { name: "Email", label: "Email", type: "email", required: true },
      { name: "Phone", label: "Phone", type: "tel" },
      { name: "Department", label: "Department" },
      { name: "CGPA", label: "CGPA", type: "number", required: true, min: 0, max: 10, step: 0.01 },
      { name: "Graduation_Year", label: "Graduation year", type: "number", required: true, min: 2026, max: 2100, step: 1, hint: "2026 or later." },
      { name: "Resume_URL", label: "Resume link", type: "url", full: true, placeholder: "https://" },
    ],
    initialValues: (lk, rows) => ({ Student_ID: nextId(rows, "Student_ID") }),
    toPayload: (v) => ({ Student_ID: v.Student_ID, Name: v.Name, Email: v.Email, Phone: v.Phone, Department: v.Department, CGPA: v.CGPA, Graduation_Year: v.Graduation_Year, Resume_URL: v.Resume_URL }),
    create: (p) => api.post("/api/students", p),
    update: (row, p) => api.put("/api/students/" + row.Student_ID, p),
    remove: (row) => api.del("/api/students/" + row.Student_ID),
    describe: (r) => r.Name + " (ID " + r.Student_ID + ").",
  });

  /* ---------- Companies ---------- */
  const companiesPage = A.crudPage({
    title: "Companies", subtitle: "Recruiting companies.", singular: "company", createLabel: "New company",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    deleteHint: "A company with drives or linked user accounts can't be deleted until those are removed.",
    load: async () => ({ rows: await get("/api/companies"), lookups: {} }),
    columns: () => [
      { label: "ID", render: (r) => idCell(r.Company_ID) },
      { label: "Company", render: (r) => withSub(r.Company_Name, r.Industry) },
      { label: "Location", render: (r) => r.Location || "—" },
      { label: "HR contact", render: (r) => withSub(r.HR_Name, r.Contact_Email) },
    ],
    searchText: (r) => [r.Company_ID, r.Company_Name, r.Industry, r.Location, r.HR_Name, r.Contact_Email].join(" "),
    fields: (lk, mode) => [
      { name: "Company_ID", label: "Company ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
      { name: "Company_Name", label: "Company name", required: true },
      { name: "Industry", label: "Industry" },
      { name: "Location", label: "Location" },
      { name: "HR_Name", label: "HR contact name", required: true },
      { name: "Contact_Email", label: "Contact email", type: "email", required: true },
    ],
    initialValues: (lk, rows) => ({ Company_ID: nextId(rows, "Company_ID") }),
    toPayload: (v) => ({ Company_ID: v.Company_ID, Company_Name: v.Company_Name, Industry: v.Industry, Contact_Email: v.Contact_Email, HR_Name: v.HR_Name, Location: v.Location }),
    create: (p) => api.post("/api/companies", p),
    update: (row, p) => api.put("/api/companies/" + row.Company_ID, p),
    remove: (row) => api.del("/api/companies/" + row.Company_ID),
    describe: (r) => r.Company_Name + " (ID " + r.Company_ID + ").",
  });

  /* ---------- Drives ---------- */
  const drivesPage = A.crudPage({
    title: "Placement drives", subtitle: "Each drive is one company's visit to campus.", singular: "drive", createLabel: "New drive",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    deleteHint: "Delete the drive's job postings first.",
    load: async () => {
      const [rows, companies] = await Promise.all([get("/api/drives"), get("/api/companies")]);
      return { rows, lookups: { companies, cm: byId(companies, "Company_ID") } };
    },
    columns: (lk) => [
      { label: "ID", render: (r) => idCell(r.Drive_ID) },
      { label: "Company", render: (r) => h("span", { class: "cell-main" }, L.company(lk.cm)(r.Company_ID)) },
      { label: "Date", render: (r) => fmtDate(r.Drive_Date) },
      { label: "Venue", render: (r) => r.Venue || "—" },
      { label: "Status", render: (r) => badge(r.Drive_Status) },
    ],
    searchText: (r, lk) => [r.Drive_ID, L.company(lk.cm)(r.Company_ID), r.Venue, r.Drive_Status].join(" "),
    filters: (lk) => [
      { label: "All statuses", options: opts(DRIVE_STATUSES), match: (r, v) => r.Drive_Status === v },
      { label: "All companies", options: lk.companies.map((c) => ({ value: c.Company_ID, label: c.Company_Name })), match: (r, v) => String(r.Company_ID) === v },
    ],
    fields: (lk, mode) => [
      { name: "Drive_ID", label: "Drive ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
      { name: "Company_ID", label: "Company", type: "select", required: true, options: lk.companies.map((c) => ({ value: c.Company_ID, label: c.Company_Name })) },
      { name: "Drive_Date", label: "Drive date", type: "date", required: true },
      { name: "Drive_Status", label: "Status", type: "select", required: true, options: opts(DRIVE_STATUSES) },
      { name: "Venue", label: "Venue", full: true },
    ],
    initialValues: (lk, rows) => ({ Drive_ID: nextId(rows, "Drive_ID"), Drive_Status: "UPCOMING" }),
    editValues: (r) => ({ ...r, Drive_Date: toInputDate(r.Drive_Date) }),
    toPayload: (v) => ({ Drive_ID: v.Drive_ID, Company_ID: Number(v.Company_ID), Drive_Date: sendDate(v.Drive_Date, DATE_STYLE()), Venue: v.Venue, Drive_Status: v.Drive_Status }),
    create: (p) => api.post("/api/drives", p),
    update: (row, p) => api.put("/api/drives/" + row.Drive_ID, p),
    remove: (row) => api.del("/api/drives/" + row.Drive_ID),
    describe: (r, lk) => "Drive " + r.Drive_ID + " for " + L.company(lk.cm)(r.Company_ID) + ".",
  });

  /* ---------- Jobs ---------- */
  const jobsPage = A.crudPage({
    title: "Job postings", subtitle: "Roles open for application.", singular: "job posting", createLabel: "New job posting",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    deleteHint: "A job with applications or interview rounds can't be deleted until those are removed.",
    load: async () => {
      const [rows, drives, companies] = await Promise.all([get("/api/jobs"), get("/api/drives"), get("/api/companies")]);
      const cm = byId(companies, "Company_ID");
      return { rows, lookups: { drives, dm: byId(drives, "Drive_ID"), cm } };
    },
    columns: (lk) => [
      { label: "ID", render: (r) => idCell(r.Job_ID) },
      { label: "Job", render: (r) => { const d = lk.dm[r.Drive_ID]; return withSub(r.Job_Title, d ? L.company(lk.cm)(d.Company_ID) : "Drive " + r.Drive_ID); } },
      { label: "Package", num: true, render: (r) => fmtLPA(r.Package_LPA) },
      { label: "Min CGPA", num: true, render: (r) => fmtNum(r.Min_CGPA_Requirement, 2) },
      { label: "Apply by", render: (r) => fmtDate(r.Application_Deadline) },
    ],
    searchText: (r, lk) => { const d = lk.dm[r.Drive_ID]; return [r.Job_ID, r.Job_Title, r.Role_Description, d ? L.company(lk.cm)(d.Company_ID) : ""].join(" "); },
    fields: (lk, mode) => [
      { name: "Job_ID", label: "Job ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
      { name: "Drive_ID", label: "Drive", type: "select", required: true, options: lk.drives.map((d) => ({ value: d.Drive_ID, label: d.Drive_ID + " · " + L.company(lk.cm)(d.Company_ID) + " · " + fmtDate(d.Drive_Date) })) },
      { name: "Job_Title", label: "Job title", required: true, full: true },
      { name: "Role_Description", label: "Role description", type: "textarea", full: true },
      { name: "Package_LPA", label: "Package (LPA)", type: "number", required: true, min: 0.01, step: 0.01 },
      { name: "Min_CGPA_Requirement", label: "Minimum CGPA", type: "number", required: true, min: 0, max: 10, step: 0.01 },
      { name: "Application_Deadline", label: "Application deadline", type: "date", required: true },
    ],
    initialValues: (lk, rows) => ({ Job_ID: nextId(rows, "Job_ID"), Min_CGPA_Requirement: 0 }),
    editValues: (r) => ({ ...r, Application_Deadline: toInputDate(r.Application_Deadline) }),
    toPayload: (v) => ({ Job_ID: v.Job_ID, Drive_ID: Number(v.Drive_ID), Job_Title: v.Job_Title, Role_Description: v.Role_Description, Package_LPA: v.Package_LPA, Min_CGPA_Requirement: v.Min_CGPA_Requirement, Application_Deadline: sendDate(v.Application_Deadline, DATE_STYLE()) }),
    create: (p) => api.post("/api/jobs", p),
    update: (row, p) => api.put("/api/jobs/" + row.Job_ID, p),
    remove: (row) => api.del("/api/jobs/" + row.Job_ID),
    describe: (r) => "“" + r.Job_Title + "” (ID " + r.Job_ID + ").",
  });

  /* ---------- Interview rounds ---------- */
  const roundsPage = A.crudPage({
    title: "Interview rounds", subtitle: "The stages for each job posting.", singular: "interview round", createLabel: "New round",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    deleteHint: "Rounds that already have results can't be deleted.",
    load: async () => {
      const [rows, jobs] = await Promise.all([get("/api/interview-rounds"), get("/api/jobs")]);
      return { rows, lookups: { jobs, jm: byId(jobs, "Job_ID") } };
    },
    columns: (lk) => [
      { label: "ID", render: (r) => idCell(r.Round_ID) },
      { label: "Job", render: (r) => h("span", { class: "cell-main" }, L.job(lk.jm)(r.Job_ID)) },
      { label: "Order", num: true, render: (r) => r.Round_Number },
      { label: "Type", render: (r) => r.Round_Type },
    ],
    searchText: (r, lk) => [r.Round_ID, L.job(lk.jm)(r.Job_ID), r.Round_Type].join(" "),
    filters: (lk) => [{ label: "All jobs", options: lk.jobs.map((j) => ({ value: j.Job_ID, label: j.Job_Title })), match: (r, v) => String(r.Job_ID) === v }],
    fields: (lk, mode) => [
      { name: "Round_ID", label: "Round ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
      { name: "Job_ID", label: "Job", type: "select", required: true, options: lk.jobs.map((j) => ({ value: j.Job_ID, label: j.Job_ID + " · " + j.Job_Title })) },
      { name: "Round_Number", label: "Round order", type: "number", required: true, min: 0, step: 1, hint: "Lower numbers run first (0, 1, 2…)." },
      { name: "Round_Type", label: "Round type", required: true, placeholder: "e.g. Aptitude, Technical, HR" },
    ],
    initialValues: (lk, rows) => ({ Round_ID: nextId(rows, "Round_ID") }),
    validate: (v, mode, lk, rows) => rows.some((r) => String(r.Job_ID) === String(v.Job_ID) && Number(r.Round_Number) === Number(v.Round_Number) && !(mode === "edit" && String(r.Round_ID) === String(v.Round_ID))) ? "That job already has a round " + v.Round_Number + "." : null,
    toPayload: (v) => ({ Round_ID: v.Round_ID, Job_ID: Number(v.Job_ID), Round_Number: v.Round_Number, Round_Type: v.Round_Type }),
    create: (p) => api.post("/api/interview-rounds", p),
    update: (row, p) => api.put("/api/interview-rounds/" + row.Round_ID, p),
    remove: (row) => api.del("/api/interview-rounds/" + row.Round_ID),
    describe: (r) => "Round " + r.Round_Number + " (" + r.Round_Type + ").",
  });

  /* ---------- Applications ---------- */
  const applicationsPage = A.crudPage({
    title: "Applications", subtitle: "Every student application.", singular: "application", createLabel: "New application",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    deleteHint: "An application with an offer or interview results can't be deleted until those are removed.",
    load: async () => {
      const [rows, students, jobs] = await Promise.all([get("/api/applications"), get("/api/students"), get("/api/jobs")]);
      return { rows, lookups: { students, jobs, sm: byId(students, "Student_ID"), jm: byId(jobs, "Job_ID") } };
    },
    columns: (lk) => [
      { label: "ID", render: (r) => idCell(r.Application_ID) },
      { label: "Student", render: (r) => withSub(L.student(lk.sm)(r.Student_ID), "ID " + r.Student_ID) },
      { label: "Job", render: (r) => L.job(lk.jm)(r.Job_ID) },
      { label: "Applied on", render: (r) => fmtDate(r.Application_Date) },
      { label: "Status", render: (r) => badge(r.Status) },
    ],
    searchText: (r, lk) => [r.Application_ID, L.student(lk.sm)(r.Student_ID), L.job(lk.jm)(r.Job_ID), r.Status].join(" "),
    filters: (lk) => [
      { label: "All statuses", options: opts(APP_STATUSES), match: (r, v) => r.Status === v },
      { label: "All jobs", options: lk.jobs.map((j) => ({ value: j.Job_ID, label: j.Job_Title })), match: (r, v) => String(r.Job_ID) === v },
    ],
    fields: (lk, mode) => [
      { name: "Application_ID", label: "Application ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
      { name: "Application_Date", label: "Application date", type: "date", required: true },
      { name: "Student_ID", label: "Student", type: "select", required: true, options: lk.students.map((s) => ({ value: s.Student_ID, label: s.Student_ID + " · " + s.Name })) },
      { name: "Job_ID", label: "Job", type: "select", required: true, options: lk.jobs.map((j) => ({ value: j.Job_ID, label: j.Job_ID + " · " + j.Job_Title })) },
      { name: "Status", label: "Status", type: "select", required: true, options: opts(APP_STATUSES) },
    ],
    initialValues: (lk, rows) => ({ Application_ID: nextId(rows, "Application_ID"), Application_Date: todayISO(), Status: "APPLIED" }),
    editValues: (r) => ({ ...r, Application_Date: toInputDate(r.Application_Date) }),
    toPayload: (v) => ({ Application_ID: v.Application_ID, Student_ID: Number(v.Student_ID), Job_ID: Number(v.Job_ID), Application_Date: v.Application_Date, Status: v.Status }),
    create: (p) => api.post("/api/applications", p),
    update: (row, p) => api.put("/api/applications/" + row.Application_ID, p),
    remove: (row) => api.del("/api/applications/" + row.Application_ID),
    describe: (r, lk) => "Application " + r.Application_ID + " by " + L.student(lk.sm)(r.Student_ID) + ".",
  });

  /* ---------- Interview results ---------- */
  const resultsPage = A.crudPage({
    title: "Interview results", subtitle: "Pass or fail for each candidate in each round.", singular: "interview result", createLabel: "Record result",
    canCreate: true, canEdit: true, canDelete: true, errorHint: "Each application can have one result per round.",
    load: async () => {
      const [rows, rounds, applications, jobs, students] = await Promise.all([get("/api/interview-results"), get("/api/interview-rounds"), get("/api/applications"), get("/api/jobs"), get("/api/students")]);
      return { rows, lookups: { rounds, applications, jobs, rm: byId(rounds, "Round_ID"), am: byId(applications, "Application_ID"), jm: byId(jobs, "Job_ID"), sm: byId(students, "Student_ID") } };
    },
    columns: (lk) => [
      { label: "Application", render: (r) => { const a = lk.am[r.Application_ID]; return withSub(a ? L.student(lk.sm)(a.Student_ID) : "Application " + r.Application_ID, "#" + r.Application_ID); } },
      { label: "Job", render: (r) => { const a = lk.am[r.Application_ID]; return a ? L.job(lk.jm)(a.Job_ID) : "—"; } },
      { label: "Round", render: (r) => { const rd = lk.rm[r.Round_ID]; return rd ? "Round " + rd.Round_Number + " · " + rd.Round_Type : "Round " + r.Round_ID; } },
      { label: "Result", render: (r) => badge(r.Result) },
    ],
    searchText: (r, lk) => { const a = lk.am[r.Application_ID]; return [r.Application_ID, r.Round_ID, r.Result, a ? L.student(lk.sm)(a.Student_ID) : "", a ? L.job(lk.jm)(a.Job_ID) : ""].join(" "); },
    filters: () => [{ label: "All results", options: opts(RESULTS), match: (r, v) => r.Result === v }],
    formNote: (mode) => (mode === "edit" ? "Only the result can be changed. To move a result to another round or application, delete it and record a new one." : null),
    fields: (lk, mode) => [
      { name: "Round_ID", label: "Round", type: "select", required: true, readOnly: mode === "edit", full: true, options: lk.rounds.map((r) => ({ value: r.Round_ID, label: L.job(lk.jm)(r.Job_ID) + " · Round " + r.Round_Number + " · " + r.Round_Type })) },
      { name: "Application_ID", label: "Application", type: "select", required: true, readOnly: mode === "edit", full: true, options: lk.applications.map((a) => ({ value: a.Application_ID, label: "#" + a.Application_ID + " · " + L.student(lk.sm)(a.Student_ID) + " · " + L.job(lk.jm)(a.Job_ID) })) },
      { name: "Result", label: "Result", type: "select", required: true, options: opts(RESULTS) },
    ],
    initialValues: () => ({ Result: "PENDING" }),
    validate: (v, mode, lk) => {
      if (mode === "edit") return null;
      const rd = lk.rm[v.Round_ID];
      const ap = lk.am[v.Application_ID];
      return rd && ap && rd.Job_ID !== ap.Job_ID ? "That application is for a different job than the round you picked." : null;
    },
    toPayload: (v, mode) => (mode === "create" ? { Round_ID: Number(v.Round_ID), Application_ID: Number(v.Application_ID), Result: v.Result } : { Result: v.Result }),
    create: (p) => api.post("/api/interview-results", p),
    update: (row, p) => api.put("/api/interview-results/" + row.Round_ID + "/" + row.Application_ID, p),
    remove: (row) => api.del("/api/interview-results/" + row.Round_ID + "/" + row.Application_ID),
    describe: (r) => "Result for application " + r.Application_ID + " in round " + r.Round_ID + ".",
  });

  /* ---------- Offers ---------- */
  const offersPage = A.crudPage({
    title: "Offers", subtitle: "Job offers made to students. Each application can have one offer.", singular: "offer", createLabel: "New offer",
    canCreate: true, canEdit: true, canDelete: true, errorHint: ERR_HINT,
    load: async () => {
      const [rows, applications, jobs, students] = await Promise.all([get("/api/offers"), get("/api/applications"), get("/api/jobs"), get("/api/students")]);
      return { rows, lookups: { applications, jobs, am: byId(applications, "Application_ID"), jm: byId(jobs, "Job_ID"), sm: byId(students, "Student_ID") } };
    },
    columns: (lk) => [
      { label: "ID", render: (r) => idCell(r.Offer_ID) },
      { label: "Student", render: (r) => { const a = lk.am[r.Application_ID]; return withSub(a ? L.student(lk.sm)(a.Student_ID) : "Application " + r.Application_ID, "Application #" + r.Application_ID); } },
      { label: "Job", render: (r) => { const a = lk.am[r.Application_ID]; return a ? L.job(lk.jm)(a.Job_ID) : "—"; } },
      { label: "Offered on", render: (r) => fmtDate(r.Offer_Date) },
      { label: "Package", num: true, render: (r) => fmtLPA(r.Offered_Package_LPA) },
      { label: "Status", render: (r) => badge(r.Offer_Status) },
    ],
    searchText: (r, lk) => { const a = lk.am[r.Application_ID]; return [r.Offer_ID, r.Application_ID, a ? L.student(lk.sm)(a.Student_ID) : "", a ? L.job(lk.jm)(a.Job_ID) : ""].join(" "); },
    filters: () => [{ label: "All statuses", options: opts(OFFER_STATUSES), match: (r, v) => r.Offer_Status === v }],
    formNote: (mode) => (mode === "edit" ? "The application an offer belongs to can't be changed." : null),
    fields: (lk, mode, row, rows) => {
      const taken = new Set(rows.map((o) => o.Application_ID));
      const eligible = mode === "edit" ? lk.applications.filter((a) => a.Application_ID === row.Application_ID) : lk.applications.filter((a) => !taken.has(a.Application_ID));
      return [
        { name: "Offer_ID", label: "Offer ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
        { name: "Application_ID", label: "Application", type: "select", required: true, readOnly: mode === "edit", full: true, options: eligible.map((a) => ({ value: a.Application_ID, label: "#" + a.Application_ID + " · " + L.student(lk.sm)(a.Student_ID) + " · " + L.job(lk.jm)(a.Job_ID) + " (" + titleCase(a.Status) + ")" })), hint: mode === "create" && !eligible.length ? "Every application already has an offer." : null },
        { name: "Offer_Date", label: "Offer date", type: "date", required: true },
        { name: "Offered_Package_LPA", label: "Package (LPA)", type: "number", required: true, min: 0.01, step: 0.01 },
        { name: "Offer_Status", label: "Status", type: "select", required: true, options: opts(OFFER_STATUSES) },
      ];
    },
    onFormChange: (raw, form, mode, lk) => {
      if (mode !== "create" || !raw.Application_ID) return;
      const a = lk.am[raw.Application_ID];
      const j = a && lk.jm[a.Job_ID];
      if (j && !form.refs.Offered_Package_LPA.input.value) form.setValue("Offered_Package_LPA", j.Package_LPA);
    },
    initialValues: (lk, rows) => ({ Offer_ID: nextId(rows, "Offer_ID"), Offer_Date: todayISO(), Offer_Status: "PENDING" }),
    editValues: (r) => ({ ...r, Offer_Date: toInputDate(r.Offer_Date) }),
    toPayload: (v) => ({ Offer_ID: v.Offer_ID, Application_ID: Number(v.Application_ID), Offer_Date: v.Offer_Date, Offered_Package_LPA: v.Offered_Package_LPA, Offer_Status: v.Offer_Status }),
    create: (p) => api.post("/api/offers", p),
    update: (row, p) => api.put("/api/offers/" + row.Offer_ID, p),
    remove: (row) => api.del("/api/offers/" + row.Offer_ID),
    describe: (r) => "Offer " + r.Offer_ID + ".",
  });

  /* ---------- Users ---------- */
  const usersPage = (ctx) =>
    A.crudPage({
      title: "User accounts", subtitle: "Logins for students, recruiters and admins.", singular: "user", createLabel: "New user",
      canCreate: true, canEdit: true, canDelete: (r) => r.User_ID !== ctx.user.user_id, errorHint: "Check that the user ID and username aren't already taken.",
      load: async () => {
        const [rows, students, companies] = await Promise.all([get("/api/users"), get("/api/students"), get("/api/companies")]);
        return { rows, lookups: { students, companies, sm: byId(students, "Student_ID"), cm: byId(companies, "Company_ID") } };
      },
      columns: (lk) => [
        { label: "ID", render: (r) => idCell(r.User_ID) },
        { label: "Username", render: (r) => h("span", { class: "cell-main" }, r.Username, r.User_ID === ctx.user.user_id ? h("span", { class: "chip", style: "margin-left:8px" }, "You") : null) },
        { label: "Role", render: (r) => h("span", { class: "chip" }, titleCase(r.Role)) },
        { label: "Linked to", render: (r) => (r.Student_ID ? L.student(lk.sm)(r.Student_ID) + " (student " + r.Student_ID + ")" : r.Company_ID ? L.company(lk.cm)(r.Company_ID) + " (company " + r.Company_ID + ")" : "—") },
      ],
      searchText: (r, lk) => [r.User_ID, r.Username, r.Role, r.Student_ID ? L.student(lk.sm)(r.Student_ID) : "", r.Company_ID ? L.company(lk.cm)(r.Company_ID) : ""].join(" "),
      filters: () => [{ label: "All roles", options: opts(ROLES), match: (r, v) => r.Role === v }],
      formNote: (mode) => (mode === "edit" ? "Leave the password blank to keep the current one." : null),
      fields: (lk, mode) => [
        { name: "User_ID", label: "User ID", type: "number", required: true, readOnly: mode === "edit", min: 1 },
        { name: "Username", label: "Username", required: true },
        { name: "Password", label: mode === "edit" ? "New password" : "Password", type: "password", required: mode === "create", hint: mode === "edit" ? "Optional." : "Share it with the user securely." },
        { name: "Role", label: "Role", type: "select", required: true, options: opts(ROLES) },
        { name: "Student_ID", label: "Student", type: "select", showIf: (v) => v.Role === "STUDENT", options: lk.students.map((s) => ({ value: s.Student_ID, label: s.Student_ID + " · " + s.Name })) },
        { name: "Company_ID", label: "Company", type: "select", showIf: (v) => v.Role === "RECRUITER", options: lk.companies.map((c) => ({ value: c.Company_ID, label: c.Company_ID + " · " + c.Company_Name })) },
      ],
      initialValues: (lk, rows) => ({ User_ID: nextId(rows, "User_ID") }),
      validate: (v) => (v.Role === "STUDENT" && !v.Student_ID ? "Pick the student this account belongs to." : v.Role === "RECRUITER" && !v.Company_ID ? "Pick the company this account belongs to." : null),
      toPayload: (v, mode) => {
        const p = { Username: v.Username, Role: v.Role, Student_ID: v.Role === "STUDENT" ? Number(v.Student_ID) : null, Company_ID: v.Role === "RECRUITER" ? Number(v.Company_ID) : null };
        if (v.Password) p.Password = v.Password;
        return mode === "create" ? { User_ID: v.User_ID, ...p } : p;
      },
      create: (p) => api.post("/api/users", p),
      update: (row, p) => api.put("/api/users/" + row.User_ID, p),
      remove: (row) => api.del("/api/users/" + row.User_ID),
      describe: (r) => "Account “" + r.Username + "”.",
    });

  A.mountApp({
    role: "ADMIN",
    pages: [
      { id: "dashboard", label: "Overview", icon: "grid", render: dashboard },
      { sep: true },
      { id: "students", label: "Students", icon: "cap", render: studentsPage },
      { id: "companies", label: "Companies", icon: "building", render: companiesPage },
      { sep: true },
      { id: "drives", label: "Drives", icon: "calendar", render: drivesPage },
      { id: "jobs", label: "Job postings", icon: "briefcase", render: jobsPage },
      { id: "rounds", label: "Interview rounds", icon: "flag", render: roundsPage },
      { sep: true },
      { id: "applications", label: "Applications", icon: "file", render: applicationsPage },
      { id: "results", label: "Interview results", icon: "rows", render: resultsPage },
      { id: "offers", label: "Offers", icon: "gift", render: offersPage },
      { sep: true },
      { id: "users", label: "User accounts", icon: "key", render: (c, ctx) => usersPage(ctx)(c, ctx) },
    ],
  });
})();
