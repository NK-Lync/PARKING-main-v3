// ============================================================
// views/loaixe.js — quản lý loại xe (CRUD)
// ============================================================

App.views.loaixe = {
  _rows: [],

  async render() {
    App.router.setTitle("Quản lý loại xe");
    App.router.setContent(`
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Danh sách loại xe</span>
          ${App.ui.addButton("Thêm loại xe")}
        </div>
        <div class="card-body" id="loaixe-table">${App.ui.spinner()}</div>
      </div>`);
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
      document.getElementById("loaixe-table").innerHTML =
        `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  draw() {
    document.getElementById("loaixe-table").innerHTML = App.ui.table(
      [
        { label: "Mã", key: "maloaixe" },
        { label: "Tên loại xe", key: "tenloaixe" },
        { label: "Đơn giá / giờ", key: "dongia", render: (v) => App.ui.fmtMoney(v) },
        { label: "", key: "maloaixe", render: (v) => App.ui.actionButtons(v) },
      ],
      this._rows
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      const row = this._rows.find((r) => String(r.maloaixe) === String(id));
      this.openForm(row);
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const isEdit = !!row;
    const modal = App.ui.modal({
      title: isEdit ? "Sửa loại xe" : "Thêm loại xe",
      body: `
        <form id="lx-form">
          <div class="mb-3">
            <label class="form-label">Tên loại xe</label>
            <input type="text" class="form-control" name="tenloaixe" value="${App.ui.escape(row?.tenloaixe || "")}" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Đơn giá (VNĐ / giờ)</label>
            <input type="number" class="form-control" name="dongia" min="0" value="${row?.dongia ?? 0}" required>
          </div>
        </form>`,
      footer: App.ui.formButtons(),
    });
    modal.show();

    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#lx-form"));
      const body = {
        tenloaixe: fd.get("tenloaixe").trim(),
        dongia: Number(fd.get("dongia")),
      };
      try {
        if (isEdit) {
          await App.api.put(`/api/loaixe/${row.maloaixe}`, body);
        } else {
          await App.api.post("/api/loaixe", body);
        }
        modal.hide();
        App.ui.toast(isEdit ? "Đã cập nhật loại xe." : "Đã thêm loại xe.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    if (!confirm("Xóa loại xe này?")) return;
    try {
      await App.api.del(`/api/loaixe/${id}`);
      App.ui.toast("Đã xóa loại xe.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
