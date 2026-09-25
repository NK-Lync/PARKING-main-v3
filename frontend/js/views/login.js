// ============================================================
// views/login.js — màn hình đăng nhập
// ============================================================

App.views.login = {
  render() {
    const root = document.getElementById("login-root");
    const U = App.ui;

    root.innerHTML = `
      <div class="xp-auth">
        <div class="xp-auth-card">
          <div class="xp-auth-mark">
            ${App.icons.svg("parking", 24)}
          </div>

          <div class="xp-auth-title">XeParking</div>
          <div class="xp-auth-sub">Hệ thống quản lý bãi đỗ xe tích hợp AI</div>

          <form id="login-form" novalidate style="margin-top:24px">
            ${U.field("Tên đăng nhập",
              `<input type="text" class="xp-input" name="tendangnhap"
                      placeholder="Nhập tên đăng nhập" autocomplete="username" required>`)}
            ${U.field("Mật khẩu",
              `<input type="password" class="xp-input" name="matkhau"
                      placeholder="Nhập mật khẩu" autocomplete="current-password" required>`)}

            <div id="login-error" hidden style="margin-top:14px"></div>

            <button type="submit" class="xp-btn xp-btn-primary xp-btn-block"
                    id="login-btn" style="margin-top:18px;height:40px">
              ${App.icons.svg("log-in", 16)}Đăng nhập
            </button>
          </form>

          <div class="xp-auth-foot">
            <div class="xp-eyebrow" style="margin-bottom:6px">Tài khoản dùng thử</div>
            <div>Quản trị viên <code>admin</code> / <code>admin123</code></div>
            <div>Nhân viên bãi xe <code>nhanvien</code> / <code>nhanvien123</code></div>
            <div>Người quản lý <code>quanly</code> / <code>quanly123</code></div>
          </div>
        </div>
      </div>`;

    const form = document.getElementById("login-form");
    const btn = document.getElementById("login-btn");
    const errBox = document.getElementById("login-error");

    const hienLoi = (chu) => {
      errBox.innerHTML = `<div class="xp-alert err">
        ${App.icons.svg("warning", 17)}<div>${App.ui.escape(chu)}</div>
      </div>`;
      errBox.hidden = false;
    };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const tendangnhap = String(fd.get("tendangnhap") || "").trim();
      const matkhau = fd.get("matkhau");

      if (!tendangnhap || !matkhau) {
        hienLoi("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.");
        return;
      }

      errBox.hidden = true;
      btn.disabled = true;
      btn.innerHTML = '<span class="xp-spin"></span>Đang đăng nhập…';

      try {
        await App.auth.login(tendangnhap, matkhau);
        window.location.hash = "#/dashboard";
        App.router.route();
      } catch (err) {
        hienLoi(err.message || "Đăng nhập thất bại.");
      } finally {
        btn.disabled = false;
        btn.innerHTML = `${App.icons.svg("log-in", 16)}Đăng nhập`;
      }
    });

    form.querySelector('[name="tendangnhap"]').focus();
  },
};
