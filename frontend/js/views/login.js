// ============================================================
// views/login.js — màn hình đăng nhập
// ============================================================

App.views.login = {
  render() {
    const root = document.getElementById("login-root");
    root.innerHTML = `
      <div class="auth-wrap">
        <div class="card auth-card shadow-lg">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <i class="bi bi-p-square-fill text-primary" style="font-size:3rem"></i>
              <h4 class="mt-3 fw-bold">Xe Parking</h4>
              <p class="text-muted mb-0">Hệ thống quản lý bãi đỗ xe tích hợp AI</p>
            </div>

            <form id="login-form" novalidate>
              <div class="mb-3">
                <label class="form-label">Tên đăng nhập</label>
                <input type="text" class="form-control" name="tendangnhap" placeholder="Tên đăng nhập" autocomplete="username" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Mật khẩu</label>
                <input type="password" class="form-control" name="matkhau" placeholder="Mật khẩu" autocomplete="current-password" required>
              </div>
              <div id="login-error" class="alert alert-danger d-none"></div>
              <button type="submit" class="btn btn-primary w-100" id="login-btn">
                <i class="bi bi-box-arrow-in-right me-1"></i>Đăng nhập
              </button>
            </form>

            <div class="mt-4 text-center small text-muted">
              <div>admin / admin123 · nhanvien / nhanvien123 · quanly / quanly123</div>
            </div>
          </div>
        </div>
      </div>`;

    const form = document.getElementById("login-form");
    const btn = document.getElementById("login-btn");
    const errBox = document.getElementById("login-error");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const tendangnhap = fd.get("tendangnhap").trim();
      const matkhau = fd.get("matkhau");

      if (!tendangnhap || !matkhau) {
        errBox.textContent = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.";
        errBox.classList.remove("d-none");
        return;
      }

      errBox.classList.add("d-none");
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Đang đăng nhập…';

      try {
        const res = await App.auth.login(tendangnhap, matkhau);
        window.location.hash = "#/dashboard";
        App.router.route();
      } catch (err) {
        errBox.textContent = err.message || "Đăng nhập thất bại.";
        errBox.classList.remove("d-none");
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i>Đăng nhập';
      }
    });
  },
};
