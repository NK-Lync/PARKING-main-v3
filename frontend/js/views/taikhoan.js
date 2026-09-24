// ============================================================
// views/taikhoan.js — quản lý tài khoản (CRUD)
// ============================================================

App.views.taikhoan = {
  _rows: [],

  async render() {
    App.router.setTitle("Quản lý tài khoản");
    App.router.setContent(`
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Danh sách tài khoản</span>
          ${App.ui.addButton("Thêm tài khoản")}
        </div>
        <div class="card-body" id="taikhoan-table">${App.ui.spinner()}</div>
      </div>`);
    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.getElementById("taikhoan-table").addEventListener("click", (e) => this._onAction(e));
    await this.load();
  },

  async load() {
    try {
      const res = await App.api.get("/api/taikhoan");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("taikhoan-table").innerHTML =
        `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  draw() {
    document.getElementById("taikhoan-table").innerHTML = App.ui.table(
      [
        { label: "Mã", key: "mand" },
        { label: "Tên đăng nhập", key: "tendangnhap" },
        { label: "Vai trò", key: "vaitro", render: (v) => App.ui.roleBadge(v) },
        { label: "Trạng thái", key: "trangthai", render: (v) => v ? App.ui.badge("Hoạt động", "success") : App.ui.badge("Bị khóa", "secondary") },
        { label: "Email", key: "email" },
        { label: "SĐT", key: "sodienthoai" },
        { label: "", key: "mand", render: (v) => App.ui.actionButtons(v) },
      ],
      this._rows
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      const row = this._rows.find((r) => String(r.mand) === String(id));
      this.openForm(row);
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const isEdit = !!row;
    const roleOptions = Object.entries(App.config.ROLES)
      .map(([k, v]) => `<option value="${k}" ${row && row.vaitro === k ? "selected" : ""}>${v}</option>`)
      .join("");

    const modal = App.ui.modal({
      title: isEdit ? "Sửa tài khoản" : "Thêm tài khoản",
      body: `
        <form id="tk-form">
          <div class="mb-3">
            <label class="form-label">Tên đăng nhập</label>
            <input type="text" class="form-control" name="tendangnhap" value="${App.ui.escape(row?.tendangnhap || "")}" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Mật khẩu ${isEdit ? '<span class="text-muted small">(để trống nếu không đổi)</span>' : ""}</label>
            <input type="password" class="form-control" name="matkhau" ${isEdit ? "" : "required"}>
          </div>
          <div class="mb-3">
            <label class="form-label">Vai trò</label>
            <select class="form-select" name="vaitro">${roleOptions}</select>
          </div>
          <div class="mb-3">
            <label class="form-label">Trạng thái</label>
            <select class="form-select" name="trangthai">
              <option value="true" ${!row || row.trangthai ? "selected" : ""}>Hoạt động</option>
              <option value="false" ${row && row.trangthai === false ? "selected" : ""}>Bị khóa</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" name="email" value="${App.ui.escape(row?.email || "")}">
          </div>
          <div class="mb-3">
            <label class="form-label">Số điện thoại</label>
            <input type="text" class="form-control" name="sodienthoai" value="${App.ui.escape(row?.sodienthoai || "")}">
          </div>
        </form>`,
      footer: App.ui.formButtons(),
    });
    modal.show();

    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const f = modal.find("#tk-form");
      const fd = new FormData(f);
      const body = {
        tendangnhap: fd.get("tendangnhap").trim(),
        vaitro: fd.get("vaitro"),
        trangthai: fd.get("trangthai") === "true",
        email: fd.get("email").trim() || null,
        sodienthoai: fd.get("sodienthoai").trim() || null,
      };
      const matkhau = fd.get("matkhau");
      if (matkhau) body.matkhau = matkhau;

      try {
        if (isEdit) {
          await App.api.put(`/api/taikhoan/${row.mand}`, body);
        } else {
          await App.api.post("/api/taikhoan", body);
        }
        modal.hide();
        App.ui.toast(isEdit ? "Đã cập nhật tài khoản." : "Đã thêm tài khoản.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    if (!confirm("Xóa tài khoản này?")) return;
    try {
      await App.api.del(`/api/taikhoan/${id}`);
      App.ui.toast("Đã xóa tài khoản.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
