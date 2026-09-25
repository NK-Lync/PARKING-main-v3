// ============================================================
// views/taikhoan.js — quản lý tài khoản người dùng (CRUD)
// ------------------------------------------------------------
// Khi sửa tài khoản, ô mật khẩu để trống nghĩa là giữ nguyên mật
// khẩu cũ, nên chỉ gửi trường matkhau khi người dùng thực sự gõ.
// ============================================================

App.views.taikhoan = {
  _rows: [],

  async render() {
    const U = App.ui;
    App.router.setTitle("Quản lý tài khoản");

    App.router.setContent(
      U.card({
        title: "Danh sách tài khoản",
        note: "Vai trò quyết định những màn hình mà tài khoản được phép mở",
        actions: U.addButton("Thêm tài khoản"),
        flush: true,
        body: `<div id="taikhoan-table">${U.spinner()}</div>`,
      })
    );

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
      document.getElementById("taikhoan-table").innerHTML = App.ui.alertLoi(err);
    }
  },

  draw() {
    const U = App.ui;
    document.getElementById("taikhoan-table").innerHTML = U.table(
      [
        { label: "Mã", key: "mand" },
        { label: "Tên đăng nhập", key: "tendangnhap", strong: true },
        { label: "Vai trò", key: "vaitro", render: (v) => U.roleBadge(v) },
        {
          label: "Trạng thái",
          key: "trangthai",
          render: (v) => U.badge(v ? "Hoạt động" : "Bị khóa", v ? "ok" : "err"),
        },
        { label: "Email", key: "email", render: (v) => (v ? U.escape(v) : "—") },
        { label: "SĐT", key: "sodienthoai", render: (v) => (v ? U.escape(v) : "—") },
        { label: "", key: "mand", act: true, render: (v) => U.actionButtons(v) },
      ],
      this._rows,
      "Chưa có tài khoản nào."
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      this.openForm(this._rows.find((r) => String(r.mand) === String(id)));
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const U = App.ui;
    const sua = !!row;

    const modal = U.modal({
      title: sua ? "Sửa tài khoản" : "Thêm tài khoản",
      body: `
        <form id="tk-form">
          ${U.field("Tên đăng nhập", U.input({
            name: "tendangnhap",
            value: row?.tendangnhap || "",
            placeholder: "VD: nhanvien01",
            required: true,
          }))}
          ${U.field(
            sua ? "Mật khẩu (để trống nếu không đổi)" : "Mật khẩu",
            U.input({ name: "matkhau", type: "password", placeholder: "••••••", required: !sua })
          )}
          ${U.field("Vai trò", U.select({
            name: "vaitro",
            value: row?.vaitro ?? "nhanvien",
            required: true,
            options: Object.entries(App.config.ROLES).map(([key, label]) => ({
              value: key,
              label,
            })),
          }))}
          ${U.field("Trạng thái", U.select({
            name: "trangthai",
            value: String(row ? !!row.trangthai : true),
            required: true,
            options: [
              { value: "true", label: "Hoạt động" },
              { value: "false", label: "Bị khóa" },
            ],
          }), "Tài khoản bị khóa sẽ không đăng nhập được")}
          ${U.field("Email", U.input({
            name: "email",
            type: "email",
            value: row?.email || "",
            placeholder: "ten@vidu.com",
          }))}
          ${U.field("Số điện thoại", U.input({
            name: "sodienthoai",
            value: row?.sodienthoai || "",
            placeholder: "09xxxxxxxx",
          }))}
        </form>`,
      footer: U.formButtons(),
    });
    modal.show();

    modal.find('[data-action="cancel"]').addEventListener("click", () => modal.hide());
    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#tk-form"));
      const matkhau = String(fd.get("matkhau") || "");

      const body = {
        tendangnhap: String(fd.get("tendangnhap") || "").trim(),
        vaitro: String(fd.get("vaitro") || ""),
        trangthai: String(fd.get("trangthai")) === "true",
        email: String(fd.get("email") || "").trim() || null,
        sodienthoai: String(fd.get("sodienthoai") || "").trim() || null,
      };
      // Chỉ gửi mật khẩu khi có gõ, để không ghi đè mật khẩu cũ bằng chuỗi rỗng.
      if (matkhau) body.matkhau = matkhau;

      try {
        if (sua) await App.api.put(`/api/taikhoan/${row.mand}`, body);
        else await App.api.post("/api/taikhoan", body);

        modal.hide();
        App.ui.toast(sua ? "Đã cập nhật tài khoản." : "Đã thêm tài khoản.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    const row = this._rows.find((r) => String(r.mand) === String(id));
    const dongY = await App.ui.confirm({
      title: "Xóa tài khoản",
      message: `Xóa tài khoản “${row ? row.tendangnhap : id}”? Người này sẽ không đăng nhập được nữa.`,
      okLabel: "Xóa",
      tone: "err",
    });
    if (!dongY) return;

    try {
      await App.api.del(`/api/taikhoan/${id}`);
      App.ui.toast("Đã xóa tài khoản.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
