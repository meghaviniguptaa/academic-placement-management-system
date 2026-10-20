/* App shell: session guard, sidebar, hash router. */
(function () {
  const A = (window.APMS = window.APMS || {});
  const { h, icon, loading, toast } = A.ui;

  const ROLE_META = {
    STUDENT: { folder: "student", login: "../login-student.html", label: "Student portal", mark: "S" },
    RECRUITER: { folder: "recruiter", login: "../login-recruiter.html", label: "Recruiter portal", mark: "R" },
    ADMIN: { folder: "admin", login: "../login-admin.html", label: "Admin console", mark: "A" },
  };

  /*
   * cfg: { role: "STUDENT"|"RECRUITER"|"ADMIN",
   *        pages: [{ id, label, icon, render(container, ctx) } | { sep: true }] }
   */
  async function mountApp(cfg) {
    const meta = ROLE_META[cfg.role];
    document.body.setAttribute("data-role", meta.folder);
    const root = document.getElementById("app");
    root.appendChild(loading("Checking your session…"));

    A.onUnauthorized = () => {
      location.href = meta.login;
    };

    let me;
    try {
      me = await A.auth.me();
    } catch (e) {
      if (e.status === 401) {
        location.href = meta.login;
        return;
      }
      root.innerHTML = "";
      root.appendChild(
        h(
          "div",
          { class: "page" },
          h("div", { class: "notice bad" }, e.message),
          h("p", { style: "margin-top:14px" }, h("a", { href: "", onClick: (ev) => { ev.preventDefault(); location.reload(); } }, "Try again"))
        )
      );
      return;
    }
    if (me.role !== cfg.role) {
      const other = ROLE_META[me.role];
      location.replace(other ? "../" + other.folder + "/" : meta.login);
      return;
    }

    const user = me;
    const pages = cfg.pages.filter((p) => !p.sep);
    const byId = {};
    pages.forEach((p) => (byId[p.id] = p));
    const defaultId = pages[0].id;

    const content = h("main", { class: "page", id: "content", tabindex: "-1" });
    const navEl = h("nav", { class: "nav", "aria-label": "Main" });
    const links = {};
    cfg.pages.forEach((p) => {
      if (p.sep) return navEl.appendChild(h("div", { class: "nav-sep" }));
      const a = h("a", { href: "#/" + p.id }, icon(p.icon), p.label);
      links[p.id] = a;
      navEl.appendChild(a);
    });

    async function signOut() {
      try {
        await A.auth.logout();
      } catch (e) {
        /* session may already be gone */
      }
      location.href = meta.login;
    }

    const sidebar = h(
      "aside",
      { class: "sidebar" },
      h(
        "a",
        { class: "brand", href: "#/" + defaultId },
        h("span", { class: "brand-mark" }, meta.mark),
        h("span", null, h("div", { class: "brand-name" }, "Placement Cell"), h("div", { class: "brand-role" }, meta.label))
      ),
      navEl,
      h(
        "div",
        { class: "sidebar-foot" },
        h("div", { class: "who", title: user.username }, user.username),
        h("div", { class: "faint" }, meta.label),
        h("button", { type: "button", onClick: signOut }, "Sign out")
      )
    );
    const topbar = h(
      "header",
      { class: "topbar" },
      h("button", { type: "button", "aria-label": "Open menu", onClick: () => document.body.classList.toggle("nav-open") }, icon("menu")),
      h("strong", null, "Placement Cell"),
      h("span", { class: "faint" }, meta.label)
    );

    root.innerHTML = "";
    root.appendChild(h("div", { class: "shell" }, sidebar, h("div", { class: "main" }, topbar, content)));
    document.body.addEventListener("click", (e) => {
      if (document.body.classList.contains("nav-open") && !e.target.closest(".sidebar, .topbar button")) {
        document.body.classList.remove("nav-open");
      }
    });

    let token = 0;
    const ctx = {
      user,
      go(id) {
        location.hash = "#/" + id;
      },
      reload() {
        return route();
      },
    };

    async function route() {
      const id = (location.hash.replace(/^#\/?/, "") || defaultId).split("?")[0];
      const page = byId[id] || byId[defaultId];
      document.body.classList.remove("nav-open");
      Object.keys(links).forEach((k) => {
        if (k === page.id) links[k].setAttribute("aria-current", "page");
        else links[k].removeAttribute("aria-current");
      });
      document.title = page.label + " · Placement Cell";
      const my = ++token;
      content.innerHTML = "";
      content.appendChild(loading());
      const holder = h("div");
      try {
        await page.render(holder, ctx);
        if (my !== token) return;
        content.innerHTML = "";
        content.appendChild(holder);
        window.scrollTo(0, 0);
      } catch (e) {
        if (my !== token) return;
        content.innerHTML = "";
        content.appendChild(
          h(
            "div",
            { class: "panel panel-pad" },
            h("h2", null, "Couldn't load this page"),
            h("p", { class: "muted", style: "margin:8px 0 16px" }, e.message || String(e)),
            h("button", { class: "btn", type: "button", onClick: route }, "Try again")
          )
        );
        if (window.console) console.error(e);
      }
    }

    window.addEventListener("hashchange", route);
    await route();
  }

  A.mountApp = mountApp;
})();
