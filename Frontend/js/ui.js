/* UI helpers: DOM builder, icons, formatting, toast, modal, forms. */
(function () {
  const A = (window.APMS = window.APMS || {});

  /* ---------- DOM builder ---------- */
  const PROPS = ["value", "checked", "disabled", "selected", "readOnly"];

  function append(el, kid) {
    if (kid === null || kid === undefined || kid === false || kid === true) return;
    if (Array.isArray(kid)) return kid.forEach((k) => append(el, k));
    if (kid instanceof Node) return el.appendChild(kid);
    el.appendChild(document.createTextNode(String(kid)));
  }

  function h(tag, attrs) {
    const el = document.createElement(tag);
    if (attrs) {
      for (const k of Object.keys(attrs)) {
        const v = attrs[k];
        if (v === null || v === undefined || v === false) continue;
        if (k === "class") el.className = v;
        else if (k === "dataset") Object.assign(el.dataset, v);
        else if (k.slice(0, 2) === "on" && typeof v === "function") el.addEventListener(k.slice(2).toLowerCase(), v);
        else if (PROPS.indexOf(k) !== -1) el[k] = v;
        else el.setAttribute(k, v === true ? "" : v);
      }
    }
    for (let i = 2; i < arguments.length; i++) append(el, arguments[i]);
    return el;
  }

  function clear(el) {
    while (el.firstChild) el.removeChild(el.firstChild);
    return el;
  }

  /* ---------- Icons ---------- */
  const ICONS = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    briefcase: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>',
    file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 3-6 6.5-6s6.5 2.4 6.5 6M16 4.5a3.5 3.5 0 0 1 0 7M18 14.3c2.2.7 3.5 2.6 3.5 5.7"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    building: '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 8h2M13 8h2M9 12h2M13 12h2M10 21v-4h4v4"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    flag: '<path d="M5 21V4M5 4h12l-2 4 2 4H5"/>',
    gift: '<rect x="3" y="9" width="18" height="12" rx="1"/><path d="M12 9v12M3 13h18M12 9c-2-4-6-4-6-1.5S9 9 12 9zm0 0c2-4 6-4 6-1.5S15 9 12 9z"/>',
    key: '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    x: '<path d="M6 6l12 12M18 6L6 18"/>',
    cap: '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5"/>',
    shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
    rows: '<path d="M9 6h12M9 12h12M9 18h12M3.5 6l1 1 2-2M3.5 12l1 1 2-2M3.5 18l1 1 2-2"/>',
    out: '<path d="M9 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h4M16 8l4 4-4 4M20 12H9"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  };

  function icon(name) {
    const t = document.createElement("template");
    t.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (ICONS[name] || "") +
      "</svg>";
    return t.content.firstChild;
  }

  /* ---------- Formatting ---------- */
  const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

  function parseDate(v) {
    if (v === null || v === undefined || v === "") return null;
    const d = new Date(v);
    return isNaN(d.getTime()) ? null : d;
  }
  // The backend serialises Oracle DATEs as midnight GMT, so read them in UTC
  // to avoid shifting the day in other time zones.
  function fmtDate(v) {
    const d = parseDate(v);
    if (!d) return "—";
    return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" });
  }
  function toInputDate(v) {
    const d = parseDate(v);
    return d ? d.toISOString().slice(0, 10) : "";
  }
  function todayISO() {
    return new Date().toLocaleDateString("en-CA");
  }
  function daysUntil(v) {
    const iso = toInputDate(v);
    if (!iso) return null;
    return Math.round((Date.parse(iso) - Date.parse(todayISO())) / 86400000);
  }
  // style: "iso" -> 2026-10-20, "oracle" -> 20-OCT-2026
  function sendDate(iso, style) {
    if (!iso) return null;
    if (style === "iso") return iso;
    const p = iso.split("-");
    if (p.length !== 3) return iso;
    return p[2] + "-" + MONTHS[parseInt(p[1], 10) - 1] + "-" + p[0];
  }
  function fmtLPA(n) {
    if (n === null || n === undefined || n === "") return "—";
    const x = Number(n);
    return isNaN(x) ? "—" : "₹" + (Math.round(x * 100) / 100) + " LPA";
  }
  function fmtNum(n, digits) {
    if (n === null || n === undefined || n === "") return "—";
    const x = Number(n);
    return isNaN(x) ? "—" : digits === undefined ? String(x) : x.toFixed(digits);
  }
  function titleCase(s) {
    if (!s) return "";
    return String(s).charAt(0).toUpperCase() + String(s).slice(1).toLowerCase();
  }
  function badge(status) {
    const s = String(status || "").toLowerCase();
    return h("span", { class: "badge b-" + s }, titleCase(status) || "—");
  }

  function maxId(rows, field) {
    let m = 0;
    (rows || []).forEach((r) => {
      const v = Number(r[field]);
      if (!isNaN(v) && v > m) m = v;
    });
    return m;
  }
  // Admin: next free id across the whole table.
  function nextId(rows, field) {
    return maxId(rows, field) + 1;
  }
  // Recruiter: ids are global primary keys but recruiters only see their own
  // rows, so each company gets its own block (company 201 -> 2010001, 2010002, ...).
  function scopedNextId(rows, field, companyId) {
    const base = Number(companyId) * 10000;
    let m = base;
    (rows || []).forEach((r) => {
      const v = Number(r[field]);
      if (!isNaN(v) && v > m && v < base + 10000) m = v;
    });
    return m + 1;
  }

  /* ---------- Toast ---------- */
  function toast(message, type) {
    let box = document.querySelector(".toasts");
    if (!box) {
      box = h("div", { class: "toasts", role: "status", "aria-live": "polite" });
      document.body.appendChild(box);
    }
    const t = h("div", { class: "toast" + (type === "error" ? " error" : "") }, message);
    box.appendChild(t);
    setTimeout(() => t.remove(), type === "error" ? 6500 : 3500);
  }

  /* ---------- Modal ---------- */
  function openModal(opts) {
    const prevFocus = document.activeElement;
    const overlay = h("div", { class: "overlay" });
    const errorBox = h("div", { class: "form-error hidden", role: "alert" });
    const foot = h("div", { class: "modal-foot" });
    const modal = h(
      "div",
      { class: "modal" + (opts.narrow ? " narrow" : ""), role: "dialog", "aria-modal": "true", "aria-label": opts.title },
      h(
        "div",
        { class: "modal-head" },
        h("h2", null, opts.title),
        h("button", { class: "modal-x", type: "button", "aria-label": "Close", onClick: () => api.close() }, "×")
      ),
      h("div", { class: "modal-body" }, errorBox, opts.body),
      foot
    );
    overlay.appendChild(modal);

    const api = {
      el: modal,
      close() {
        document.removeEventListener("keydown", onKey);
        overlay.remove();
        if (prevFocus && prevFocus.focus) prevFocus.focus();
      },
      error(msg) {
        if (msg) {
          errorBox.textContent = msg;
          errorBox.classList.remove("hidden");
          errorBox.scrollIntoView({ block: "nearest" });
        } else errorBox.classList.add("hidden");
      },
    };
    function onKey(e) {
      if (e.key === "Escape") api.close();
    }
    document.addEventListener("keydown", onKey);
    overlay.addEventListener("mousedown", (e) => {
      if (e.target === overlay && !opts.persistent) api.close();
    });

    (opts.actions || []).forEach((a) => {
      const btn = h("button", { class: "btn" + (a.kind ? " btn-" + a.kind : ""), type: "button" }, a.label);
      btn.addEventListener("click", async () => {
        if (btn.disabled) return;
        const all = foot.querySelectorAll("button");
        all.forEach((b) => (b.disabled = true));
        api.error(null);
        try {
          await a.onClick(api);
        } catch (e) {
          api.error(e.message || "Something went wrong.");
        } finally {
          all.forEach((b) => (b.disabled = false));
        }
      });
      foot.appendChild(btn);
    });
    if (!(opts.actions || []).length) foot.classList.add("hidden");

    document.body.appendChild(overlay);
    const first = modal.querySelector("input:not([readonly]):not([type=hidden]), select, textarea");
    (first || modal.querySelector(".modal-x")).focus();
    return api;
  }

  function confirmDialog(opts) {
    return new Promise((resolve) => {
      let done = false;
      const finish = (v) => {
        if (!done) {
          done = true;
          resolve(v);
        }
      };
      const m = openModal({
        title: opts.title,
        narrow: true,
        body: h("p", null, opts.message),
        actions: [
          { label: "Cancel", onClick: (mm) => { finish(false); mm.close(); } },
          { label: opts.confirmLabel || "Confirm", kind: opts.danger ? "danger" : "primary", onClick: (mm) => { finish(true); mm.close(); } },
        ],
      });
      const x = m.el.querySelector(".modal-x");
      const origClose = m.close;
      m.close = function () { finish(false); origClose(); };
      x.onclick = () => m.close();
    });
  }

  /* ---------- Forms ---------- */
  let formSeq = 0;
  /*
   * fields: [{name,label,type,required,options,readOnly,hint,full,min,max,step,placeholder,showIf(values)}]
   * type: text | email | url | tel | number | date | password | textarea | select
   */
  function buildForm(fields, values, onChange) {
    values = values || {};
    const uid = "f" + ++formSeq + "_";
    const wrap = h("div", { class: "form-grid" });
    const refs = {};

    fields.forEach((f) => {
      const id = uid + f.name;
      let input;
      const cur = values[f.name];
      if (f.type === "select") {
        input = h("select", { class: "input", id, name: f.name, disabled: !!f.readOnly });
        const opts = f.options || [];
        const hasCur = cur !== null && cur !== undefined && cur !== "";
        if (!f.required || !hasCur) input.appendChild(h("option", { value: "" }, f.placeholder || "Select…"));
        opts.forEach((o) => input.appendChild(h("option", { value: String(o.value) }, o.label)));
        if (hasCur) input.value = String(cur);
      } else if (f.type === "textarea") {
        input = h("textarea", { class: "input", id, name: f.name, readOnly: !!f.readOnly, placeholder: f.placeholder });
        input.value = cur === null || cur === undefined ? "" : cur;
      } else {
        input = h("input", {
          class: "input",
          id,
          name: f.name,
          type: f.type || "text",
          readOnly: !!f.readOnly,
          min: f.min,
          max: f.max,
          step: f.step,
          placeholder: f.placeholder,
          autocomplete: f.type === "password" ? "new-password" : "off",
        });
        input.value = cur === null || cur === undefined ? "" : cur;
      }
      const field = h(
        "div",
        { class: "field" + (f.full ? " full" : "") },
        h("label", { for: id }, f.label, f.required ? h("span", { class: "req" }, " *") : null),
        input,
        f.hint ? h("div", { class: "hint" }, f.hint) : null
      );
      refs[f.name] = { field, input, def: f };
      wrap.appendChild(field);
    });

    function raw() {
      const out = {};
      fields.forEach((f) => (out[f.name] = refs[f.name].input.value));
      return out;
    }
    function applyVisibility() {
      const r = raw();
      fields.forEach((f) => {
        if (f.showIf) refs[f.name].field.classList.toggle("hidden", !f.showIf(r));
      });
    }
    function visible(f) {
      return !refs[f.name].field.classList.contains("hidden");
    }
    wrap.addEventListener("input", () => { applyVisibility(); if (onChange) onChange(raw()); });
    wrap.addEventListener("change", () => { applyVisibility(); if (onChange) onChange(raw()); });
    applyVisibility();

    function getValues() {
      const out = {};
      fields.forEach((f) => {
        const v = refs[f.name].input.value;
        if (!visible(f)) out[f.name] = null;
        else if (f.type === "number") out[f.name] = v === "" ? null : Number(v);
        else if (f.type === "password") out[f.name] = v;
        else {
          const t = v.trim();
          out[f.name] = t === "" ? null : t;
        }
      });
      return out;
    }
    function validate() {
      const vals = getValues();
      for (const f of fields) {
        if (!visible(f) || f.readOnly) continue;
        const v = vals[f.name];
        if (f.required && (v === null || v === "")) return f.label + " is required.";
        if (v !== null && f.type === "number") {
          if (isNaN(v)) return f.label + " must be a number.";
          if (f.min !== undefined && v < Number(f.min)) return f.label + " must be at least " + f.min + ".";
          if (f.max !== undefined && v > Number(f.max)) return f.label + " must be at most " + f.max + ".";
        }
        if (v && f.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) return "Enter a valid email address for " + f.label + ".";
      }
      return null;
    }
    function setValue(name, v) {
      refs[name].input.value = v === null || v === undefined ? "" : v;
      applyVisibility();
    }
    return { el: wrap, getValues, validate, setValue, refs };
  }

  /* ---------- Small view helpers ---------- */
  function loading(text) {
    return h("div", { class: "loading" }, h("span", { class: "spinner" }), text || "Loading…");
  }
  function empty(title, text, action) {
    return h("div", { class: "empty" }, h("h3", null, title), text ? h("p", null, text) : null, action || null);
  }
  function pageHead(title, subtitle, actions) {
    return h(
      "div",
      { class: "page-head" },
      h("div", null, h("h1", null, title), subtitle ? h("p", null, subtitle) : null),
      actions ? h("div", { class: "page-actions" }, actions) : null
    );
  }
  function stat(value, label, highlight) {
    return h("div", { class: "stat" + (highlight ? " hl" : "") }, h("div", { class: "n" }, value), h("div", { class: "l" }, label));
  }
  // counts: {STATUS: n}; order: [STATUS,...]
  function breakdown(counts, order) {
    const total = order.reduce((s, k) => s + (counts[k] || 0), 0);
    if (!total) return h("p", { class: "muted" }, "Nothing to show yet.");
    const bar = h("div", { class: "breakdown-bar", role: "img", "aria-label": order.map((k) => titleCase(k) + " " + (counts[k] || 0)).join(", ") });
    const legend = h("div", { class: "breakdown-legend" });
    order.forEach((k) => {
      const n = counts[k] || 0;
      if (n) bar.appendChild(h("span", { class: "seg-" + k.toLowerCase(), style: "width:" + (n / total) * 100 + "%", title: titleCase(k) + ": " + n }));
      legend.appendChild(h("span", null, h("i", { class: "seg-" + k.toLowerCase() }), titleCase(k) + " ", h("b", null, n)));
    });
    return h("div", null, bar, legend);
  }
  function barRows(items) {
    const max = Math.max.apply(null, items.map((i) => i.value).concat([1]));
    return h(
      "div",
      { class: "bar-rows" },
      items.map((i) =>
        h(
          "div",
          { class: "bar-row" },
          h("div", { class: "name", title: i.label }, i.label),
          h("div", { class: "track" }, h("div", { class: "fill", style: "width:" + (i.value / max) * 100 + "%" })),
          h("div", { class: "v" }, i.value)
        )
      )
    );
  }
  function countBy(rows, field) {
    const out = {};
    (rows || []).forEach((r) => {
      const k = r[field];
      out[k] = (out[k] || 0) + 1;
    });
    return out;
  }
  function byId(rows, field) {
    const m = {};
    (rows || []).forEach((r) => (m[r[field]] = r));
    return m;
  }

  A.ui = {
    h, clear, icon, fmtDate, toInputDate, todayISO, daysUntil, sendDate, fmtLPA, fmtNum, titleCase, badge,
    nextId, scopedNextId, toast, openModal, confirmDialog, buildForm, loading, empty, pageHead, stat,
    breakdown, barRows, countBy, byId, parseDate,
  };
})();
