// ============================================================
// views/vethang.js — quản lý vé tháng (CRUD)
// ------------------------------------------------------------
// API trả ngày dạng ISO đầy đủ, nhưng ô <input type="date"> chỉ
// nhận 10 ký tự đầu, nên phải cắt bớt trước khi đổ vào form.
// ============================================================

App.views.vethang = {
  _rows: [],
  _loaixe: [],

  async render() {
    const U = App.ui;
    App.router.setTitle("Quản lý vé tháng");

    App.router.setContent(
      U.card({
        title: "Danh sách vé tháng",
        note: "Xe có vé tháng còn hiệu lực sẽ được miễn phí khi ra bãi",
        actions: U.addButton("Thêm vé tháng"),
        flush: true,
        body: `<div id="vethang-table">${U.spinner()}</div>`,
      })
    );

    document.querySelector('[data-action="add"]').addEventListener("click", () => this.openForm(null));
    document.getElementById("vethang-table").addEventListener("click", (e) => this._onAction(e));

    await Promise.all([this.loadLoaixe(), this.load()]);
  },

  // ISO datetime -> "yyyy-mm-dd" cho ô nhập ngày.
  _toDate(v) {
    return v ? String(v).slice(0, 10) : "";
  },

  async loadLoaixe() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._loaixe = res.data || [];
    } catch (err) {
      this._loaixe = [];
    }
  },

  async load() {
    try {
      const res = await App.api.get("/api/vethang");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("vethang-table").innerHTML = App.ui.alertLoi(err);
    }
  },

  _loaixeName(id) {
    const lx = this._loaixe.find((l) => String(l.maloaixe) === String(id));
    return lx ? lx.tenloaixe : "—";
  },

  draw() {
    const U = App.ui;
    document.getElementById("vethang-table").innerHTML = U.table(
      [
        { label: "Mã vé", key: "mave" },
        { label: "Biển số", key: "bienso", strong: true },
        { label: "Khách hàng", key: "tenkhachhang", render: (v) => (v ? U.escape(v) : "—") },
        { label: "Loại xe", key: "maloaixe", render: (v) => U.escape(this._loaixeName(v)) },
        { label: "Ngày đăng ký", key: "ngaydangky", render: (v) => U.fmtDate(v) },
        { label: "Ngày hết hạn", key: "ngayhethan", render: (v) => U.fmtDate(v) },
        { label: "Trạng thái", key: "trangthai", render: (v) => U.boolBadge(v) },
        { label: "", key: "mave", act: true, render: (v) => U.actionButtons(v) },
      ],
      this._rows,
      "Chưa có vé tháng nào."
    );
  },

  _onAction(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = btn.dataset.id;
    if (btn.dataset.action === "edit") {
      this.openForm(this._rows.find((r) => String(r.mave) === String(id)));
    } else if (btn.dataset.action === "delete") {
      this.remove(id);
    }
  },

  openForm(row) {
    const U = App.ui;
    const sua = !!row;

    const modal = U.modal({
      title: sua ? "Sửa vé tháng" : "Thêm vé tháng",
      body: `
        <form id="vt-form">
          ${U.field("Biển số", U.input({
            name: "bienso",
            value: row?.bienso || "",
            placeholder: "VD: 51A-12345",
            required: true,
          }))}
          ${U.field("Tên khách hàng", U.input({
            name: "tenkhachhang",
            value: row?.tenkhachhang || "",
            placeholder: "Không bắt buộc",
          }))}
          ${U.field("Loại xe", U.select({
            name: "maloaixe",
            value: row?.maloaixe ?? "",
            placeholder: "— Chưa xác định —",
            options: this._loaixe.map((l) => ({
              value: l.maloaixe,
              label: `${l.tenloaixe} (${U.fmtMoney(l.dongia)}/giờ)`,
            })),
          }))}
          ${U.field("Ngày đăng ký", U.input({
            name: "ngaydangky",
            type: "date",
            value: this._toDate(row?.ngaydangky),
          }), "Để trống thì lấy ngày hôm nay")}
          ${U.field("Ngày hết hạn", U.input({
            name: "ngayhethan",
            type: "date",
            value: this._toDate(row?.ngayhethan),
            required: true,
          }))}
          ${U.field("Trạng thái", U.select({
            name: "trangthai",
            value: String(row ? !!row.trangthai : true),
            required: true,
            options: [
              { value: "true", label: "Còn hiệu lực" },
              { value: "false", label: "Ngừng hiệu lực" },
            ],
          }), "Vé hết hạn vẫn giữ trong danh sách, chỉ đổi trạng thái")}
        </form>`,
      footer: U.formButtons(),
    });
    modal.show();

    modal.find('[data-action="cancel"]').addEventListener("click", () => modal.hide());
    modal.find('[data-action="save"]').addEventListener("click", async () => {
      const fd = new FormData(modal.find("#vt-form"));
      const maLoaiXe = String(fd.get("maloaixe") || "");

      const body = {
        bienso: String(fd.get("bienso") || "").trim(),
        tenkhachhang: String(fd.get("tenkhachhang") || "").trim() || null,
        maloaixe: maLoaiXe ? Number(maLoaiXe) : null,
        ngaydangky: String(fd.get("ngaydangky") || "") || null,
        ngayhethan: String(fd.get("ngayhethan") || ""),
        trangthai: String(fd.get("trangthai")) === "true",
      };

      try {
        if (sua) await App.api.put(`/api/vethang/${row.mave}`, body);
        else await App.api.post("/api/vethang", body);

        modal.hide();
        App.ui.toast(sua ? "Đã cập nhật vé tháng." : "Đã thêm vé tháng.");
        await this.load();
      } catch (err) {
        App.ui.toast(err.message, "danger");
      }
    });
  },

  async remove(id) {
    const row = this._rows.find((r) => String(r.mave) === String(id));
    const dongY = await App.ui.confirm({
      title: "Xóa vé tháng",
      message: `Xóa vé tháng của xe “${row ? row.bienso : id}”?`,
      okLabel: "Xóa",
      tone: "err",
    });
    if (!dongY) return;

    try {
      await App.api.del(`/api/vethang/${id}`);
      App.ui.toast("Đã xóa vé tháng.");
      await this.load();
    } catch (err) {
      App.ui.toast(err.message, "danger");
    }
  },
};
