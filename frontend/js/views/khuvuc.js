// ============================================================
// views/khuvuc.js — quản lý khu vực (CRUD + đồng bộ)
// ============================================================

App.views.khuvuc = {
  _rows: [],

  async render() {
    const U = App.ui;
    App.router.setTitle("Quản lý khu vực");

    App.router.setContent(
      U.card({
        title: "Danh sách khu vực",
        note: "Số xe hiện tại do hệ thống tự đếm, bấm Đồng bộ để cập nhật lại",
        actions: `
          <button class="xp-btn xp-btn-outline" data-action="sync">
            ${App.icons.svg("refresh", 15)}Đồng bộ
          </button>
          ${U.addButton("Thêm khu vực")}`,
        flush: true,
        body: `<div id="khuvuc-table">${U.spinner()}</div>`,
      })
    );

    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.querySelector('[data-action="sync"]').addEventListener("click", () => this.sync());
    document.getElementById("khuvuc-table").addEventListener("click", (e) => this._onAction(e));

    await this.load();
  },

  async load() {
    try {
      const res = await App.api.get("/api/khuvuc");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("khuvuc-table").innerHTML = App.ui.alertLoi(err);
    }
  },

  draw() {
    const U = App.ui;
    document.getElementById("khuvuc-table").innerHTML = U.table(
      [
        { label: "Mã", key: "makhuvuc" },
        { label: "Tên khu vực", key: "tenkhuvuc", strong: true },
        { label: "Tổng số vị trí", key: "tongsovitri" },
        {
          label: "Số xe hiện tại",
          key: "soxehientai",
          render: (v, row) => {
            const day = (row.tongsovitri ?? 0) > 0 && (v ?? 0) >= row.tongsovitri;
            return day ? U.badge(v ?? 0, "warn") : String(v ?? 0);
          },
        },
        { label: "", key: "makhuvuc", act: true, render: (v) => U.actionButtons(v) },
      ],
      this._rows,
      "Chưa có khu vực nào."
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      this.openForm(this._rows.find((r) => String(r.makhuvuc) === String(id)));
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const U = App.ui;
    const sua = !!row;

    const modal = U.modal({
      title: sua ? "Sửa khu vực" : "Thêm khu vực",
      body: `
        <form id="kv-form">
          ${U.field("Tên khu vực", U.input({
            name: "tenkhuvuc",
            value: row?.tenkhuvuc || "",
            placeholder: "VD: Khu A",
            required: true,
          }))}
          ${U.field("Tổng số vị trí", U.input({
            name: "tongsovitri",
            type: "number",
            min: 0,
            value: row?.tongsovitri ?? 0,
            required: true,
          }), "Số chỗ đỗ mà khu vực này có")}
        </form>`,
      footer: U.formButtons(),
    });
    modal.show();

    modal.find('[data-action="cancel"]').addEventListener("click", () => modal.hide());
    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#kv-form"));
      const body = {
        tenkhuvuc: String(fd.get("tenkhuvuc") || "").trim(),
        tongsovitri: Number(fd.get("tongsovitri")),
      };
      try {
        if (sua) await App.api.put(`/api/khuvuc/${row.makhuvuc}`, body);
        else await App.api.post("/api/khuvuc", body);

        modal.hide();
        App.ui.toast(sua ? "Đã cập nhật khu vực." : "Đã thêm khu vực.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    const row = this._rows.find((r) => String(r.makhuvuc) === String(id));
    const dongY = await App.ui.confirm({
      title: "Xóa khu vực",
      message: `Xóa khu vực “${row ? row.tenkhuvuc : id}”? Các vị trí đỗ thuộc khu vực này có thể bị ảnh hưởng.`,
      okLabel: "Xóa",
      tone: "err",
    });
    if (!dongY) return;

    try {
      await App.api.del(`/api/khuvuc/${id}`);
      App.ui.toast("Đã xóa khu vực.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },

  async sync() {
    try {
      await App.api.post("/api/khuvuc/cap-nhat");
      App.ui.toast("Đã đồng bộ số xe hiện tại.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
