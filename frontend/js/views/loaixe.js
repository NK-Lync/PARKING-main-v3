// ============================================================
// views/loaixe.js — quản lý loại xe (CRUD)
// ============================================================

App.views.loaixe = {
  _rows: [],

  async render() {
    const U = App.ui;
    App.router.setTitle("Quản lý loại xe");

    App.router.setContent(
      U.card({
        title: "Danh sách loại xe",
        note: "Đơn giá này là cơ sở tính phí khi xe ra khỏi bãi",
        actions: U.addButton("Thêm loại xe"),
        flush: true,
        body: `<div id="loaixe-table">${U.spinner()}</div>`,
      })
    );

    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.getElementById("loaixe-table").addEventListener("click", (e) => this._onAction(e));

    await this.load();
  },

  async load() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("loaixe-table").innerHTML = App.ui.alertLoi(err);
    }
  },

  draw() {
    const U = App.ui;
    document.getElementById("loaixe-table").innerHTML = U.table(
      [
        { label: "Mã", key: "maloaixe" },
        { label: "Tên loại xe", key: "tenloaixe", strong: true },
        { label: "Đơn giá / giờ", key: "dongia", render: (v) => U.fmtMoney(v) },
        { label: "", key: "maloaixe", act: true, render: (v) => U.actionButtons(v) },
      ],
      this._rows,
      "Chưa có loại xe nào."
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      this.openForm(this._rows.find((r) => String(r.maloaixe) === String(id)));
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const U = App.ui;
    const sua = !!row;

    const modal = U.modal({
      title: sua ? "Sửa loại xe" : "Thêm loại xe",
      body: `
        <form id="lx-form">
          ${U.field("Tên loại xe", U.input({
            name: "tenloaixe",
            value: row?.tenloaixe || "",
            placeholder: "VD: Xe máy",
            required: true,
          }))}
          ${U.field("Đơn giá (VNĐ / giờ)", U.input({
            name: "dongia",
            type: "number",
            min: 0,
            step: 1000,
            value: row?.dongia ?? 0,
            required: true,
          }), "Phí tính theo mỗi giờ hoặc phần giờ đã gửi")}
        </form>`,
      footer: U.formButtons(),
    });
    modal.show();

    modal.find('[data-action="cancel"]').addEventListener("click", () => modal.hide());
    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#lx-form"));
      const body = {
        tenloaixe: String(fd.get("tenloaixe") || "").trim(),
        dongia: Number(fd.get("dongia")),
      };
      try {
        if (sua) await App.api.put(`/api/loaixe/${row.maloaixe}`, body);
        else await App.api.post("/api/loaixe", body);

        modal.hide();
        App.ui.toast(sua ? "Đã cập nhật loại xe." : "Đã thêm loại xe.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    const row = this._rows.find((r) => String(r.maloaixe) === String(id));
    const dongY = await App.ui.confirm({
      title: "Xóa loại xe",
      message: `Xóa loại xe “${row ? row.tenloaixe : id}”?`,
      okLabel: "Xóa",
      tone: "err",
    });
    if (!dongY) return;

    try {
      await App.api.del(`/api/loaixe/${id}`);
      App.ui.toast("Đã xóa loại xe.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
