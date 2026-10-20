/* Recruiter portal */
(function () {
  const A = window.APMS;
  const { h, fmtDate, fmtLPA, fmtNum, badge, toast, openModal, confirmDialog, buildForm, empty, pageHead, stat, breakdown, barRows, titleCase, sendDate, toInputDate, todayISO, scopedNextId } = A.ui;
  const api = A.api;
  const DATE_STYLE = () => A.config.PLAIN_DATE_STYLE;

  const APP_STATUSES = ["APPLIED", "SHORTLISTED", "SELECTED", "REJECTED", "WITHDRAWN"];
  const DRIVE_STATUSES = ["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"];
  const OFFER_STATUSES = ["PENDING", "ACCEPTED", "REJECTED"];
  const opts = (list) => list.map((s) => ({ value: s, label: titleCase(s) }));

  const ID_HINT = "Needs to be unique across the whole system. We suggest a number from your company's own range.";
  const ERR_HINT = "Check that the ID isn't already taken and that every value is valid.";

  function companyId(ctx) {
    return ctx.user.company_id;
  }

  async function loadAll() {
    const [drives, jobs, applications, rounds, offers] = await Promise.all([
      api.get("/api/recruiter/drives"),
      api.get("/api/recruiter/jobs"),
      api.get("/api/recruiter/applications"),
      api.get("/api/recruiter/interview-rounds"),
      api.get("/api/recruiter/offers"),
    ]);
    return { drives, jobs, applications, rounds, offers };
  }

  const jobTitle = (jobs) => {
    const m = A.ui.byId(jobs, "Job_ID");
    return (id) => (m[id] ? m[id].Job_Title : "Job " + id);
  };
  const driveLabel = (d) => d.Drive_ID + " · " + fmtDate(d.Drive_Date) + (d.Venue ? " · " + d.Venue : "");

  /* ---------- Dashboard ---------- */
  async function dashboard(c, ctx) {
    const [company, all] = await Promise.all([api.get("/api/recruiter/company"), loadAll()]);
    const { drives, jobs, applications, offers } = all;
    c.appendChild(pageHead(company.Company_Name, "Your hiring activity at a glance."));

    const appCounts = A.ui.countBy(applications, "Status");
    const activeDrives = drives.filter((d) => d.Drive_Status === "UPCOMING" || d.Drive_Status === "ONGOING").length;
    c.appendChild(
      h(
        "div",
        { class: "stats" },
        stat(activeDrives, "Active drives"),
        stat(jobs.length, "Job postings"),
        stat(applications.length, "Applications received"),
        stat(appCounts.APPLIED || 0, "Waiting for review", (appCounts.APPLIED || 0) > 0),
        stat(appCounts.SELECTED || 0, "Selected"),
        stat(offers.length, "Offers made")
      )
    );
    if (appCounts.APPLIED) {
      c.appendChild(
        h("div", { class: "notice warn", style: "margin-bottom:18px" }, appCounts.APPLIED + (appCounts.APPLIED === 1 ? " application is" : " applications are") + " waiting for review. ", h("a", { href: "#/applications" }, "Review applications"))
      );
    }

    const perJob = jobs
      .map((j) => ({ label: j.Job_Title, value: applications.filter((a) => a.Job_ID === j.Job_ID).length }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
    const upcoming = drives
      .filter((d) => d.Drive_Status === "UPCOMING" || d.Drive_Status === "ONGOING")
      .sort((a, b) => new Date(a.Drive_Date) - new Date(b.Drive_Date));

    c.appendChild(
      h(
        "div",
        { class: "grid-2" },
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Applicant pipeline"), breakdown(appCounts, APP_STATUSES)),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Offers"), breakdown(A.ui.countBy(offers, "Offer_Status"), OFFER_STATUSES)),
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Applications per job"), perJob.length ? barRows(perJob) : h("p", { class: "muted" }, "No jobs posted yet.")),
        h(
          "div",
          { class: "panel" },
          h("div", { class: "panel-head" }, h("h2", null, "Upcoming drives"), h("a", { href: "#/drives" }, "Manage")),
          upcoming.length
            ? h("div", { class: "job-list" }, upcoming.slice(0, 5).map((d) => h("div", { class: "job", style: "padding:14px 20px" }, h("div", null, h("div", { class: "cell-main" }, fmtDate(d.Drive_Date)), h("div", { class: "cell-sub" }, d.Venue || "Venue to be announced")), badge(d.Drive_Status))))
            : empty("No upcoming drives", "Create a drive to start receiving applications.", h("a", { class: "btn btn-primary", href: "#/drives" }, "Create a drive"))
        )
      )
    );
  }

  /* ---------- Company profile ---------- */
  async function companyPage(c) {
    const co = await api.get("/api/recruiter/company");
    const form = buildForm(
      [
        { name: "Company_ID", label: "Company ID", readOnly: true },
        { name: "Company_Name", label: "Company name", required: true },
        { name: "Industry", label: "Industry" },
        { name: "Location", label: "Location" },
        { name: "HR_Name", label: "HR contact name", required: true },
        { name: "Contact_Email", label: "Contact email", type: "email", required: true },
      ],
      co
    );
    const err = h("div", { class: "form-error hidden", role: "alert" });
    const save = h("button", { class: "btn btn-primary", type: "button" }, "Save changes");
    save.addEventListener("click", async () => {
      err.classList.add("hidden");
      const p = form.validate();
      if (p) {
        err.textContent = p;
        return err.classList.remove("hidden");
      }
      const v = form.getValues();
      save.disabled = true;
      try {
        await api.put("/api/recruiter/company", { Company_Name: v.Company_Name, Industry: v.Industry, Location: v.Location, HR_Name: v.HR_Name, Contact_Email: v.Contact_Email });
        toast("Company details saved.");
      } catch (e) {
        err.textContent = e.message;
        err.classList.remove("hidden");
      } finally {
        save.disabled = false;
      }
    });
    c.appendChild(pageHead("Company profile", "These details are shown to students on job listings."));
    c.appendChild(h("div", { class: "panel panel-pad", style: "max-width:760px" }, err, form.el, h("div", { style: "margin-top:18px" }, save)));
  }

  /* ---------- Drives ---------- */
  const drivesPage = (ctx) =>
    A.crudPage({
      title: "Placement drives",
      subtitle: "A drive is one visit by your company. Job postings hang off a drive.",
      singular: "drive",
      createLabel: "New drive",
      canCreate: true, canEdit: true, canDelete: true,
      errorHint: ERR_HINT,
      deleteHint: "Delete the drive's job postings first.",
      load: async () => {
        const [rows, jobs] = await Promise.all([api.get("/api/recruiter/drives"), api.get("/api/recruiter/jobs")]);
        return { rows, lookups: { jobs } };
      },
      columns: (lk) => [
        { label: "Drive ID", render: (r) => h("span", { class: "mono" }, r.Drive_ID) },
        { label: "Date", render: (r) => h("span", { class: "cell-main" }, fmtDate(r.Drive_Date)) },
        { label: "Venue", render: (r) => r.Venue || "—" },
        { label: "Jobs", num: true, render: (r) => lk.jobs.filter((j) => j.Drive_ID === r.Drive_ID).length },
        { label: "Status", render: (r) => badge(r.Drive_Status) },
      ],
      searchText: (r) => [r.Drive_ID, r.Venue, r.Drive_Status, fmtDate(r.Drive_Date)].join(" "),
      filters: () => [{ label: "All statuses", options: opts(DRIVE_STATUSES), match: (r, v) => r.Drive_Status === v }],
      fields: (lk, mode) => [
        { name: "Drive_ID", label: "Drive ID", type: "number", required: true, readOnly: mode === "edit", min: 1, hint: mode === "create" ? ID_HINT : null },
        { name: "Drive_Date", label: "Drive date", type: "date", required: true },
        { name: "Venue", label: "Venue", full: true, placeholder: "e.g. Main Auditorium" },
        { name: "Drive_Status", label: "Status", type: "select", required: true, options: opts(DRIVE_STATUSES) },
      ],
      initialValues: (lk, rows) => ({ Drive_ID: scopedNextId(rows, "Drive_ID", companyId(ctx)), Drive_Status: "UPCOMING" }),
      editValues: (r) => ({ ...r, Drive_Date: toInputDate(r.Drive_Date) }),
      toPayload: (v, mode) => {
        const base = { Drive_Date: sendDate(v.Drive_Date, DATE_STYLE()), Venue: v.Venue, Drive_Status: v.Drive_Status };
        return mode === "create" ? { Drive_ID: v.Drive_ID, ...base } : base;
      },
      create: (p) => api.post("/api/recruiter/drives", p),
      update: (row, p) => api.put("/api/recruiter/drives/" + row.Drive_ID, p),
      remove: (row) => api.del("/api/recruiter/drives/" + row.Drive_ID),
      describe: (r) => "Drive " + r.Drive_ID + " on " + fmtDate(r.Drive_Date) + ".",
    });

  /* ---------- Jobs ---------- */
  const jobsPage = (ctx) =>
    A.crudPage({
      title: "Job postings",
      subtitle: "Roles students can apply to. Each one belongs to one of your drives.",
      singular: "job posting",
      createLabel: "New job posting",
      canCreate: true, canEdit: true, canDelete: true,
      errorHint: ERR_HINT,
      deleteHint: "A job with applications or interview rounds can't be deleted until those are removed.",
      load: async () => {
        const [rows, drives] = await Promise.all([api.get("/api/recruiter/jobs"), api.get("/api/recruiter/drives")]);
        return { rows, lookups: { drives } };
      },
      columns: (lk) => {
        const dm = A.ui.byId(lk.drives, "Drive_ID");
        return [
          { label: "Job ID", render: (r) => h("span", { class: "mono" }, r.Job_ID) },
          { label: "Title", render: (r) => h("div", null, h("div", { class: "cell-main" }, r.Job_Title), h("div", { class: "cell-sub" }, dm[r.Drive_ID] ? "Drive on " + fmtDate(dm[r.Drive_ID].Drive_Date) : "Drive " + r.Drive_ID)) },
          { label: "Package", num: true, render: (r) => fmtLPA(r.Package_LPA) },
          { label: "Min CGPA", num: true, render: (r) => fmtNum(r.Min_CGPA_Requirement, 2) },
          { label: "Apply by", render: (r) => fmtDate(r.Application_Deadline) },
        ];
      },
      searchText: (r) => [r.Job_ID, r.Job_Title, r.Role_Description].join(" "),
      notice: null,
      formNote: (mode) => (mode === "edit" ? "A job's drive can't be changed once it's created." : null),
      fields: (lk, mode) => [
        { name: "Job_ID", label: "Job ID", type: "number", required: true, readOnly: mode === "edit", min: 1, hint: mode === "create" ? ID_HINT : null },
        { name: "Drive_ID", label: "Drive", type: "select", required: true, readOnly: mode === "edit", options: lk.drives.map((d) => ({ value: d.Drive_ID, label: driveLabel(d) })), hint: !lk.drives.length ? "Create a drive first." : null },
        { name: "Job_Title", label: "Job title", required: true, full: true },
        { name: "Role_Description", label: "Role description", type: "textarea", full: true },
        { name: "Package_LPA", label: "Package (LPA)", type: "number", required: true, min: 0.01, step: 0.01 },
        { name: "Min_CGPA_Requirement", label: "Minimum CGPA", type: "number", required: true, min: 0, max: 10, step: 0.01 },
        { name: "Application_Deadline", label: "Application deadline", type: "date", required: true },
      ],
      initialValues: (lk, rows) => ({ Job_ID: scopedNextId(rows, "Job_ID", companyId(ctx)), Min_CGPA_Requirement: 0 }),
      editValues: (r) => ({ ...r, Application_Deadline: toInputDate(r.Application_Deadline) }),
      toPayload: (v, mode) => {
        const base = {
          Job_Title: v.Job_Title, Role_Description: v.Role_Description, Package_LPA: v.Package_LPA,
          Min_CGPA_Requirement: v.Min_CGPA_Requirement, Application_Deadline: sendDate(v.Application_Deadline, DATE_STYLE()),
        };
        return mode === "create" ? { Job_ID: v.Job_ID, Drive_ID: Number(v.Drive_ID), ...base } : base;
      },
      create: (p) => api.post("/api/recruiter/jobs", p),
      update: (row, p) => api.put("/api/recruiter/jobs/" + row.Job_ID, p),
      remove: (row) => api.del("/api/recruiter/jobs/" + row.Job_ID),
      describe: (r) => "“" + r.Job_Title + "”.",
    });

  /* ---------- Applications ---------- */
  function openOfferModal(app, all, ctx, done) {
    const jobs = A.ui.byId(all.jobs, "Job_ID");
    const job = jobs[app.Job_ID];
    const form = buildForm(
      [
        { name: "Offer_ID", label: "Offer ID", type: "number", required: true, min: 1, hint: ID_HINT },
        { name: "Offer_Date", label: "Offer date", type: "date", required: true },
        { name: "Offered_Package_LPA", label: "Package (LPA)", type: "number", required: true, min: 0.01, step: 0.01 },
        { name: "Offer_Status", label: "Status", type: "select", required: true, options: opts(OFFER_STATUSES) },
      ],
      { Offer_ID: scopedNextId(all.offers, "Offer_ID", companyId(ctx)), Offer_Date: todayISO(), Offered_Package_LPA: job ? job.Package_LPA : "", Offer_Status: "PENDING" }
    );
    openModal({
      title: "Make an offer",
      body: h("div", null, h("p", { class: "muted", style: "margin-bottom:16px" }, "Student " + app.Student_ID + " · " + app.Job_Title + " (application " + app.Application_ID + ")"), form.el),
      actions: [
        { label: "Cancel", onClick: (m) => m.close() },
        {
          label: "Send offer", kind: "primary",
          onClick: async (m) => {
            const p = form.validate();
            if (p) return m.error(p);
            const v = form.getValues();
            try {
              await api.post("/api/recruiter/offers", { Offer_ID: v.Offer_ID, Application_ID: app.Application_ID, Offer_Date: v.Offer_Date, Offered_Package_LPA: v.Offered_Package_LPA, Offer_Status: v.Offer_Status });
            } catch (e) {
              return m.error(e.message + " " + ERR_HINT);
            }
            m.close();
            toast("Offer created.");
            done();
          },
        },
      ],
    });
  }

  async function applicationsPage(c, ctx) {
    const all = await loadAll();
    const state = { q: "", job: "", status: "" };
    const holder = h("div", { class: "table-wrap" });
    const count = h("span", { class: "count" });

    const search = h("input", { class: "input", type: "search", placeholder: "Search by student or application ID", "aria-label": "Search applications", onInput: (e) => { state.q = e.target.value; draw(); } });
    const jobSel = h("select", { class: "input", "aria-label": "Filter by job", onChange: (e) => { state.job = e.target.value; draw(); } }, h("option", { value: "" }, "All jobs"), all.jobs.map((j) => h("option", { value: j.Job_ID }, j.Job_Title)));
    const statusSel = h("select", { class: "input", "aria-label": "Filter by status", onChange: (e) => { state.status = e.target.value; draw(); } }, h("option", { value: "" }, "All statuses"), APP_STATUSES.map((s) => h("option", { value: s }, titleCase(s))));

    c.appendChild(pageHead("Applications", "Review applicants for your jobs and move them through the pipeline."));
    c.appendChild(h("div", { class: "panel" }, h("div", { class: "toolbar" }, search, jobSel, statusSel, count), holder));

    async function refresh() {
      const [applications, offers] = await Promise.all([api.get("/api/recruiter/applications"), api.get("/api/recruiter/offers")]);
      all.applications = applications;
      all.offers = offers;
      draw();
    }

    async function setStatus(app, status) {
      if (status === app.Status) return;
      const ok = await confirmDialog({
        title: "Change status?",
        message: "Move application " + app.Application_ID + " (student " + app.Student_ID + ") from " + titleCase(app.Status) + " to " + titleCase(status) + ".",
        confirmLabel: "Change to " + titleCase(status),
      });
      if (!ok) return draw();
      try {
        await api.put("/api/recruiter/applications/" + app.Application_ID, { Status: status });
        toast("Application " + app.Application_ID + " is now " + titleCase(status) + ".");
        await refresh();
      } catch (e) {
        toast(e.message, "error");
        draw();
      }
    }

    function draw() {
      const q = state.q.trim().toLowerCase();
      const withOffer = new Set(all.offers.map((o) => o.Application_ID));
      const rows = all.applications.filter(
        (a) => (!q || (a.Application_ID + " " + a.Student_ID + " " + a.Job_Title).toLowerCase().includes(q)) && (!state.job || String(a.Job_ID) === state.job) && (!state.status || a.Status === state.status)
      );
      count.textContent = rows.length + " shown";
      holder.innerHTML = "";
      if (!rows.length) {
        holder.appendChild(all.applications.length ? empty("No matches", "Try a different search or clear the filters.") : empty("No applications yet", "Applications show up here once students apply to your jobs."));
        return;
      }
      holder.appendChild(
        h(
          "table",
          { class: "data" },
          h("thead", null, h("tr", null, ["Application", "Student ID", "Job", "Applied on", "Status", "Change status", ""].map((t) => h("th", null, t)))),
          h(
            "tbody",
            null,
            rows.map((a) => {
              const sel = h("select", { class: "input", style: "min-height:34px;padding:4px 8px;width:auto", "aria-label": "Change status of application " + a.Application_ID, onChange: (e) => setStatus(a, e.target.value) }, APP_STATUSES.map((s) => h("option", { value: s, selected: s === a.Status }, titleCase(s))));
              return h(
                "tr",
                null,
                h("td", { class: "mono" }, "#" + a.Application_ID),
                h("td", { class: "mono" }, a.Student_ID),
                h("td", { class: "cell-main" }, a.Job_Title),
                h("td", null, fmtDate(a.Application_Date)),
                h("td", null, badge(a.Status)),
                h("td", null, sel),
                h("td", { class: "actions" }, a.Status === "SELECTED" && !withOffer.has(a.Application_ID) ? h("button", { class: "btn btn-sm btn-primary", type: "button", onClick: () => openOfferModal(a, all, ctx, refresh) }, "Make offer") : withOffer.has(a.Application_ID) ? h("span", { class: "chip ok" }, "Offer made") : null)
              );
            })
          )
        )
      );
    }
    draw();
  }

  /* ---------- Interview rounds ---------- */
  const roundsPage = (ctx) =>
    A.crudPage({
      title: "Interview rounds",
      subtitle: "The stages candidates go through for each job, in order.",
      singular: "interview round",
      createLabel: "New round",
      canCreate: true, canEdit: true, canDelete: true,
      errorHint: ERR_HINT,
      deleteHint: "Rounds that already have results can't be deleted.",
      notice: "Recording a candidate's pass or fail in a round is handled by the placement admin.",
      load: async () => {
        const [rows, jobs] = await Promise.all([api.get("/api/recruiter/interview-rounds"), api.get("/api/recruiter/jobs")]);
        return { rows, lookups: { jobs } };
      },
      columns: (lk) => {
        const t = jobTitle(lk.jobs);
        return [
          { label: "Round ID", render: (r) => h("span", { class: "mono" }, r.Round_ID) },
          { label: "Job", render: (r) => h("span", { class: "cell-main" }, t(r.Job_ID)) },
          { label: "Order", num: true, render: (r) => r.Round_Number },
          { label: "Type", render: (r) => r.Round_Type },
        ];
      },
      searchText: (r, lk) => [r.Round_ID, jobTitle(lk.jobs)(r.Job_ID), r.Round_Type].join(" "),
      filters: (lk) => [{ label: "All jobs", options: lk.jobs.map((j) => ({ value: j.Job_ID, label: j.Job_Title })), match: (r, v) => String(r.Job_ID) === v }],
      formNote: (mode) => (mode === "edit" ? "A round's job can't be changed once it's created." : null),
      fields: (lk, mode) => [
        { name: "Round_ID", label: "Round ID", type: "number", required: true, readOnly: mode === "edit", min: 1, hint: mode === "create" ? ID_HINT : null },
        { name: "Job_ID", label: "Job", type: "select", required: true, readOnly: mode === "edit", options: lk.jobs.map((j) => ({ value: j.Job_ID, label: j.Job_ID + " · " + j.Job_Title })), hint: !lk.jobs.length ? "Create a job posting first." : null },
        { name: "Round_Number", label: "Round order", type: "number", required: true, min: 0, step: 1, hint: "Lower numbers run first (0, 1, 2…)." },
        { name: "Round_Type", label: "Round type", required: true, placeholder: "e.g. Aptitude, Technical, HR" },
      ],
      initialValues: (lk, rows) => ({ Round_ID: scopedNextId(rows, "Round_ID", companyId(ctx)) }),
      validate: (v, mode, lk, rows) => {
        const clash = rows.some((r) => String(r.Job_ID) === String(v.Job_ID) && Number(r.Round_Number) === Number(v.Round_Number) && !(mode === "edit" && String(r.Round_ID) === String(v.Round_ID)));
        return clash ? "That job already has a round " + v.Round_Number + ". Pick a different order." : null;
      },
      toPayload: (v, mode) => {
        const base = { Job_ID: Number(v.Job_ID), Round_Number: v.Round_Number, Round_Type: v.Round_Type };
        return mode === "create" ? { Round_ID: v.Round_ID, ...base } : base;
      },
      create: (p) => api.post("/api/recruiter/interview-rounds", p),
      update: (row, p) => api.put("/api/recruiter/interview-rounds/" + row.Round_ID, p),
      remove: (row) => api.del("/api/recruiter/interview-rounds/" + row.Round_ID),
      describe: (r) => "Round " + r.Round_Number + " (" + r.Round_Type + ").",
    });

  /* ---------- Offers ---------- */
  const offersPage = (ctx) =>
    A.crudPage({
      title: "Offers",
      subtitle: "Offers you've made. Each application can have one offer.",
      singular: "offer",
      createLabel: "New offer",
      canCreate: true, canEdit: true, canDelete: true,
      errorHint: ERR_HINT,
      load: async () => {
        const [rows, applications, jobs] = await Promise.all([api.get("/api/recruiter/offers"), api.get("/api/recruiter/applications"), api.get("/api/recruiter/jobs")]);
        return { rows, lookups: { applications, jobs } };
      },
      columns: (lk) => {
        const t = jobTitle(lk.jobs);
        return [
          { label: "Offer ID", render: (r) => h("span", { class: "mono" }, r.Offer_ID) },
          { label: "Student ID", render: (r) => h("span", { class: "mono" }, r.Student_ID) },
          { label: "Job", render: (r) => h("span", { class: "cell-main" }, t(r.Job_ID)) },
          { label: "Offered on", render: (r) => fmtDate(r.Offer_Date) },
          { label: "Package", num: true, render: (r) => fmtLPA(r.Offered_Package_LPA) },
          { label: "Status", render: (r) => badge(r.Offer_Status) },
        ];
      },
      searchText: (r, lk) => [r.Offer_ID, r.Student_ID, r.Application_ID, jobTitle(lk.jobs)(r.Job_ID)].join(" "),
      filters: () => [{ label: "All statuses", options: opts(OFFER_STATUSES), match: (r, v) => r.Offer_Status === v }],
      formNote: (mode) => (mode === "edit" ? "The application an offer belongs to can't be changed." : null),
      fields: (lk, mode, row, rows) => {
        const taken = new Set(rows.map((o) => o.Application_ID));
        const t = jobTitle(lk.jobs);
        const eligible = mode === "edit" ? lk.applications.filter((a) => a.Application_ID === row.Application_ID) : lk.applications.filter((a) => !taken.has(a.Application_ID));
        return [
          { name: "Offer_ID", label: "Offer ID", type: "number", required: true, readOnly: mode === "edit", min: 1, hint: mode === "create" ? ID_HINT : null },
          { name: "Application_ID", label: "Application", type: "select", required: true, readOnly: mode === "edit", full: true, options: eligible.map((a) => ({ value: a.Application_ID, label: "#" + a.Application_ID + " · Student " + a.Student_ID + " · " + t(a.Job_ID) + " (" + titleCase(a.Status) + ")" })), hint: mode === "create" && !eligible.length ? "Every application already has an offer, or there are no applications yet." : null },
          { name: "Offer_Date", label: "Offer date", type: "date", required: true },
          { name: "Offered_Package_LPA", label: "Package (LPA)", type: "number", required: true, min: 0.01, step: 0.01 },
          { name: "Offer_Status", label: "Status", type: "select", required: true, options: opts(OFFER_STATUSES) },
        ];
      },
      onFormChange: (raw, form, mode, lk) => {
        if (mode !== "create" || !raw.Application_ID) return;
        const app = lk.applications.find((a) => String(a.Application_ID) === raw.Application_ID);
        const job = app && lk.jobs.find((j) => j.Job_ID === app.Job_ID);
        if (job && !form.refs.Offered_Package_LPA.input.value) form.setValue("Offered_Package_LPA", job.Package_LPA);
      },
      initialValues: (lk, rows) => ({ Offer_ID: scopedNextId(rows, "Offer_ID", companyId(ctx)), Offer_Date: todayISO(), Offer_Status: "PENDING" }),
      editValues: (r) => ({ ...r, Offer_Date: toInputDate(r.Offer_Date) }),
      toPayload: (v, mode) => {
        const base = { Offer_Date: v.Offer_Date, Offered_Package_LPA: v.Offered_Package_LPA, Offer_Status: v.Offer_Status };
        return mode === "create" ? { Offer_ID: v.Offer_ID, Application_ID: Number(v.Application_ID), ...base } : base;
      },
      create: (p) => api.post("/api/recruiter/offers", p),
      update: (row, p) => api.put("/api/recruiter/offers/" + row.Offer_ID, p),
      remove: (row) => api.del("/api/recruiter/offers/" + row.Offer_ID),
      describe: (r) => "Offer " + r.Offer_ID + " for student " + r.Student_ID + ".",
    });

  // crudPage needs the session user for id suggestions, so build pages once the session is known.
  A.mountApp({
    role: "RECRUITER",
    pages: [
      { id: "dashboard", label: "Dashboard", icon: "grid", render: dashboard },
      { id: "applications", label: "Applications", icon: "file", render: applicationsPage },
      { sep: true },
      { id: "drives", label: "Drives", icon: "calendar", render: (c, ctx) => drivesPage(ctx)(c, ctx) },
      { id: "jobs", label: "Job postings", icon: "briefcase", render: (c, ctx) => jobsPage(ctx)(c, ctx) },
      { id: "rounds", label: "Interview rounds", icon: "flag", render: (c, ctx) => roundsPage(ctx)(c, ctx) },
      { id: "offers", label: "Offers", icon: "gift", render: (c, ctx) => offersPage(ctx)(c, ctx) },
      { sep: true },
      { id: "company", label: "Company profile", icon: "building", render: companyPage },
    ],
  });
})();
