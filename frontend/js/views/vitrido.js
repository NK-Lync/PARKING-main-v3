// ============================================================
// views/vitrido.js — quản lý vị trí đỗ (CRUD)
// ------------------------------------------------------------
// Bảng vitrido chỉ lưu khóa ngoại makhuvuc, nên tên khu vực phải
// tra qua danh sách khu vực tải song song.
// ============================================================

App.views.vitrido = {
  _rows: [],
  _khuvuc: [],

  async render() {
    const U = App.ui;
    App.router.setTitle("Quản lý vị trí đỗ");

    App.router.setContent(
      U.card({
        title: "Danh sách vị trí đỗ",
        note: "Trạng thái vị trí được hệ thống cập nhật khi xe vào và ra bãi",
        actions: U.addButton("Thêm vị trí"),
        flush: true,
        body: `<div id="vitrido-table">${U.spinner()}</div>`,
      })
    );

    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.getElementById("vitrido-table").addEventListener("click", (e) => this._onAction(e));

    await Promise.all([this.loadKhuvuc(), this.load()]);
  },

  async loadKhuvuc() {
    try {
      const res = await App.api.get("/api/khuvuc");
      this._khuvuc = res.data || [];
    } catch (err) {
      this._khuvuc = [];
    }
  },

  async load() {
    try {
      const res = await App.api.get("/api/vitrido");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("vitrido-table").innerHTML = App.ui.alertLoi(err);
    }
  },

  _tenKhuVuc(id) {
    const k = this._khuvuc.find((x) => String(x.makhuvuc) === String(id));
    return k ? k.tenkhuvuc : (id ?? "—");
  },

  draw() {
    const U = App.ui;
    document.getElementById("vitrido-table").innerHTML = U.table(
      [
        { label: "Mã vị trí", key: "mavitri", strong: true },
        { label: "Khu vực", key: "makhuvuc", render: (v) => U.escape(this._tenKhuVuc(v)) },
        { label: "Trạng thái", key: "trangthai", render: (v) => U.statusBadge(v) },
        { label: "", key: "mavitri", act: true, render: (v) => U.actionButtons(v) },
      ],
      this._rows,
      "Chưa có vị trí đỗ nào."
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      this.openForm(this._rows.find((r) => String(r.mavitri) === String(id)));
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const U = App.ui;
    const sua = !!row;

    const modal = U.modal({
      title: sua ? "Sửa vị trí đỗ" : "Thêm vị trí đỗ",
      body: `
        <form id="vt-form">
          ${U.field("Khu vực", U.select({
            name: "makhuvuc",
            value: row?.makhuvuc ?? "",
            placeholder: "— Chọn khu vực —",
            required: true,
            options: this._khuvuc.map((k) => ({ value: k.makhuvuc, label: k.tenkhuvuc })),
          }))}
          ${U.field("Trạng thái", U.select({
            name: "trangthai",
            value: row?.trangthai ?? App.config.TRANG_THAI_VI_TRI[0],
            required: true,
            options: App.config.TRANG_THAI_VI_TRI.map((t) => ({ value: t, label: t })),
          }), "Đặt về “Còn trống” nếu vị trí đang bị kẹt trạng thái")}
        </form>`,
      footer: U.formButtons(),
    });
    modal.show();

    modal.find('[data-action="cancel"]').addEventListener("click", () => modal.hide());
    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#vt-form"));
      const body = {
        makhuvuc: Number(fd.get("makhuvuc")),
        trangthai: String(fd.get("trangthai") || ""),
      };
      try {
        if (sua) await App.api.put(`/api/vitrido/${row.mavitri}`, body);
        else await App.api.post("/api/vitrido", body);

        modal.hide();
        App.ui.toast(sua ? "Đã cập nhật vị trí." : "Đã thêm vị trí.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    const dongY = await App.ui.confirm({
      title: "Xóa vị trí đỗ",
      message: `Xóa vị trí #${id}? Lượt gửi xe đang gắn với vị trí này có thể bị ảnh hưởng.`,
      okLabel: "Xóa",
      tone: "err",
    });
    if (!dongY) return;

    try {
      await App.api.del(`/api/vitrido/${id}`);
      App.ui.toast("Đã xóa vị trí.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
