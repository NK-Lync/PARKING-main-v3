// ============================================================
// router.js — định tuyến hash cho SPA
// ============================================================

App.router = {
  _content: null,
  _topbarTitle: null,
  _topbarUser: null,
  _sideUser: null,
  _sidebar: null,
  _shell: null,
  _scrim: null,

  init() {
    this._content = document.getElementById("app-content");
    this._topbarTitle = document.getElementById("topbar-title");
    this._topbarUser = document.getElementById("topbar-user");
    this._sideUser = document.getElementById("side-user");
    this._sidebar = document.getElementById("sidebar-nav");
    this._shell = document.getElementById("app-shell");
    this._scrim = document.getElementById("side-scrim");

    window.addEventListener("hashchange", () => this.route());

    document
      .getElementById("btn-logout")
      ?.addEventListener("click", () => this.handleLogout());

    // Trên màn hẹp, sidebar trượt ra và che mất một phần nội dung.
    // Bấm ra vùng mờ hoặc chọn xong một mục thì đóng lại.
    document
      .getElementById("btn-toggle-sidebar")
      ?.addEventListener("click", () => this.moSidebar(!this._shell.classList.contains("side-open")));

    this._scrim?.addEventListener("click", () => this.moSidebar(false));

    this.route();
  },

  moSidebar(mo) {
    this._shell.classList.toggle("side-open", !!mo);
    if (this._scrim) this._scrim.hidden = !mo;
  },

  parse() {
    const hash = window.location.hash.replace(/^#\/?/, "");
    const parts = hash.split("/");
    return { route: parts[0] || App.config.DEFAULT_ROUTE, param: parts[1] || null };
  },

  route() {
    App.charts.destroy();
    // Giải phóng camera khi rời màn hình, nếu không đèn camera vẫn sáng.
    App.camera.tat();
    this.moSidebar(false);

    if (!App.auth.isLoggedIn()) {
      this.renderShell(false);
      App.views.login.render();
      return;
    }

    const { route } = this.parse();
    const view = App.views[route];

    if (!App.auth.can(route) || !view) {
      this.renderShell(true);
      this.renderForbidden(route);
      return;
    }

    this.renderShell(true);
    view.render(this.parse().param);
  },

  // Dựng khung (sidebar + topbar) khi đã đăng nhập; bỏ đi khi chưa.
  renderShell(show) {
    document.getElementById("app-shell").hidden = !show;
    document.getElementById("login-root").hidden = show;
    if (!show) return;

    const dangMo = this.parse().route;
    const perms = App.config.PERMISSIONS[App.auth.role()] || [];
    const duocPhep = App.config.MENU.filter((m) => perms.includes(m.route));

    // Gom menu theo nhóm. Nhóm nào không còn mục nào thì bỏ luôn
    // tiêu đề, để vai trò ít quyền không thấy tiêu đề trống.
    let html = "";
    App.config.NHOM.forEach((nhom) => {
      const muc = duocPhep.filter((m) => m.nhom === nhom);
      if (!muc.length) return;

      html += `<div class="xp-nav-group">${App.ui.escape(nhom)}</div>`;
      html += muc
        .map(
          (m) => `
          <a class="xp-nav-item${m.route === dangMo ? " on" : ""}"
             href="#/${m.route}" data-route="${m.route}">
            ${App.icons.svg(m.icon, 17)}<span>${App.ui.escape(m.label)}</span>
          </a>`
        )
        .join("");
    });
    this._sidebar.innerHTML = html;

    // Tiêu đề topbar.
    const current = App.config.MENU.find((m) => m.route === dangMo);
    this._topbarTitle.textContent = current ? current.label : "";

    // Thông tin người dùng: hiện ở cả topbar lẫn chân sidebar.
    const user = App.auth.getUser();
    const ten = user.tendangnhap || "";
    const chuDau = (ten.match(/[a-zA-Z0-9À-ỹ]/) || ["?"])[0];

    this._topbarUser.innerHTML = `
      <span class="xp-top-user">${App.ui.escape(user.hoten || ten)}</span>
      ${App.ui.roleBadge(user.vaitro)}`;

    if (this._sideUser) {
      this._sideUser.innerHTML = `
        <div class="xp-avatar">${App.ui.escape(chuDau)}</div>
        <div class="xp-grow">
          <div class="xp-side-foot-name">${App.ui.escape(ten)}</div>
          <div class="xp-side-foot-role">${App.ui.escape(App.ui.roleLabel(user.vaitro))}</div>
        </div>`;
    }
  },

  renderForbidden(route) {
    this._topbarTitle.textContent = "Không có quyền truy cập";
    this._content.innerHTML = `
      <div class="xp-card">
        <div class="xp-card-body">
          <div class="xp-empty" style="padding:56px 20px">
            <div style="color:var(--xp-faint)">${App.icons.svg("lock", 40)}</div>
            <div class="xp-bold" style="font-size:16px;color:var(--xp-text);margin-top:12px">
              Bạn không có quyền truy cập màn hình này
            </div>
            <div class="xp-small xp-mt-sm">
              Vai trò hiện tại không được phép vào “${App.ui.escape(route)}”.
            </div>
            <a href="#/dashboard" class="xp-btn xp-btn-primary" style="margin-top:18px">Về Dashboard</a>
          </div>
        </div>
      </div>`;
  },

  async handleLogout() {
    await App.auth.logout();
    window.location.hash = "#/login";
    this.route();
  },

  // Set nội dung màn hình (view gọi hàm này).
  setContent(html) {
    this._content.innerHTML = html;
  },

  setTitle(title) {
    this._topbarTitle.textContent = title;
  },
};
