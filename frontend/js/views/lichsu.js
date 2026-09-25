// ============================================================
// views/lichsu.js — tra cứu lịch sử lượt gửi xe
// ------------------------------------------------------------
// API trả về toàn bộ lượt gửi trong một lần, việc lọc theo biển
// số và trạng thái làm ngay ở client.
// ============================================================

App.views.lichsu = {
  _rows: [],
  _loaixe: [],

  async render() {
    App.router.setTitle("Tra cứu lịch sử");
    const U = App.ui;

    App.router.setContent(`
      ${U.card({
        title: "Lịch sử lượt gửi xe",
        note: "Lọc ngay khi gõ, không cần bấm tìm",
        flush: true,
        body: `
          <div class="xp-card-head" style="border-bottom:1px solid var(--xp-border-soft)">
            <div class="xp-row xp-grow">
              <div style="position:relative;flex:1;min-width:200px;max-width:320px">
                <span style="position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--xp-faint);display:flex">
                  ${App.icons.svg("search", 15)}
                </span>
                <input type="text" class="xp-input" id="lichsu-search"
                       placeholder="Tìm theo biển số…" style="padding-left:34px">
              </div>
              <select class="xp-select" id="lichsu-tinhtrang" style="width:180px">
                <option value="">Tất cả trạng thái</option>
                <option value="Đang gửi">Đang gửi</option>
                <option value="Đã trả">Đã trả</option>
              </select>
              <span class="xp-small xp-muted" id="lichsu-dem"></span>
            </div>
          </div>
          <div id="lichsu-table">${U.spinner()}</div>`,
      })}`);

    document.getElementById("lichsu-search").addEventListener("input", () => this.draw());
    document.getElementById("lichsu-tinhtrang").addEventListener("change", () => this.draw());

    await Promise.all([this.load(), this.loadLoaixe()]);
  },

  async loadLoaixe() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._loaixe = res.data || [];
    } catch (err) {
      /* Không tra được tên loại xe thì hiện mã, không chặn màn hình. */
    }
  },

  async load() {
    try {
      const res = await App.api.get("/api/luotguixe");
      this._rows = res.data || [];
      this.draw();
    } catch (err) {
      document.getElementById("lichsu-table").innerHTML = App.ui.alertLoi(err);
    }
  },

  _loaixeName(id) {
    const lx = this._loaixe.find((l) => String(l.maloaixe) === String(id));
    return lx ? lx.tenloaixe : (id ?? "—");
  },

  draw() {
    const U = App.ui;
    const q = document.getElementById("lichsu-search").value.trim().toLowerCase();
    const tt = document.getElementById("lichsu-tinhtrang").value;

    let rows = this._rows;
    if (q) rows = rows.filter((r) => String(r.bienso || "").toLowerCase().includes(q));
    if (tt) rows = rows.filter((r) => r.tinhtrang === tt);

    document.getElementById("lichsu-dem").textContent =
      rows.length === this._rows.length
        ? `${rows.length} lượt`
        : `${rows.length} / ${this._rows.length} lượt`;

    document.getElementById("lichsu-table").innerHTML = U.table(
      [
        { label: "Mã", key: "maluotgui" },
        { label: "Biển số", key: "bienso", strong: true },
        { label: "Loại xe", key: "maloaixe", render: (v) => U.escape(this._loaixeName(v)) },
        { label: "Vị trí", key: "mavitri", render: (v) => (v == null ? "—" : `#${v}`) },
        {
          label: "Loại vé",
          key: "loaive",
          render: (v) => U.chip((App.config.NHAN_LOAI_VE || {})[v] || v || "—", "neutral"),
        },
        { label: "Giờ vào", key: "thoigianvao", render: (v) => U.fmtDateTime(v) },
        { label: "Giờ ra", key: "thoigianra", render: (v) => U.fmtDateTime(v) },
        { label: "Tổng phí", key: "tongphi", render: (v) => U.fmtMoney(v) },
        { label: "Trạng thái", key: "tinhtrang", render: (v) => U.statusBadge(v) },
      ],
      rows,
      q || tt ? "Không có lượt nào khớp điều kiện lọc." : "Chưa có lượt gửi xe nào."
    );
  },
};
