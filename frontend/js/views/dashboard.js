// ============================================================
// views/dashboard.js — tổng quan bãi xe
// ============================================================

App.views.dashboard = {
  async render() {
    App.router.setTitle("Dashboard");
    App.router.setContent(App.ui.spinner());

    try {
      const [statusRes, ptRes] = await Promise.all([
        App.api.get("/api/parking/status"),
        App.api.get("/api/thongke/phan-tich"),
      ]);

      const s = statusRes.data || {};
      const pt = ptRes.data || {};

      const xe = s.xe_dang_gui || [];
      const conTrong = s.con_trong ?? 0;
      const dangSuDung = s.dang_su_dung ?? 0;
      const tyLe = s.ty_le_lap_day ?? 0;

      App.router.setContent(`
        <div class="row g-3 mb-3">
          ${this._stat("Tổng vị trí", s.tong_vi_tri ?? 0, "bi-p-square", "primary")}
          ${this._stat("Đang sử dụng", dangSuDung, "bi-car-front-fill", "danger")}
          ${this._stat("Còn trống", conTrong, "bi-check-circle", "success")}
          ${this._stat("Tỷ lệ lấp đầy", tyLe + "%", "bi-percent", "warning")}
        </div>

        <div class="row g-3">
          <div class="col-lg-5">
            <div class="card h-100">
              <div class="card-header">Mức độ lấp đầy</div>
              <div class="card-body">
                <div class="chart-box"><canvas id="chart-occupancy"></canvas></div>
              </div>
            </div>
          </div>
          <div class="col-lg-7">
            <div class="card h-100">
              <div class="card-header">Xe đang gửi trong bãi (${xe.length})</div>
              <div class="card-body p-0">
                ${this._vehicles(xe)}
              </div>
            </div>
          </div>
        </div>

        <div class="row g-3 mt-1">
          <div class="col-lg-4">${this._mini("Tổng doanh thu", App.ui.fmtMoney(pt.tong_doanh_thu), "bi-cash-stack", "success")}</div>
          <div class="col-lg-4">${this._mini("Lượt đã trả", pt.so_luot_da_tra ?? 0, "bi-receipt", "info")}</div>
          <div class="col-lg-4">${this._mini("Vé tháng hiệu lực", pt.so_ve_thang_hieu_luc ?? 0, "bi-calendar-check", "primary")}</div>
        </div>`);

      App.charts.doughnut(
        "chart-occupancy",
        ["Đang sử dụng", "Còn trống"],
        [dangSuDung, conTrong],
        "occupancy"
      );
    } catch (err) {
      App.router.setContent(this._error(err));
    }
  },

  _stat(label, value, icon, color) {
    return `
      <div class="col-6 col-lg-3">
        <div class="card stat-card h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-${color}"><i class="bi ${icon}"></i></div>
            <div>
              <div class="stat-value">${value}</div>
              <div class="stat-label">${label}</div>
            </div>
          </div>
        </div>
      </div>`;
  },

  _mini(label, value, icon, color) {
    return `
      <div class="card stat-card h-100">
        <div class="card-body d-flex align-items-center gap-3">
          <div class="stat-icon bg-${color}"><i class="bi ${icon}"></i></div>
          <div>
            <div class="stat-value">${value}</div>
            <div class="stat-label">${label}</div>
          </div>
        </div>
      </div>`;
  },

  _vehicles(vehicles) {
    if (!vehicles.length) {
      return '<div class="p-4 text-center text-muted">Hiện không có xe nào đang gửi.</div>';
    }
    const rows = vehicles.map((v) => `
      <tr>
        <td class="fw-semibold">${App.ui.escape(v.bienso)}</td>
        <td>${App.ui.escape(v.tenkhuvuc || "—")}</td>
        <td>#${v.mavitri ?? "—"}</td>
        <td>${App.ui.fmtDateTime(v.thoigianvao)}</td>
      </tr>`).join("");
    return `
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr><th>Biển số</th><th>Khu vực</th><th>Vị trí</th><th>Giờ vào</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  },

  _error(err) {
    return `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-1"></i>${App.ui.escape(err.message)}</div>`;
  },
};
