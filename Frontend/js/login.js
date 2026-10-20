/* Shared logic for the three role-specific login pages. */
(function () {
  const A = window.APMS;
  const { h, toast } = A.ui;

  const ROLES = {
    STUDENT: { folder: "student", page: "login-student.html", name: "student" },
    RECRUITER: { folder: "recruiter", page: "login-recruiter.html", name: "recruiter" },
    ADMIN: { folder: "admin", page: "login-admin.html", name: "admin" },
  };

  const expected = document.body.getAttribute("data-expected-role");
  const me = ROLES[expected];
  const form = document.getElementById("login-form");
  const errorBox = document.getElementById("login-error");
  const submit = document.getElementById("login-submit");
  const pw = document.getElementById("password");

  function showError(node) {
    errorBox.textContent = "";
    if (typeof node === "string") errorBox.textContent = node;
    else if (node) errorBox.appendChild(node);
    errorBox.classList.toggle("hidden", !node);
  }

  document.getElementById("pw-toggle").addEventListener("click", (e) => {
    const show = pw.type === "password";
    pw.type = show ? "text" : "password";
    e.currentTarget.textContent = show ? "Hide" : "Show";
    e.currentTarget.setAttribute("aria-pressed", String(show));
  });

  // Already signed in with the right role? Skip the form.
  A.auth
    .me()
    .then((u) => {
      if (u.role === expected) location.replace(me.folder + "/");
    })
    .catch(() => {});

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showError(null);
    const username = form.elements.username.value.trim();
    const password = form.elements.password.value;
    if (!username || !password) return showError("Enter your username and password.");

    submit.disabled = true;
    submit.textContent = "Signing in…";
    try {
      const res = await A.auth.login(username, password);
      const user = res.user;
      if (user.Role !== expected) {
        // Right credentials, wrong door. Don't leave a session behind.
        await A.auth.logout().catch(() => {});
        const actual = ROLES[user.Role];
        showError(
          h(
            "span",
            null,
            "That account is " + (actual && actual.name === "admin" ? "an " : "a ") + (actual ? actual.name : user.Role.toLowerCase()) + " account. ",
            actual ? h("a", { href: actual.page, style: "color:inherit;font-weight:600" }, "Go to the " + actual.name + " login") : null
          )
        );
        return;
      }
      location.href = me.folder + "/";
    } catch (err) {
      showError(err.status === 401 ? "Incorrect username or password." : err.message);
    } finally {
      submit.disabled = false;
      submit.textContent = "Sign in";
    }
  });
})();
