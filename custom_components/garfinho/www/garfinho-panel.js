/* Garfinho sidebar panel: search recipes, browse and manage favorites. */

const STYLE = `
  :host { display: block; height: 100%; background: var(--primary-background-color); color: var(--primary-text-color); }
  * { box-sizing: border-box; }
  header { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 16px; background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); position: sticky; top: 0; z-index: 2; }
  header h1 { font-size: 20px; font-weight: 400; margin: 0; flex: 1; }
  header button { background: none; border: 0; color: inherit; cursor: pointer; padding: 8px; border-radius: 50%; display: flex; }
  header button:hover { background: rgba(255,255,255,.12); }
  main { max-width: 1200px; margin: 0 auto; padding: 16px; }
  .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--divider-color); margin-bottom: 16px; }
  .tab { background: none; border: 0; border-bottom: 2px solid transparent; padding: 10px 16px; font: inherit; color: var(--secondary-text-color); cursor: pointer; }
  .tab[active] { color: var(--primary-color); border-color: var(--primary-color); }
  .tab .count { margin-left: 6px; font-size: 12px; background: var(--secondary-background-color); border-radius: 10px; padding: 1px 7px; }
  .controls { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
  input[type=search], select { font: inherit; color: inherit; background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 12px; }
  input[type=search] { flex: 1; min-width: 200px; }
  input:focus, select:focus { outline: 2px solid var(--primary-color); outline-offset: -1px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
  .chip { font: inherit; font-size: 13px; cursor: pointer; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); border-radius: 16px; padding: 4px 12px; }
  .chip[active] { background: var(--primary-color); border-color: var(--primary-color); color: var(--text-primary-color, #fff); }
  .chip small { opacity: .6; margin-left: 4px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
  .card { background: var(--card-background-color); border-radius: var(--ha-card-border-radius, 12px); box-shadow: var(--ha-card-box-shadow, 0 1px 3px rgba(0,0,0,.2)); overflow: hidden; display: flex; flex-direction: column; }
  .photo { position: relative; aspect-ratio: 4 / 3; background: var(--secondary-background-color) center / cover no-repeat; cursor: pointer; }
  .photo.empty { display: grid; place-items: center; color: var(--disabled-text-color); font-size: 40px; }
  .fav { position: absolute; top: 8px; right: 8px; width: 36px; height: 36px; border-radius: 50%; border: 0; cursor: pointer; background: rgba(0,0,0,.45); color: #fff; font-size: 20px; line-height: 1; display: grid; place-items: center; transition: transform .12s; }
  .fav:hover { transform: scale(1.1); }
  .fav[on] { background: #e91e63; }
  .fav[busy] { opacity: .5; pointer-events: none; }
  .body { padding: 12px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
  .title { font-weight: 500; line-height: 1.3; cursor: pointer; }
  .tags { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag { font-size: 11px; color: var(--secondary-text-color); background: var(--secondary-background-color); border-radius: 10px; padding: 2px 8px; }
  .ing { font-size: 13px; color: var(--secondary-text-color); line-height: 1.5; }
  .ing b { color: var(--primary-text-color); font-weight: 500; }
  .empty-state { text-align: center; color: var(--secondary-text-color); padding: 64px 16px; }
  .more { display: block; margin: 24px auto 0; font: inherit; cursor: pointer; border: 1px solid var(--primary-color); color: var(--primary-color); background: none; border-radius: 20px; padding: 8px 24px; }
  .error { background: var(--error-color); color: #fff; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
  .folder { margin-bottom: 24px; }
  .folder h2 { font-size: 16px; font-weight: 500; margin: 0 0 8px; }
  .muted { color: var(--secondary-text-color); font-weight: 400; font-size: 13px; }
  .overlay { position: fixed; inset: 0; z-index: 10; background: rgba(0,0,0,.6); display: flex; align-items: center; justify-content: center; padding: 16px; }
  .dialog { background: var(--card-background-color); color: var(--primary-text-color); border-radius: 16px; width: min(720px, 100%); max-height: 100%; overflow: auto; position: relative; box-shadow: 0 8px 32px rgba(0,0,0,.4); }
  .dialog .hero { aspect-ratio: 16 / 9; background: var(--secondary-background-color) center / cover no-repeat; display: grid; place-items: center; font-size: 64px; color: var(--disabled-text-color); }
  .dialog .close { position: absolute; top: 12px; left: 12px; width: 36px; height: 36px; border-radius: 50%; border: 0; background: rgba(0,0,0,.55); color: #fff; font-size: 18px; cursor: pointer; }
  .dialog .fav { top: 12px; right: 12px; width: 44px; height: 44px; font-size: 24px; }
  .dialog .content { padding: 20px 24px 24px; display: flex; flex-direction: column; gap: 16px; }
  .dialog h2 { margin: 0; font-size: 24px; font-weight: 500; line-height: 1.25; }
  .dialog h3 { margin: 0 0 8px; font-size: 14px; text-transform: uppercase; letter-spacing: .06em; color: var(--secondary-text-color); font-weight: 500; display: flex; align-items: center; justify-content: space-between; }
  .dialog h3 button { text-transform: none; letter-spacing: 0; font: inherit; font-size: 13px; background: none; border: 1px solid var(--divider-color); color: var(--primary-color); border-radius: 14px; padding: 2px 12px; cursor: pointer; }
  .items { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 2px 16px; }
  .items label { display: flex; gap: 10px; align-items: center; padding: 8px 0; cursor: pointer; border-bottom: 1px solid var(--divider-color); }
  .items input { width: 18px; height: 18px; accent-color: var(--primary-color); }
  .items input:checked + span { text-decoration: line-through; color: var(--disabled-text-color); }
  .text { line-height: 1.55; }
  .text h4 { margin: 18px 0 6px; color: var(--primary-color); font-size: 16px; font-weight: 600; }
  .text h4:first-child { margin-top: 0; }
  .text ul, .text ol { margin: 0 0 8px; padding-left: 22px; }
  .text li { margin: 4px 0; }
  .text p { margin: 8px 0; }
  .video { display: inline-flex; align-self: flex-start; gap: 8px; align-items: center; color: var(--primary-color); border: 1px solid var(--primary-color); border-radius: 20px; padding: 6px 16px; text-decoration: none; font-size: 14px; }
  .spinner { text-align: center; padding: 48px; color: var(--secondary-text-color); }
`;

const ICON = {
  menu: '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M3 6h18v2H3V6m0 5h18v2H3v-2m0 5h18v2H3v-2Z"/></svg>',
  refresh: '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M17.65 6.35A8 8 0 1 0 19.73 14h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35Z"/></svg>',
};

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

class GarfinhoPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._s = {
      tab: "search", text: "", tags: new Set(), sort: "relevance",
      results: [], hasMore: false, loading: false, error: "",
      favorites: [], folders: [], topTags: [], total: 0, ready: false,
      detail: {}, open: null, checked: new Set(), busy: new Set(),
    };
    this._timer = null;
    this._seq = 0;
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) this._init();
  }
  disconnectedCallback() { window.removeEventListener('keydown', this._onKey); }
  set narrow(v) { this._narrow = v; if (this._rendered) this._renderHeader(); }

  async _init() {
    this.shadowRoot.innerHTML = `<style>${STYLE}</style><header></header><main></main>`;
    this._rendered = true;
    this._renderHeader();
    this._bind();
    await this._loadState();
    await this._search();
  }

  async _ws(msg) { return this._hass.callWS(msg); }

  async _loadState() {
    try {
      const d = await this._ws({ type: "garfinho/state" });
      Object.assign(this._s, { favorites: d.favorites, folders: d.folders, topTags: d.tags, total: d.total, ready: true, error: "" });
    } catch (e) {
      this._s.error = e.message || "Could not load Garfinho";
      this._s.ready = true;
    }
    this._render();
  }

  async _search(more = false) {
    const s = this._s;
    const seq = ++this._seq;
    s.loading = true;
    if (!more) this._render();
    try {
      const d = await this._ws({
        type: "garfinho/search", text: s.text, tags: [...s.tags], sort: s.sort,
        limit: 24, offset: more ? s.results.length : 0,
      });
      if (seq !== this._seq) return;
      s.results = more ? s.results.concat(d.recipes) : d.recipes;
      s.hasMore = d.has_more;
      s.error = "";
    } catch (e) {
      if (seq === this._seq) s.error = e.message || "Search failed";
    }
    if (seq === this._seq) { s.loading = false; this._render(); }
  }

  async _toggle(id, on) {
    const s = this._s;
    if (s.busy.has(id)) return;
    s.busy.add(id);
    this._render();
    try {
      await this._ws({ type: "garfinho/set_favorite", recipe_id: id, favorite: on });
      for (const r of s.results) if (r.id === id) r.favorite = on;
      await this._loadState();
    } catch (e) {
      s.error = e.message || "Could not update favorite";
    }
    s.busy.delete(id);
    this._render();
  }

  _bind() {
    const root = this.shadowRoot;
    root.addEventListener("click", (ev) => {
      const el = ev.target.closest("[data-act]");
      if (!el) return;
      const s = this._s;
      const { act, id, tag, tab } = el.dataset;
      if (act === "menu") this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }));
      else if (act === "refresh") this._loadState().then(() => this._search());
      else if (act === "tab") { s.tab = tab; this._render(); }
      else if (act === "fav") this._toggle(id, el.dataset.on !== "true");
      else if (act === "open") { s.open = id; this._render(); this._loadDetail(id); }
      else if (act === "close") { if (!ev.target.closest(".dialog") || el.classList.contains("close")) { s.open = null; this._render(); } }
      else if (act === "check") { s.checked.has(el.dataset.key) ? s.checked.delete(el.dataset.key) : s.checked.add(el.dataset.key); }
      else if (act === "copy") this._copyList(id)
      else if (act === "tag") { s.tags.has(tag) ? s.tags.delete(tag) : s.tags.add(tag); this._search(); }
      else if (act === "more") this._search(true);
    });
    this._onKey = (ev) => { if (ev.key === "Escape" && this._s.open) { this._s.open = null; this._render(); } };
    window.addEventListener("keydown", this._onKey);
    root.addEventListener("input", (ev) => {
      if (ev.target.id !== "q") return;
      this._s.text = ev.target.value;
      clearTimeout(this._timer);
      this._timer = setTimeout(() => this._search(), 250);
    });
    root.addEventListener("change", (ev) => {
      if (ev.target.id === "sort") { this._s.sort = ev.target.value; this._search(); }
    });
  }

  _renderHeader() {
    this.shadowRoot.querySelector("header").innerHTML =
      (this._narrow ? `<button data-act="menu" aria-label="Menu">${ICON.menu}</button>` : "") +
      `<h1>Garfinho</h1><button data-act="refresh" aria-label="Refresh" title="Refresh">${ICON.refresh}</button>`;
  }

  _card(r) {
    const open = false;
    const busy = this._s.busy.has(r.id);
    const bg = r.image ? `style="background-image:url('${esc(r.image)}')"` : "";
    const ings = `<div class="ing">${r.ingredients.length} ingredients</div>`;
    const fav = `<button class="fav" data-act="fav" data-id="${esc(r.id)}" data-on="${r.favorite}" ${r.favorite ? "on" : ""} ${busy ? "busy" : ""}
        aria-label="${r.favorite ? "Remove from favorites" : "Add to favorites"}" title="${r.favorite ? "Remove from favorites" : "Add to favorites"}">${r.favorite ? "♥" : "♡"}</button>`;
    return `<article class="card">
      <div class="photo ${r.image ? "" : "empty"}" data-act="open" data-id="${esc(r.id)}" ${bg}>${r.image ? "" : "🍽"}${fav}</div>
      <div class="body">
        <div class="title" data-act="open" data-id="${esc(r.id)}">${esc(r.title)}</div>
        <div class="tags">${r.tags.slice(0, open ? 99 : 3).map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
        ${ings}
      </div></article>`;
  }

  _grid(list, emptyMsg) {
    return list.length
      ? `<div class="grid">${list.map((r) => this._card(r)).join("")}</div>`
      : `<div class="empty-state">${emptyMsg}</div>`;
  }

  _render() {
    const s = this._s;
    const main = this.shadowRoot.querySelector("main");
    if (!main) return;
    const focus = this.shadowRoot.activeElement?.id === "q";
    const caret = focus ? this.shadowRoot.getElementById("q").selectionStart : 0;
    let body;
    if (!s.ready) body = `<div class="spinner">Loading…</div>`;
    else if (s.tab === "favorites") body = this._favoritesView();
    else body = this._searchView();
    main.innerHTML =
      (s.error ? `<div class="error" role="alert">${esc(s.error)}</div>` : "") +
      `<div class="tabs" role="tablist">
        <button class="tab" role="tab" data-act="tab" data-tab="search" ${s.tab === "search" ? "active" : ""}>Search</button>
        <button class="tab" role="tab" data-act="tab" data-tab="favorites" ${s.tab === "favorites" ? "active" : ""}>Favorites<span class="count">${s.favorites.length}</span></button>
      </div>` + body + this._dialog();
    if (focus) {
      const q = this.shadowRoot.getElementById("q");
      q.focus();
      q.setSelectionRange(caret, caret);
    }
  }

  async _loadDetail(id) {
    const s = this._s;
    if (s.detail[id]) return;
    s.detail[id] = { loading: true };
    this._render();
    try {
      const d = await this._ws({ type: "garfinho/recipe", recipe_id: id });
      s.detail[id] = { html: d.html, video: d.video_id };
    } catch {
      s.detail[id] = { html: "", video: null, failed: true };
    }
    this._render();
  }

  _find(id) {
    const s = this._s;
    return s.results.find((r) => r.id === id) || s.favorites.find((r) => r.id === id);
  }

  async _copyList(id) {
    const r = this._find(id);
    if (!r) return;
    const text = r.title + "\n" + r.ingredients.map((i) => "- " + i).join("\n");
    try { await navigator.clipboard.writeText(text); this._s.error = ""; this._flash("Ingredients copied"); } catch { this._flash("Could not copy"); }
  }

  _flash(msg) {
    const btn = this.shadowRoot.querySelector('[data-act="copy"]');
    if (btn) { const old = btn.textContent; btn.textContent = msg; setTimeout(() => { btn.textContent = old; }, 1500); }
  }

  _dialog() {
    const r = this._s.open && this._find(this._s.open);
    if (!r) return "";
    const busy = this._s.busy.has(r.id);
    const items = r.ingredients.map((name, i) => {
      const key = `${r.id}:${i}`;
      return `<li><label><input type="checkbox" data-act="check" data-key="${esc(key)}" ${this._s.checked.has(key) ? "checked" : ""}><span>${esc(name)}</span></label></li>`;
    }).join("");
    const bg = r.image ? `style="background-image:url('${esc(r.image)}')"` : "";
    return `<div class="overlay" data-act="close"><div class="dialog" role="dialog" aria-modal="true" aria-label="${esc(r.title)}">
      <div class="hero" ${bg}>${r.image ? "" : "🍽"}</div>
      <button class="close" data-act="close" aria-label="Close">✕</button>
      <button class="fav" data-act="fav" data-id="${esc(r.id)}" data-on="${r.favorite}" ${r.favorite ? "on" : ""} ${busy ? "busy" : ""}
        aria-label="${r.favorite ? "Remove from favorites" : "Add to favorites"}">${r.favorite ? "♥" : "♡"}</button>
      <div class="content">
        <h2>${esc(r.title)}</h2>
        <div class="tags">${r.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
        ${this._recipeBody(r, items)}
      </div></div></div>`;
  }

  _recipeBody(r, items) {
    const d = this._s.detail[r.id];
    if (!d || d.loading) return `<div class="spinner">Loading recipe…</div>`;
    const video = d.video ? `<a class="video" href="https://www.youtube.com/watch?v=${esc(d.video)}" target="_blank" rel="noopener noreferrer">▶ Watch the video</a>` : "";
    if (d.html) return `${video}<section class="text">${d.html}</section>`;
    return `${video}<section><h3>Ingredients <button data-act="copy" data-id="${esc(r.id)}">Copy list</button></h3><ul class="items">${items || "<li class='muted'>No ingredients listed</li>"}</ul>${d.failed ? "<p class='muted'>Could not load the instructions.</p>" : "<p class='muted'>No instructions available for this recipe.</p>"}</section>`;
  }

  _searchView() {
    const s = this._s;
    const sorts = [["relevance", "Relevance"], ["newest", "Newest"], ["title", "A–Z"], ["random", "Random"]];
    const chips = s.topTags.map((t) =>
      `<button class="chip" data-act="tag" data-tag="${esc(t.name)}" ${s.tags.has(t.name) ? "active" : ""}>${esc(t.name)}<small>${t.count}</small></button>`).join("");
    return `<div class="controls">
        <input id="q" type="search" placeholder="Search ${s.total} recipes by name or ingredient" value="${esc(s.text)}" aria-label="Search recipes">
        <select id="sort" aria-label="Sort">${sorts.map(([v, l]) => `<option value="${v}" ${s.sort === v ? "selected" : ""}>${l}</option>`).join("")}</select>
      </div>
      <div class="chips">${chips}</div>` +
      (s.loading && !s.results.length ? `<div class="spinner">Searching…</div>` : this._grid(s.results, "No recipes match your search.")) +
      (s.hasMore ? `<button class="more" data-act="more">${s.loading ? "Loading…" : "Show more"}</button>` : "");
  }

  _favoritesView() {
    const s = this._s;
    if (!s.favorites.length) return `<div class="empty-state">No favorites yet. Find a recipe in Search and tap ♡.</div>`;
    const byId = new Map(s.favorites.map((r) => [r.id, r]));
    const inFolder = new Set();
    const folders = s.folders
      .map((f) => {
        const recipes = f.recipes.map((id) => byId.get(id)).filter(Boolean);
        recipes.forEach((r) => inFolder.add(r.id));
        return recipes.length ? `<section class="folder"><h2>${esc(f.title)} <span class="muted">${recipes.length}</span></h2>${this._grid(recipes, "")}</section>` : "";
      }).join("");
    const rest = s.favorites.filter((r) => !inFolder.has(r.id));
    return folders + (rest.length ? `<section class="folder">${folders ? `<h2>Unsorted <span class="muted">${rest.length}</span></h2>` : ""}${this._grid(rest, "")}</section>` : "");
  }
}

customElements.define("garfinho-panel", GarfinhoPanel);
