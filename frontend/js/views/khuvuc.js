// ============================================================
// views/khuvuc.js — quản lý khu vực (CRUD + đồng bộ)
// ============================================================

App.views.khuvuc = {
  _rows: [],

  async render() {
    App.router.setTitle("Quản lý khu vực");
    App.router.setContent(`
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Danh sách khu vực</span>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary" data-action="sync"><i class="bi bi-arrow-repeat me-1"></i>Đồng bộ</button>
            ${App.ui.addButton("Thêm khu vực")}
          </div>
        </div>
        <div class="card-body" id="khuvuc-table">${App.ui.spinner()}</div>
      </div>`);
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
      document.getElementById("khuvuc-table").innerHTML =
        `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  draw() {
    document.getElementById("khuvuc-table").innerHTML = App.ui.table(
      [
        { label: "Mã", key: "makhuvuc" },
        { label: "Tên khu vực", key: "tenkhuvuc" },
        { label: "Tổng số vị trí", key: "tongsovitri" },
        { label: "Số xe hiện tại", key: "soxehientai" },
        { label: "", key: "makhuvuc", render: (v) => App.ui.actionButtons(v) },
      ],
      this._rows
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      const row = this._rows.find((r) => String(r.makhuvuc) === String(id));
      this.openForm(row);
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const isEdit = !!row;
    const modal = App.ui.modal({
      title: isEdit ? "Sửa khu vực" : "Thêm khu vực",
      body: `
        <form id="kv-form">
          <div class="mb-3">
            <label class="form-label">Tên khu vực</label>
            <input type="text" class="form-control" name="tenkhuvuc" value="${App.ui.escape(row?.tenkhuvuc || "")}" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Tổng số vị trí</label>
            <input type="number" class="form-control" name="tongsovitri" min="0" value="${row?.tongsovitri ?? 0}" required>
          </div>
        </form>`,
      footer: App.ui.formButtons(),
    });
    modal.show();

    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#kv-form"));
      const body = {
        tenkhuvuc: fd.get("tenkhuvuc").trim(),
        tongsovitri: Number(fd.get("tongsovitri")),
      };
      try {
        if (isEdit) {
          await App.api.put(`/api/khuvuc/${row.makhuvuc}`, body);
        } else {
          await App.api.post("/api/khuvuc", body);
        }
        modal.hide();
        App.ui.toast(isEdit ? "Đã cập nhật khu vực." : "Đã thêm khu vực.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    if (!confirm("Xóa khu vực này?")) return;
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
