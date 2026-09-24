// ============================================================
// views/chotrong.js — theo dõi chỗ trống (grid + tổng hợp khu vực)
// ============================================================

App.views.chotrong = {
  async render() {
    App.router.setTitle("Theo dõi chỗ trống");
    App.router.setContent(App.ui.spinner());

    try {
      const [kvRes, vtRes] = await Promise.all([
        App.api.get("/api/khuvuc/cho-trong"),
        App.api.get("/api/vitrido"),
      ]);
      const khuVucs = kvRes.data || [];
      const viTris = vtRes.data || [];

      const summary = khuVucs.map((k) => `
        <div class="col-6 col-md-4 col-lg-3">
          <div class="card stat-card h-100">
            <div class="card-body text-center">
              <div class="stat-label">${App.ui.escape(k.tenkhuvuc)}</div>
              <div class="stat-value ${k.so_cho_trong > 0 ? "text-success" : "text-danger"}">${k.so_cho_trong}</div>
              <div class="stat-label">/ ${k.tong_so_vi_tri} chỗ trống</div>
            </div>
          </div>
        </div>`).join("");

      const grid = viTris.map((v) => {
        const empty = v.trangthai === "Còn trống";
        return `
          <div class="slot ${empty ? "empty" : "occupied"}" title="${App.ui.escape(v.tenkhuvuc || "")} #${v.mavitri}">
            <i class="bi ${empty ? "bi-check-circle" : "bi-car-front-fill"}"></i>
            #${v.mavitri}
            <div class="small opacity-75">${App.ui.escape(v.tenkhuvuc || "")}</div>
          </div>`;
      }).join("");

      App.router.setContent(`
        <div class="card mb-3">
          <div class="card-header">Chỗ trống theo khu vực</div>
          <div class="card-body">
            <div class="row g-3">${summary || '<div class="col text-muted">Chưa có khu vực.</div>'}</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Sơ đồ vị trí đỗ</span>
            <div class="d-flex gap-3 small">
              <span><span class="badge bg-success me-1">■</span>Còn trống</span>
              <span><span class="badge bg-danger me-1">■</span>Đang sử dụng</span>
            </div>
          </div>
          <div class="card-body">
            <div class="slot-grid">${grid || '<div class="text-muted">Chưa có vị trí đỗ.</div>'}</div>
          </div>
        </div>`);
    } catch (err) {
      App.router.setContent(`<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`);
    }
  },
};
