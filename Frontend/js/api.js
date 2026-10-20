/* Thin fetch wrapper around the Flask backend. */
(function () {
  const A = (window.APMS = window.APMS || {});

  class ApiError extends Error {
    constructor(message, status) {
      super(message);
      this.name = "ApiError";
      this.status = status;
    }
  }

  // The backend builds rows from cursor.description, and Oracle reports
  // unquoted column names in UPPERCASE (STUDENT_ID, COMPANY_NAME, ...), while
  // request bodies use the schema's mixed case (Student_ID, Company_Name, ...).
  // Map known uppercase keys back to the schema spelling so the UI uses one set
  // of names everywhere. Lowercase keys (e.g. /api/auth/me) are left alone.
  const FIELD_NAMES = (
    "Student_ID Name Email Phone Department CGPA Graduation_Year Resume_URL " +
    "Company_ID Company_Name Industry Contact_Email HR_Name Location " +
    "Drive_ID Drive_Date Venue Drive_Status " +
    "Job_ID Job_Title Role_Description Package_LPA Min_CGPA_Requirement Application_Deadline " +
    "Application_ID Application_Date Status " +
    "Round_ID Round_Number Round_Type Result " +
    "Offer_ID Offer_Date Offered_Package_LPA Offer_Status " +
    "User_ID Username Role"
  ).split(" ").reduce((m, n) => ((m[n.toUpperCase()] = n), m), {});

  function normalize(v) {
    if (Array.isArray(v)) return v.map(normalize);
    if (v && typeof v === "object") {
      const out = {};
      Object.keys(v).forEach((k) => {
        const canon = k === k.toUpperCase() && FIELD_NAMES[k] ? FIELD_NAMES[k] : k;
        out[canon] = v[k];
      });
      return out;
    }
    return v;
  }

  async function request(method, url, body, opts) {
    opts = opts || {};
    let res;
    try {
      res = await fetch(A.config.API_BASE + url, {
        method,
        credentials: "same-origin",
        headers: body !== undefined ? { "Content-Type": "application/json" } : {},
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    } catch (e) {
      throw new ApiError(
        "Can't reach the server. Check that the backend and server.py are running.",
        0
      );
    }

    let data = null;
    const text = await res.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (e) {
        data = null; // e.g. Flask's HTML error page
      }
    }

    if (!res.ok) {
      if (res.status === 401 && !opts.noRedirect && typeof A.onUnauthorized === "function") {
        A.onUnauthorized();
      }
      let msg = data && data.message;
      if (!msg) {
        if (res.status === 502 || res.status === 504) msg = "The backend isn't responding.";
        else if (res.status === 404) msg = "Not found.";
        else if (res.status === 405) msg = "That action isn't supported by the backend.";
        else if (res.status >= 500) msg = "The server couldn't complete that request. Check the values and try again.";
        else msg = "Request failed (" + res.status + ").";
      }
      throw new ApiError(msg, res.status);
    }
    return normalize(data);
  }

  A.ApiError = ApiError;
  A.api = {
    get: (url, opts) => request("GET", url, undefined, opts),
    post: (url, body, opts) => request("POST", url, body === undefined ? {} : body, opts),
    put: (url, body, opts) => request("PUT", url, body === undefined ? {} : body, opts),
    del: (url, opts) => request("DELETE", url, undefined, opts),
  };

  A.auth = {
    login: (Username, Password) => A.api.post("/api/auth/login", { Username, Password }, { noRedirect: true }),
    me: () => A.api.get("/api/auth/me", { noRedirect: true }),
    logout: () => A.api.post("/api/auth/logout", {}, { noRedirect: true }),
  };
})();
