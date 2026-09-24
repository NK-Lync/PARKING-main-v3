// ============================================================
// views/thongke.js — thống kê lưu lượng & doanh thu
// ============================================================

App.views.thongke = {
  async render() {
    App.router.setTitle("Thống kê");
    App.router.setContent(App.ui.spinner());

    try {
      const ptRes = await App.api.get("/api/thongke/phan-tich");
      const pt = ptRes.data || {};

      App.router.setContent(`
        <div class="card mb-3">
          <div class="card-body d-flex flex-wrap align-items-center gap-3">
            <label class="fw-semibold">Ngày thống kê</label>
            <input type="date" class="form-control" style="max-width:200px" id="tk-ngay">
            <button class="btn btn-outline-secondary" id="tk-clear">Tất cả</button>
          </div>
        </div>

        <div class="row g-3 mb-3" id="tk-cards">${App.ui.spinner("Đang tải số liệu theo ngày…")}</div>

        <div class="row g-3">
          <div class="col-12">
            <div class="card">
              <div class="card-header">Lưu lượng xe theo giờ</div>
              <div class="card-body">
                <div class="chart-box"><canvas id="chart-luuluong"></canvas></div>
              </div>
            </div>
          </div>
        </div>`);

      document.getElementById("tk-ngay").addEventListener("change", () => this.loadDaily());
      document.getElementById("tk-clear").addEventListener("click", () => {
        document.getElementById("tk-ngay").value = "";
        this.loadDaily();
      });

      await this.loadDaily();
    } catch (err) {
      App.router.setContent(`<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`);
    }
  },

  async loadDaily() {
    const ngay = document.getElementById("tk-ngay").value;
    const q = ngay ? `?ngay=${ngay}` : "";

    try {
      const [llRes, dtRes] = await Promise.all([
        App.api.get(`/api/thongke/luu-luong${q}`),
        App.api.get(`/api/thongke/doanh-thu${q}`),
      ]);
      const ll = llRes.data || {};
      const dt = dtRes.data || {};

      document.getElementById("tk-cards").innerHTML = `
        <div class="col-6 col-lg-3">
          <div class="card stat-card h-100"><div class="card-body">
            <div class="stat-label">Tổng lượt xe</div>
            <div class="stat-value">${ll.tong_luot ?? 0}</div>
          </div></div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card stat-card h-100"><div class="card-body">
            <div class="stat-label">Doanh thu</div>
            <div class="stat-value">${App.ui.fmtMoney(dt.tong_doanh_thu)}</div>
          </div></div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card stat-card h-100"><div class="card-body">
            <div class="stat-label">Lượt đã trả</div>
            <div class="stat-value">${dt.so_luot_da_tra ?? 0}</div>
          </div></div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card stat-card h-100"><div class="card-body">
            <div class="stat-label">Đơn giá trung bình</div>
            <div class="stat-value">${dt.so_luot_da_tra ? App.ui.fmtMoney(Math.round(dt.tong_doanh_thu / dt.so_luot_da_tra)) : "—"}</div>
          </div></div>
        </div>`;

      const theoGio = ll.theo_gio || {};
      const labels = Object.keys(theoGio).map((g) => g + "h");
      const values = Object.keys(theoGio).map((g) => theoGio[g]);

      App.charts.bar(
        "chart-luuluong",
        labels,
        [{
          label: "Lượt xe vào",
          data: values,
          backgroundColor: "rgba(13,110,253,0.7)",
          borderRadius: 4,
        }],
        "luuluong"
      );
    } catch (err) {
      document.getElementById("tk-cards").innerHTML =
        `<div class="col"><div class="alert alert-danger">${App.ui.escape(err.message)}</div></div>`;
    }
  },
};
