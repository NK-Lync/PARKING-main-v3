// ============================================================
// views/vitrido.js — quản lý vị trí đỗ (CRUD)
// ============================================================

App.views.vitrido = {
  _rows: [],

  async render() {
    App.router.setTitle("Quản lý vị trí đỗ");
    App.router.setContent(`
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Danh sách vị trí đỗ</span>
          ${App.ui.addButton("Thêm vị trí")}
        </div>
        <div class="card-body" id="vitrido-table">${App.ui.spinner()}</div>
      </div>`);
    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.getElementById("vitrido-table").addEventListener("click", (e) => this._onAction(e));
    await this.load();
  },

  async load() {
    try {
      const res = await App.api.get("/api/vitrido");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("vitrido-table").innerHTML =
        `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  draw() {
    document.getElementById("vitrido-table").innerHTML = App.ui.table(
      [
        { label: "Mã vị trí", key: "mavitri" },
        { label: "Khu vực", key: "tenkhuvuc" },
        { label: "Trạng thái", key: "trangthai", render: (v) => App.ui.statusBadge(v) },
        { label: "", key: "mavitri", render: (v) => App.ui.actionButtons(v) },
      ],
      this._rows
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      const row = this._rows.find((r) => String(r.mavitri) === String(id));
      this.openForm(row);
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const isEdit = !!row;
    const statusOptions = App.config.TRANG_THAI_VI_TRI
      .map((s) => `<option value="${s}" ${row && row.trangthai === s ? "selected" : ""}>${s}</option>`)
      .join("");

    const modal = App.ui.modal({
      title: isEdit ? "Sửa vị trí đỗ" : "Thêm vị trí đỗ",
      body: `
        <form id="vt-form">
          <div class="mb-3">
            <label class="form-label">Tên khu vực</label>
            <input type="text" class="form-control" name="tenkhuvuc" value="${App.ui.escape(row?.tenkhuvuc || "")}" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Trạng thái</label>
            <select class="form-select" name="trangthai">${statusOptions}</select>
          </div>
        </form>`,
      footer: App.ui.formButtons(),
    });
    modal.show();

    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#vt-form"));
      const body = {
        tenkhuvuc: fd.get("tenkhuvuc").trim(),
        trangthai: fd.get("trangthai"),
      };
      try {
        if (isEdit) {
          await App.api.put(`/api/vitrido/${row.mavitri}`, body);
        } else {
          await App.api.post("/api/vitrido", body);
        }
        modal.hide();
        App.ui.toast(isEdit ? "Đã cập nhật vị trí." : "Đã thêm vị trí.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    if (!confirm("Xóa vị trí đỗ này?")) return;
    try {
      await App.api.del(`/api/vitrido/${id}`);
      App.ui.toast("Đã xóa vị trí đỗ.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
