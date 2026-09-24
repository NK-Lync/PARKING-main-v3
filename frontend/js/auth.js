// ============================================================
// auth.js — quản lý phiên đăng nhập & phân quyền (client-side)
// ============================================================

App.auth = {
  getUser() {
    try {
      return JSON.parse(localStorage.getItem(App.config.STORAGE_KEY));
    } catch (err) {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem(App.config.STORAGE_KEY, JSON.stringify(user));
  },

  clear() {
    localStorage.removeItem(App.config.STORAGE_KEY);
  },

  isLoggedIn() {
    return !!this.getUser();
  },

  role() {
    const u = this.getUser();
    return u ? u.vaitro : null;
  },

  roleLabel() {
    return App.ui.roleLabel(this.role());
  },

  // Kiểm tra vai trò có được truy cập route này không.
  can(route) {
    const perms = App.config.PERMISSIONS[this.role()] || [];
    return perms.includes(route);
  },

  async login(tendangnhap, matkhau) {
    const res = await App.api.post("/api/taikhoan/dang-nhap", { tendangnhap, matkhau });
    if (res.success) {
      this.setUser(res.data);
    }
    return res;
  },

  async logout() {
    const user = this.getUser();
    if (user && user.mand) {
      try { await App.api.post("/api/taikhoan/dang-xuat", { mand: user.mand }); } catch (err) { /* bỏ qua */ }
    }
    this.clear();
  },
};
