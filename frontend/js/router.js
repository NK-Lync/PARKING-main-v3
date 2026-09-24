// ============================================================
// router.js — định tuyến hash cho SPA
// ============================================================

App.router = {
  _content: null,
  _topbarTitle: null,
  _topbarUser: null,
  _sidebar: null,

  init() {
    this._content = document.getElementById("app-content");
    this._topbarTitle = document.getElementById("topbar-title");
    this._topbarUser = document.getElementById("topbar-user");
    this._sidebar = document.getElementById("sidebar-nav");

    window.addEventListener("hashchange", () => this.route());
    // Đăng xuất toàn cục (nút ở topbar).
    document.getElementById("btn-logout")?.addEventListener("click", () => this.handleLogout());
    // Toggle sidebar trên mobile.
    document.getElementById("btn-toggle-sidebar")?.addEventListener("click", () => {
      document.querySelector(".sidebar")?.classList.toggle("open");
    });

    this.route();
  },

  parse() {
    const hash = window.location.hash.replace(/^#\/?/, "");
    const parts = hash.split("/");
    return { route: parts[0] || App.config.DEFAULT_ROUTE, param: parts[1] || null };
  },

  route() {
    App.charts.destroy();

    if (!App.auth.isLoggedIn()) {
      this.renderShell(false);
      App.views.login.render();
      return;
    }

    const { route, param } = this.parse();
    const view = App.views[route];

    if (!App.auth.can(route) || !view) {
      this.renderShell(true);
      this.renderForbidden(route);
      return;
    }

    this.renderShell(true);
    view.render(param);
  },

  // Dựng khung (sidebar + topbar) khi đã đăng nhập; bỏ đi khi chưa.
  renderShell(show) {
    document.getElementById("app-shell").style.display = show ? "" : "none";
    document.getElementById("login-root").style.display = show ? "none" : "";
    if (!show) return;

    // Đổ menu theo quyền.
    const perms = App.config.PERMISSIONS[App.auth.role()] || [];
    const items = App.config.MENU
      .filter((m) => perms.includes(m.route))
      .map((m) => {
        const active = this.parse().route === m.route ? "active" : "";
        return `
          <a href="#/${m.route}" class="list-group-item list-group-item-action ${active}" data-route="${m.route}">
            <i class="bi ${m.icon} me-2"></i>${App.ui.escape(m.label)}
          </a>`;
      })
      .join("");
    this._sidebar.innerHTML = items;

    // Tiêu đề topbar.
    const current = App.config.MENU.find((m) => m.route === this.parse().route);
    this._topbarTitle.textContent = current ? current.label : "";

    // Thông tin người dùng.
    const user = App.auth.getUser();
    this._topbarUser.innerHTML = `
      <span class="text-muted me-2 d-none d-md-inline">
        ${App.ui.escape(user.tendangnhap || "")}
      </span>
      ${App.ui.roleBadge(user.vaitro)}`;
  },

  renderForbidden(route) {
    this._topbarTitle.textContent = "Không có quyền truy cập";
    this._content.innerHTML = `
      <div class="text-center py-5">
        <i class="bi bi-shield-lock text-muted" style="font-size:4rem"></i>
        <h4 class="mt-3">Bạn không có quyền truy cập màn hình này</h4>
        <p class="text-muted">Vai trò hiện tại của bạn không được phép vào "${App.ui.escape(route)}".</p>
        <a href="#/dashboard" class="btn btn-primary">Về Dashboard</a>
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
