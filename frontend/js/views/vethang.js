// ============================================================
// views/vethang.js — quản lý vé tháng (CRUD)
// ============================================================

App.views.vethang = {
  _rows: [],
  _loaixe: [],

  async render() {
    App.router.setTitle("Quản lý vé tháng");
    App.router.setContent(`
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Danh sách vé tháng</span>
          ${App.ui.addButton("Thêm vé tháng")}
        </div>
        <div class="card-body" id="vethang-table">${App.ui.spinner()}</div>
      </div>`);
    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.getElementById("vethang-table").addEventListener("click", (e) => this._onAction(e));
    await Promise.all([this.load(), this.loadLoaixe()]);
  },

  async loadLoaixe() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._loaixe = res.data || [];
    } catch (err) { /* không quan trọng */ }
  },

  async load() {
    try {
      const res = await App.api.get("/api/vethang");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("vethang-table").innerHTML =
        `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  draw() {
    document.getElementById("vethang-table").innerHTML = App.ui.table(
      [
        { label: "Mã vé", key: "mave" },
        { label: "Biển số", key: "bienso" },
        { label: "Khách hàng", key: "tenkhachhang" },
        { label: "Loại xe", key: "maloaixe", render: (v) => this._loaixeName(v) },
        { label: "Ngày đăng ký", key: "ngaydangky", render: (v) => App.ui.fmtDateTime(v) },
        { label: "Ngày hết hạn", key: "ngayhethan", render: (v) => App.ui.fmtDateTime(v) },
        { label: "Trạng thái", key: "trangthai", render: (v) => App.ui.boolBadge(v) },
        { label: "", key: "mave", render: (v) => App.ui.actionButtons(v) },
      ],
      this._rows
    );
  },

  _loaixeName(id) {
    const lx = this._loaixe.find((l) => String(l.maloaixe) === String(id));
    return lx ? lx.tenloaixe : (id ?? "—");
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      const row = this._rows.find((r) => String(r.mave) === String(id));
      this.openForm(row);
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const isEdit = !!row;
    const lxOptions = this._loaixe
      .map((l) => `<option value="${l.maloaixe}" ${row && String(row.maloaixe) === String(l.maloaixe) ? "selected" : ""}>${App.ui.escape(l.tenloaixe)}</option>`)
      .join("");

    const toDate = (v) => v ? String(v).slice(0, 10) : "";

    const modal = App.ui.modal({
      title: isEdit ? "Sửa vé tháng" : "Thêm vé tháng",
      body: `
        <form id="vth-form">
          <div class="mb-3">
            <label class="form-label">Biển số xe</label>
            <input type="text" class="form-control" name="bienso" value="${App.ui.escape(row?.bienso || "")}" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Tên khách hàng</label>
            <input type="text" class="form-control" name="tenkhachhang" value="${App.ui.escape(row?.tenkhachhang || "")}">
          </div>
          <div class="mb-3">
            <label class="form-label">Loại xe</label>
            <select class="form-select" name="maloaixe"><option value="">— Chọn loại xe —</option>${lxOptions}</select>
          </div>
          <div class="mb-3">
            <label class="form-label">Ngày đăng ký</label>
            <input type="date" class="form-control" name="ngaydangky" value="${toDate(row?.ngaydangky)}">
          </div>
          <div class="mb-3">
            <label class="form-label">Ngày hết hạn</label>
            <input type="date" class="form-control" name="ngayhethan" value="${toDate(row?.ngayhethan)}" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Trạng thái</label>
            <select class="form-select" name="trangthai">
              <option value="true" ${!row || row.trangthai ? "selected" : ""}>Hiệu lực</option>
              <option value="false" ${row && row.trangthai === false ? "selected" : ""}>Hết hạn</option>
            </select>
          </div>
        </form>`,
      footer: App.ui.formButtons(),
    });
    modal.show();

    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#vth-form"));
      const body = {
        bienso: fd.get("bienso").trim(),
        tenkhachhang: fd.get("tenkhachhang").trim() || null,
        maloaixe: fd.get("maloaixe") ? Number(fd.get("maloaixe")) : null,
        ngaydangky: fd.get("ngaydangky") || null,
        ngayhethan: fd.get("ngayhethan"),
        trangthai: fd.get("trangthai") === "true",
      };
      try {
        if (isEdit) {
          await App.api.put(`/api/vethang/${row.mave}`, body);
        } else {
          await App.api.post("/api/vethang", body);
        }
        modal.hide();
        App.ui.toast(isEdit ? "Đã cập nhật vé tháng." : "Đã thêm vé tháng.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    if (!confirm("Xóa vé tháng này?")) return;
    try {
      await App.api.del(`/api/vethang/${id}`);
      App.ui.toast("Đã xóa vé tháng.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
