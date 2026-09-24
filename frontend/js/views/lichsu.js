// ============================================================
// views/lichsu.js — tra cứu lịch sử lượt gửi xe
// ============================================================

App.views.lichsu = {
  _rows: [],
  _loaixe: [],

  async render() {
    App.router.setTitle("Tra cứu lịch sử");
    App.router.setContent(`
      <div class="card">
        <div class="card-header">Lịch sử lượt gửi xe</div>
        <div class="card-body">
          <div class="row g-2 mb-3">
            <div class="col-md-4">
              <input type="text" class="form-control" id="lichsu-search" placeholder="Tìm theo biển số…">
            </div>
            <div class="col-md-3">
              <select class="form-select" id="lichsu-tinhtrang">
                <option value="">Tất cả trạng thái</option>
                <option value="Đang gửi">Đang gửi</option>
                <option value="Đã trả">Đã trả</option>
              </select>
            </div>
          </div>
          <div id="lichsu-table">${App.ui.spinner()}</div>
        </div>
      </div>`);
    document.getElementById("lichsu-search").addEventListener("input", () => this.draw());
    document.getElementById("lichsu-tinhtrang").addEventListener("change", () => this.draw());
    await Promise.all([this.load(), this.loadLoaixe()]);
  },

  async loadLoaixe() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._loaixe = res.data || [];
    } catch (err) { /* bỏ qua */ }
  },

  async load() {
    try {
      const res = await App.api.get("/api/luotguixe");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("lichsu-table").innerHTML =
        `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    }
  },

  _loaixeName(id) {
    const lx = this._loaixe.find((l) => String(l.maloaixe) === String(id));
    return lx ? lx.tenloaixe : (id ?? "—");
  },

  draw() {
    const q = document.getElementById("lichsu-search").value.trim().toLowerCase();
    const tt = document.getElementById("lichsu-tinhtrang").value;

    let rows = this._rows;
    if (q) rows = rows.filter((r) => String(r.bienso || "").toLowerCase().includes(q));
    if (tt) rows = rows.filter((r) => r.tinhtrang === tt);

    document.getElementById("lichsu-table").innerHTML = App.ui.table(
      [
        { label: "Mã", key: "maluotgui" },
        { label: "Biển số", key: "bienso" },
        { label: "Loại xe", key: "maloaixe", render: (v) => this._loaixeName(v) },
        { label: "Vị trí", key: "mavitri", render: (v) => v != null ? `#${v}` : "—" },
        { label: "Loại vé", key: "loaive" },
        { label: "Giờ vào", key: "thoigianvao", render: (v) => App.ui.fmtDateTime(v) },
        { label: "Giờ ra", key: "thoigianra", render: (v) => App.ui.fmtDateTime(v) },
        { label: "Tổng phí", key: "tongphi", render: (v) => App.ui.fmtMoney(v) },
        { label: "Trạng thái", key: "tinhtrang", render: (v) => App.ui.statusBadge(v) },
      ],
      rows
    );
  },
};
