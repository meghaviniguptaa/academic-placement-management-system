/*
 * Frontend settings. Edit this file if your setup differs from the defaults.
 */
window.APMS = window.APMS || {};

window.APMS.config = {
  // Leave empty when the page is served by server.py (it proxies /api to the
  // Flask backend, so the session cookie stays same-origin).
  API_BASE: "",

  // How dates are sent for placement drives and job postings.
  // The backend binds these two as plain strings (the other date columns use
  // TO_DATE(..., 'YYYY-MM-DD') on the server).
  //   "oracle" -> "20-OCT-2026"  works with Oracle's default NLS_DATE_FORMAT (DD-MON-RR)
  //   "iso"    -> "2026-10-20"   use this if your database session is set to YYYY-MM-DD
  PLAIN_DATE_STYLE: "oracle",
};
