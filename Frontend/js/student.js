/* Student portal */
(function () {
  const A = window.APMS;
  const { h, icon, fmtDate, fmtLPA, fmtNum, badge, toast, openModal, confirmDialog, buildForm, empty, pageHead, stat, breakdown, daysUntil, titleCase } = A.ui;
  const api = A.api;

  const APP_STATUSES = ["APPLIED", "SHORTLISTED", "SELECTED", "REJECTED", "WITHDRAWN"];

  /* ---------- shared helpers ---------- */
  function deadlineChip(v) {
    const d = daysUntil(v);
    if (d === null) return null;
    if (d < 0) return h("span", { class: "chip bad" }, "Closed");
    if (d === 0) return h("span", { class: "chip bad" }, "Closes today");
    if (d <= 3) return h("span", { class: "chip bad" }, d + (d === 1 ? " day left" : " days left"));
    if (d <= 7) return h("span", { class: "chip" }, d + " days left");
    return null;
  }

  async function applyTo(job, profile, appliedSet, after) {
    const ok = await confirmDialog({
      title: "Apply for this job?",
      message: "You're applying for " + job.Job_Title + " at " + job.Company_Name + ". You can't withdraw an application from this portal.",
      confirmLabel: "Apply now",
    });
    if (!ok) return false;
    try {
      await api.post("/api/student/applications", { Job_ID: job.Job_ID });
      appliedSet.add(job.Job_ID);
      toast("Applied for " + job.Job_Title + " at " + job.Company_Name + ".");
      if (after) after();
      return true;
    } catch (e) {
      toast(e.message, "error");
      return false;
    }
  }

  /* ---------- Dashboard ---------- */
  async function dashboard(c) {
    const [dash, profile, apps, jobs] = await Promise.all([
      api.get("/api/student/dashboard"),
      api.get("/api/student/profile"),
      api.get("/api/student/applications"),
      api.get("/api/student/jobs"),
    ]);
    const first = (profile.Name || "").split(" ")[0] || "there";
    c.appendChild(pageHead("Hi, " + first, "Here's where your placement search stands today."));

    c.appendChild(
      h(
        "div",
        { class: "stats" },
        stat(dash.TOTAL_APPLICATIONS || 0, "Applications sent"),
        stat(dash.SHORTLISTED_APPLICATIONS || 0, "Shortlisted"),
        stat(dash.PASSED_ROUNDS || 0, "Interview rounds passed"),
        stat(dash.TOTAL_OFFERS || 0, "Offers received", (dash.TOTAL_OFFERS || 0) > 0),
        stat(dash.ACCEPTED_OFFERS || 0, "Offers accepted")
      )
    );

    const counts = A.ui.countBy(apps, "Status");
    const appliedIds = new Set(apps.map((a) => a.Job_ID));
    const cgpa = Number(profile.CGPA);
    const closing = jobs
      .filter((j) => !appliedIds.has(j.Job_ID) && Number(j.Min_CGPA_Requirement) <= cgpa)
      .map((j) => ({ j, d: daysUntil(j.Application_Deadline) }))
      .filter((x) => x.d !== null && x.d >= 0 && x.d <= 14)
      .sort((a, b) => a.d - b.d)
      .slice(0, 4);

    c.appendChild(
      h(
        "div",
        { class: "grid-2" },
        h("div", { class: "panel panel-pad" }, h("h2", { style: "margin-bottom:14px" }, "Application status"), breakdown(counts, APP_STATUSES)),
        h(
          "div",
          { class: "panel" },
          h("div", { class: "panel-head" }, h("h2", null, "Closing soon"), h("a", { href: "#/jobs" }, "Browse all jobs")),
          closing.length
            ? h(
                "div",
                { class: "job-list" },
                closing.map(({ j, d }) =>
                  h(
                    "div",
                    { class: "job", style: "padding:14px 20px" },
                    h("div", null, h("div", { class: "cell-main" }, j.Job_Title), h("div", { class: "cell-sub" }, j.Company_Name + " · " + fmtLPA(j.Package_LPA))),
                    h("span", { class: "chip" + (d <= 3 ? " bad" : "") }, d === 0 ? "Closes today" : d + (d === 1 ? " day left" : " days left"))
                  )
                )
              )
            : empty("Nothing closing soon", "Jobs you're eligible for and haven't applied to will show up here when their deadline is within two weeks.")
        )
      )
    );

    c.appendChild(
      h(
        "div",
        { class: "panel", style: "margin-top:18px" },
        h("div", { class: "panel-head" }, h("h2", null, "Recent applications"), h("a", { href: "#/applications" }, "View all")),
        apps.length ? applicationsTable(apps.slice(0, 5)) : empty("No applications yet", "Find a role that fits and apply.", h("a", { class: "btn btn-primary", href: "#/jobs" }, "Browse jobs"))
      )
    );
  }

  function applicationsTable(rows) {
    return h(
      "div",
      { class: "table-wrap" },
      h(
        "table",
        { class: "data" },
        h("thead", null, h("tr", null, h("th", null, "Job"), h("th", null, "Applied on"), h("th", null, "Deadline"), h("th", { class: "num" }, "Package"), h("th", null, "Status"))),
        h(
          "tbody",
          null,
          rows.map((a) =>
            h(
              "tr",
              null,
              h("td", null, h("div", { class: "cell-main" }, a.Job_Title), h("div", { class: "cell-sub" }, a.Company_Name)),
              h("td", null, fmtDate(a.Application_Date)),
              h("td", null, fmtDate(a.Application_Deadline)),
              h("td", { class: "num" }, fmtLPA(a.Package_LPA)),
              h("td", null, badge(a.Status))
            )
          )
        )
      )
    );
  }

  /* ---------- Jobs ---------- */
  async function jobsPage(c) {
    const [profile, apps] = await Promise.all([api.get("/api/student/profile"), api.get("/api/student/applications")]);
    const applied = new Set(apps.map((a) => a.Job_ID));
    const cgpa = Number(profile.CGPA);
    const f = { search: "", min: "", max: "", eligibleOnly: false };
    let jobs = [];

    const list = h("div", { class: "job-list" });
    const count = h("span", { class: "muted" });
    const errorBox = h("div", { class: "form-error hidden", style: "margin:14px 16px 0", role: "alert" });

    const search = h("input", { class: "input", type: "search", placeholder: "Search by job title or company", "aria-label": "Search jobs", style: "max-width:300px" });
    const min = h("input", { class: "input", type: "number", min: "0", step: "0.5", placeholder: "Min LPA", "aria-label": "Minimum package in LPA", style: "max-width:120px" });
    const max = h("input", { class: "input", type: "number", min: "0", step: "0.5", placeholder: "Max LPA", "aria-label": "Maximum package in LPA", style: "max-width:120px" });
    const eligible = h("input", { type: "checkbox", id: "elig" });
    const toolbar = h(
      "form",
      { class: "toolbar", onSubmit: (e) => { e.preventDefault(); fetchJobs(); } },
      search, min, max,
      h("button", { class: "btn", type: "submit" }, "Search"),
      h("label", { for: "elig", style: "display:flex;gap:7px;align-items:center;font-size:14px" }, eligible, "Only jobs I qualify for"),
      h("span", { class: "count" }, count)
    );
    eligible.addEventListener("change", draw);

    c.appendChild(pageHead("Open jobs", "Jobs with an open deadline and an upcoming or ongoing drive. Your CGPA is " + fmtNum(profile.CGPA, 2) + "."));
    c.appendChild(h("div", { class: "panel" }, toolbar, errorBox, list));

    async function fetchJobs() {
      errorBox.classList.add("hidden");
      const q = new URLSearchParams();
      if (search.value.trim()) q.set("search", search.value.trim());
      if (min.value !== "") q.set("min_package", min.value);
      if (max.value !== "") q.set("max_package", max.value);
      list.innerHTML = "";
      list.appendChild(A.ui.loading());
      try {
        jobs = await api.get("/api/student/jobs" + (q.toString() ? "?" + q : ""));
      } catch (e) {
        list.innerHTML = "";
        errorBox.textContent = e.message;
        errorBox.classList.remove("hidden");
        return;
      }
      draw();
    }

    function draw() {
      list.innerHTML = "";
      const shown = jobs.filter((j) => !eligible.checked || Number(j.Min_CGPA_Requirement) <= cgpa);
      count.textContent = shown.length + (shown.length === 1 ? " job" : " jobs");
      if (!shown.length) {
        list.appendChild(empty("No jobs found", jobs.length ? "Turn off “Only jobs I qualify for” to see everything that's open." : "Nothing is open right now, or your filters are too narrow."));
        return;
      }
      shown.forEach((j) => list.appendChild(jobRow(j)));
    }

    function jobRow(j) {
      const meets = Number(j.Min_CGPA_Requirement) <= cgpa;
      const isApplied = applied.has(j.Job_ID);
      const right = h("div", { class: "job-side" });
      const row = h(
        "div",
        { class: "job" },
        h(
          "div",
          null,
          h("div", { class: "job-title" }, j.Job_Title),
          h("div", { class: "cell-sub", style: "margin-top:2px" }, j.Company_Name),
          h(
            "div",
            { class: "job-meta" },
            h("span", null, "Apply by ", h("b", null, fmtDate(j.Application_Deadline))),
            h("span", null, "Drive on ", h("b", null, fmtDate(j.Drive_Date))),
            h("span", null, "Min CGPA ", h("b", null, fmtNum(j.Min_CGPA_Requirement, 2)), " ", h("span", { class: "chip " + (meets ? "ok" : "bad") }, meets ? "You qualify" : "Below requirement")),
            deadlineChip(j.Application_Deadline)
          )
        ),
        right
      );
      right.appendChild(h("div", { class: "job-pay" }, fmtLPA(j.Package_LPA).replace(" LPA", ""), h("small", null, "LPA")));
      right.appendChild(h("button", { class: "btn", type: "button", onClick: () => showDetails(j) }, "Details"));
      if (isApplied) right.appendChild(h("span", { class: "badge b-selected" }, "Applied"));
      else
        right.appendChild(
          h("button", { class: "btn btn-primary", type: "button", disabled: !meets, title: meets ? "" : "Your CGPA is below the requirement", onClick: async () => { if (await applyTo(j, profile, applied)) draw(); } }, "Apply")
        );
      return row;
    }

    async function showDetails(j) {
      let d;
      try {
        d = await api.get("/api/student/jobs/" + j.Job_ID);
      } catch (e) {
        return toast(e.message, "error");
      }
      const meets = Number(d.Min_CGPA_Requirement) <= cgpa;
      const isApplied = applied.has(d.Job_ID);
      const actions = [{ label: "Close", onClick: (m) => m.close() }];
      if (!isApplied)
        actions.push({
          label: meets ? "Apply" : "Not eligible",
          kind: "primary",
          onClick: async (m) => {
            if (!meets) return m.error("Your CGPA (" + fmtNum(profile.CGPA, 2) + ") is below the " + fmtNum(d.Min_CGPA_Requirement, 2) + " required for this job.");
            m.close();
            if (await applyTo(d, profile, applied)) draw();
          },
        });
      openModal({
        title: d.Job_Title,
        body: h(
          "dl",
          { class: "kv" },
          h("dt", null, "Company"), h("dd", null, d.Company_Name),
          h("dt", null, "Industry"), h("dd", null, d.Industry || "—"),
          h("dt", null, "Location"), h("dd", null, d.Location || "—"),
          h("dt", null, "About the role"), h("dd", null, d.Role_Description || "No description provided."),
          h("dt", null, "Package"), h("dd", null, fmtLPA(d.Package_LPA)),
          h("dt", null, "Minimum CGPA"), h("dd", null, fmtNum(d.Min_CGPA_Requirement, 2), " ", h("span", { class: "chip " + (meets ? "ok" : "bad") }, meets ? "You qualify" : "Below requirement")),
          h("dt", null, "Apply by"), h("dd", null, fmtDate(d.Application_Deadline)),
          h("dt", null, "Drive"), h("dd", null, fmtDate(d.Drive_Date) + (d.Venue ? " · " + d.Venue : ""), " ", badge(d.Drive_Status)),
          isApplied ? [h("dt", null, "Your status"), h("dd", null, h("span", { class: "badge b-selected" }, "Applied"))] : null
        ),
        actions,
      });
    }

    await fetchJobs();
  }

  /* ---------- Applications ---------- */
  async function applicationsPage(c) {
    const apps = await api.get("/api/student/applications");
    c.appendChild(pageHead("My applications", "Every job you've applied to, newest first."));
    if (!apps.length) {
      c.appendChild(h("div", { class: "panel" }, empty("You haven't applied yet", "Open jobs are waiting on the jobs page.", h("a", { class: "btn btn-primary", href: "#/jobs" }, "Browse jobs"))));
      return;
    }
    const counts = A.ui.countBy(apps, "Status");
    c.appendChild(h("div", { class: "panel panel-pad", style: "margin-bottom:18px" }, breakdown(counts, APP_STATUSES)));

    const holder = h("div");
    const select = h(
      "select",
      { class: "input", "aria-label": "Filter by status", style: "max-width:200px", onChange: draw },
      h("option", { value: "" }, "All statuses"),
      APP_STATUSES.filter((s) => counts[s]).map((s) => h("option", { value: s }, titleCase(s) + " (" + counts[s] + ")"))
    );
    c.appendChild(h("div", { class: "panel" }, h("div", { class: "toolbar" }, select), holder));
    function draw() {
      holder.innerHTML = "";
      const rows = select.value ? apps.filter((a) => a.Status === select.value) : apps;
      holder.appendChild(applicationsTable(rows));
    }
    draw();
  }

  /* ---------- Interviews ---------- */
  function stepStates(rounds) {
    let blocked = false;
    let currentSet = false;
    return rounds.map((r) => {
      const res = String(r.Result || "PENDING").toUpperCase();
      if (blocked) return { r, state: "idle", label: "Not reached" };
      if (res === "PASSED") return { r, state: "passed", label: "Passed" };
      if (res === "FAILED") {
        blocked = true;
        return { r, state: "failed", label: "Not cleared" };
      }
      if (!currentSet) {
        currentSet = true;
        return { r, state: "current", label: "Awaiting result" };
      }
      return { r, state: "idle", label: "Upcoming" };
    });
  }

  async function interviewsPage(c) {
    const [results, apps] = await Promise.all([api.get("/api/student/interview-results"), api.get("/api/student/applications")]);
    c.appendChild(pageHead("Interview rounds", "Each application's rounds, in order. A failed round ends the sequence."));

    const groups = new Map();
    results.forEach((r) => {
      if (!groups.has(r.Application_ID)) groups.set(r.Application_ID, { info: r, rounds: [] });
      groups.get(r.Application_ID).rounds.push(r);
    });
    const appById = A.ui.byId(apps, "Application_ID");

    if (!groups.size) {
      c.appendChild(h("div", { class: "panel" }, empty("No interview rounds yet", "Rounds appear here once a company sets them up for a job you've applied to.")));
    } else {
      const panel = h("div", { class: "panel" });
      groups.forEach((g, appId) => {
        g.rounds.sort((a, b) => a.Round_Number - b.Round_Number);
        const app = appById[appId];
        const steps = stepStates(g.rounds);
        panel.appendChild(
          h(
            "section",
            { class: "app-track" },
            h(
              "div",
              { class: "app-track-head" },
              h("div", null, h("h3", null, g.info.Job_Title), h("div", { class: "cell-sub" }, g.info.Company_Name)),
              app ? badge(app.Status) : null
            ),
            h(
              "ol",
              { class: "pipeline" },
              steps.map(({ r, state, label }) =>
                h(
                  "li",
                  { class: "step " + state },
                  h("span", { class: "dot" }, state === "passed" ? icon("check") : state === "failed" ? icon("x") : null),
                  h("div", { class: "s-name" }, "Round " + r.Round_Number + " · " + r.Round_Type),
                  h("div", { class: "s-res" }, label)
                )
              )
            )
          )
        );
      });
      c.appendChild(panel);
    }

    const waiting = apps.filter((a) => !groups.has(a.Application_ID) && (a.Status === "APPLIED" || a.Status === "SHORTLISTED"));
    if (waiting.length) {
      c.appendChild(
        h(
          "div",
          { class: "panel panel-pad", style: "margin-top:18px" },
          h("h3", { style: "margin-bottom:10px" }, "No rounds announced yet"),
          h("ul", { style: "margin:0;padding-left:18px;color:var(--muted)" }, waiting.map((a) => h("li", null, a.Job_Title + " at " + a.Company_Name + " (" + titleCase(a.Status) + ")")))
        )
      );
    }
  }

  /* ---------- Offers ---------- */
  async function offersPage(c) {
    const offers = await api.get("/api/student/offers");
    c.appendChild(pageHead("My offers", "Offers made against your applications."));
    if (!offers.length) {
      c.appendChild(h("div", { class: "panel" }, empty("No offers yet", "When a company makes you an offer it will show up here.")));
      return;
    }
    const best = Math.max.apply(null, offers.map((o) => Number(o.Offered_Package_LPA) || 0));
    c.appendChild(
      h("div", { class: "stats" }, stat(offers.length, offers.length === 1 ? "Offer" : "Offers"), stat(fmtLPA(best), "Highest package", true), stat(offers.filter((o) => o.Offer_Status === "ACCEPTED").length, "Accepted"))
    );
    c.appendChild(
      h(
        "div",
        { class: "offer-grid" },
        offers.map((o) =>
          h(
            "article",
            { class: "offer" + (o.Offer_Status === "ACCEPTED" ? " accepted" : "") },
            h("div", { style: "display:flex;justify-content:space-between;gap:10px;align-items:flex-start" }, h("div", null, h("h3", null, o.Job_Title), h("div", { class: "cell-sub" }, o.Company_Name)), badge(o.Offer_Status)),
            h("div", { class: "pkg" }, fmtNum(o.Offered_Package_LPA), h("small", null, "LPA")),
            h("div", { class: "cell-sub" }, "Offered on " + fmtDate(o.Offer_Date))
          )
        )
      )
    );
    c.appendChild(h("p", { class: "notice", style: "margin-top:18px" }, "Accepting or declining an offer isn't available in this portal yet."));
  }

  /* ---------- Profile ---------- */
  async function profilePage(c) {
    const p = await api.get("/api/student/profile");
    const fields = [
      { name: "Name", label: "Full name", required: true },
      { name: "Email", label: "Email", type: "email", required: true },
      { name: "Phone", label: "Phone", type: "tel" },
      { name: "Resume_URL", label: "Resume link", type: "url", placeholder: "https://", hint: "A link to your resume (Drive, Dropbox, portfolio…)." },
      { name: "Student_ID", label: "Student ID", readOnly: true },
      { name: "Department", label: "Department", readOnly: true },
      { name: "CGPA", label: "CGPA", readOnly: true },
      { name: "Graduation_Year", label: "Graduation year", readOnly: true },
    ];
    const form = buildForm(fields, p);
    const err = h("div", { class: "form-error hidden", role: "alert" });
    const save = h("button", { class: "btn btn-primary", type: "button" }, "Save changes");
    save.addEventListener("click", async () => {
      err.classList.add("hidden");
      const problem = form.validate();
      if (problem) {
        err.textContent = problem;
        return err.classList.remove("hidden");
      }
      const v = form.getValues();
      save.disabled = true;
      try {
        await api.put("/api/student/profile", { Name: v.Name, Email: v.Email, Phone: v.Phone, Resume_URL: v.Resume_URL });
        toast("Profile saved.");
      } catch (e) {
        err.textContent = e.message;
        err.classList.remove("hidden");
      } finally {
        save.disabled = false;
      }
    });
    c.appendChild(pageHead("My profile", "Update how recruiters can reach you."));
    c.appendChild(
      h(
        "div",
        { class: "panel panel-pad", style: "max-width:760px" },
        err,
        form.el,
        h("p", { class: "muted", style: "font-size:13px;margin-top:14px" }, "Student ID, department, CGPA and graduation year are maintained by the placement cell."),
        h("div", { style: "margin-top:18px" }, save)
      )
    );
  }

  A.mountApp({
    role: "STUDENT",
    pages: [
      { id: "dashboard", label: "Dashboard", icon: "grid", render: dashboard },
      { id: "jobs", label: "Open jobs", icon: "briefcase", render: jobsPage },
      { id: "applications", label: "My applications", icon: "file", render: applicationsPage },
      { id: "interviews", label: "Interview rounds", icon: "flag", render: interviewsPage },
      { id: "offers", label: "My offers", icon: "gift", render: offersPage },
      { sep: true },
      { id: "profile", label: "My profile", icon: "user", render: profilePage },
    ],
  });
})();
