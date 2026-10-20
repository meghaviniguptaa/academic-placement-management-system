/*
 * Generic list + create/edit/delete page, driven by a config object.
 *
 * cfg = {
 *   title, subtitle, singular,                  // "Placement drives", "…", "drive"
 *   load: async () => ({ rows, lookups }),
 *   columns: (lk, rows) => [{ label, render(row) -> Node|string, num?: true }],
 *   fields:  (lk, mode, row, rows) => [field defs for ui.buildForm],
 *   initialValues: (lk, rows) => values for a new record,
 *   editValues:    (row, lk) => values for the edit form (defaults to row),
 *   toPayload:     (values, mode, row, lk) => JSON body,
 *   create: async (payload) => …, update: async (row, payload) => …, remove: async (row) => …,
 *   canCreate, canEdit, canDelete: boolean | (row) => boolean,
 *   rowActions: (row, lk, reload) => [Node],
 *   searchText: (row, lk) => string,
 *   filters: (lk) => [{ label, options: [{value,label}], match(row, value) }],
 *   describe: (row, lk) => string,              // used in the delete confirmation
 *   notice: string | Node, emptyText, createLabel, errorHint, deleteHint
 * }
 */
(function () {
  const A = (window.APMS = window.APMS || {});
  const { h, loading, empty, pageHead, openModal, confirmDialog, buildForm, toast } = A.ui;

  const flag = (v, row) => (typeof v === "function" ? v(row) : v === undefined ? true : v);

  function crudPage(cfg) {
    return async function render(container, ctx) {
      const state = { rows: [], lk: {}, q: "", filters: {} };
      const tableHolder = h("div", { class: "table-wrap" });
      const toolbar = h("div", { class: "toolbar" });
      const panel = h("div", { class: "panel" }, toolbar, tableHolder);
      const newBtn = flag(cfg.canCreate)
        ? h("button", { class: "btn btn-primary", type: "button", onClick: () => openForm("create") }, A.ui.icon("plus"), cfg.createLabel || "New " + cfg.singular)
        : null;

      container.appendChild(pageHead(cfg.title, cfg.subtitle, newBtn));
      if (cfg.notice) container.appendChild(h("div", { class: "notice", style: "margin-bottom:18px" }, cfg.notice));
      container.appendChild(panel);

      async function fetchData() {
        const r = await cfg.load();
        state.rows = r.rows || [];
        state.lk = r.lookups || {};
      }

      function filtered() {
        const q = state.q.trim().toLowerCase();
        const fdefs = cfg.filters ? cfg.filters(state.lk) : [];
        return state.rows.filter((row) => {
          if (q) {
            const text = cfg.searchText ? cfg.searchText(row, state.lk) : Object.values(row).join(" ");
            if (!String(text).toLowerCase().includes(q)) return false;
          }
          for (let i = 0; i < fdefs.length; i++) {
            const val = state.filters[i];
            if (val && !fdefs[i].match(row, val)) return false;
          }
          return true;
        });
      }

      function buildToolbar() {
        toolbar.innerHTML = "";
        const search = h("input", {
          class: "input",
          type: "search",
          placeholder: "Search " + cfg.title.toLowerCase(),
          "aria-label": "Search " + cfg.title.toLowerCase(),
          value: state.q,
          onInput: (e) => {
            state.q = e.target.value;
            drawTable();
          },
        });
        toolbar.appendChild(search);
        (cfg.filters ? cfg.filters(state.lk) : []).forEach((f, i) => {
          const sel = h("select", { class: "input", "aria-label": f.label, onChange: (e) => { state.filters[i] = e.target.value; drawTable(); } },
            h("option", { value: "" }, f.label),
            f.options.map((o) => h("option", { value: String(o.value), selected: String(state.filters[i] || "") === String(o.value) }, o.label)));
          toolbar.appendChild(sel);
        });
        toolbar.appendChild(h("span", { class: "count", id: "crud-count" }));
      }

      function drawTable() {
        const rows = filtered();
        const count = toolbar.querySelector(".count");
        if (count) count.textContent = rows.length + (rows.length === state.rows.length ? "" : " of " + state.rows.length) + " shown";
        tableHolder.innerHTML = "";
        if (!rows.length) {
          const none = !state.rows.length;
          tableHolder.appendChild(
            empty(
              none ? "No " + cfg.title.toLowerCase() + " yet" : "No matches",
              none ? cfg.emptyText || "Records you add will show up here." : "Try a different search or clear the filters.",
              none && flag(cfg.canCreate)
                ? h("button", { class: "btn btn-primary", type: "button", onClick: () => openForm("create") }, cfg.createLabel || "New " + cfg.singular)
                : null
            )
          );
          return;
        }
        const cols = cfg.columns(state.lk, state.rows);
        const hasActions = flag(cfg.canEdit) || flag(cfg.canDelete) || cfg.rowActions;
        const table = h(
          "table",
          { class: "data" },
          h("thead", null, h("tr", null, cols.map((c) => h("th", { class: c.num ? "num" : "" }, c.label)), hasActions ? h("th", { class: "num" }, h("span", { class: "sr-only" }, "Actions")) : null)),
          h(
            "tbody",
            null,
            rows.map((row) =>
              h(
                "tr",
                null,
                cols.map((c) => h("td", { class: c.num ? "num" : "" }, c.render(row))),
                hasActions
                  ? h(
                      "td",
                      { class: "actions" },
                      cfg.rowActions ? cfg.rowActions(row, state.lk, reload) : null,
                      flag(cfg.canEdit, row) ? h("button", { class: "btn btn-sm", type: "button", onClick: () => openForm("edit", row) }, "Edit") : null,
                      flag(cfg.canDelete, row) ? h("button", { class: "btn btn-sm btn-danger", type: "button", onClick: () => onDelete(row) }, "Delete") : null
                    )
                  : null
              )
            )
          )
        );
        tableHolder.appendChild(table);
      }

      async function reload() {
        try {
          await fetchData();
        } catch (e) {
          toast(e.message, "error");
          return;
        }
        buildToolbar();
        drawTable();
      }

      function openForm(mode, row) {
        const lk = state.lk;
        const fields = cfg.fields(lk, mode, row, state.rows);
        const values = mode === "edit" ? (cfg.editValues ? cfg.editValues(row, lk) : row) : cfg.initialValues ? cfg.initialValues(lk, state.rows) : {};
        const form = buildForm(fields, values, (raw) => {
          if (cfg.onFormChange) cfg.onFormChange(raw, form, mode, lk, state.rows);
        });
        const hint = cfg.formNote ? h("p", { class: "muted", style: "margin-bottom:16px;font-size:13.5px" }, typeof cfg.formNote === "function" ? cfg.formNote(mode) : cfg.formNote) : null;
        openModal({
          title: (mode === "edit" ? "Edit " : "New ") + cfg.singular,
          body: h("div", null, hint, form.el),
          actions: [
            { label: "Cancel", onClick: (m) => m.close() },
            {
              label: mode === "edit" ? "Save changes" : cfg.createLabel || "Create " + cfg.singular,
              kind: "primary",
              onClick: async (m) => {
                const problem = form.validate();
                if (problem) return m.error(problem);
                const vals = form.getValues();
                if (cfg.validate) {
                  const p2 = cfg.validate(vals, mode, lk, state.rows);
                  if (p2) return m.error(p2);
                }
                const payload = cfg.toPayload ? cfg.toPayload(vals, mode, row, lk) : vals;
                try {
                  if (mode === "edit") await cfg.update(row, payload);
                  else await cfg.create(payload);
                } catch (e) {
                  const hintTxt = e.status >= 400 && cfg.errorHint ? " " + cfg.errorHint : "";
                  return m.error(e.message + hintTxt);
                }
                m.close();
                toast(mode === "edit" ? "Changes saved." : "Created " + cfg.singular + ".");
                await reload();
              },
            },
          ],
        });
      }

      async function onDelete(row) {
        const ok = await confirmDialog({
          title: "Delete " + cfg.singular + "?",
          message: (cfg.describe ? cfg.describe(row, state.lk) + " " : "") + "This can't be undone.",
          confirmLabel: "Delete",
          danger: true,
        });
        if (!ok) return;
        try {
          await cfg.remove(row);
          toast("Deleted " + cfg.singular + ".");
          await reload();
        } catch (e) {
          toast(e.message + " " + (cfg.deleteHint || "It may still be used by other records, such as applications or offers."), "error");
        }
      }

      container.appendChild(h("div", null)); // keeps container non-empty while loading
      tableHolder.appendChild(loading());
      await fetchData();
      buildToolbar();
      drawTable();
    };
  }

  A.crudPage = crudPage;
})();
