// ============================================================
// views/thongke.js — thống kê lưu lượng & doanh thu
// ------------------------------------------------------------
// Không chọn ngày thì API trả số liệu của toàn bộ thời gian,
// nên nhãn trên màn hình phải đổi theo cho khỏi hiểu nhầm là
// "hôm nay".
// ============================================================

App.views.thongke = {
  async render() {
    App.router.setTitle("Thống kê");
    App.router.setContent(App.ui.spinner());

    try {
      const ptRes = await App.api.get("/api/thongke/phan-tich");
      const pt = ptRes.data || {};

      App.router.setContent(this._khung(pt));

      document.getElementById("tk-ngay").addEventListener("change", () => this.loadDaily());
      document.getElementById("tk-clear").addEventListener("click", () => {
        document.getElementById("tk-ngay").value = "";
        this.loadDaily();
      });

      await this.loadDaily();
    } catch (err) {
      App.router.setContent(App.ui.alertLoi(err));
    }
  },

  _khung(pt) {
    const U = App.ui;

    return `
      <div class="xp-stack">
        ${U.card({
          flush: true,
          body: `
            <div class="xp-card-head" style="border-bottom:0">
              <div>
                <div class="xp-card-title">Khoảng thời gian</div>
                <div class="xp-card-note" id="tk-nhan">Toàn bộ thời gian</div>
              </div>
              <div class="xp-card-head-right">
                <input type="date" class="xp-input" id="tk-ngay" style="width:170px">
                <button class="xp-btn xp-btn-outline" id="tk-clear">
                  ${App.icons.svg("refresh", 15)}Tất cả
                </button>
              </div>
            </div>`,
        })}

        <div class="xp-grid cols-4" id="tk-cards">${U.spinner("Đang tải số liệu…")}</div>

        ${U.card({
          title: "Lưu lượng xe theo giờ",
          note: "Số lượt xe vào bãi, gom theo giờ ghi nhận",
          body: `<div class="xp-chart tall"><canvas id="chart-luuluong"></canvas></div>`,
        })}

        ${U.card({
          title: "Tổng hợp toàn hệ thống",
          note: "Không phụ thuộc khoảng thời gian đang chọn",
          body: `
            <div class="xp-grid cols-4">
              <div>
                <div class="xp-fig-label">Tổng lượt gửi xe</div>
                <div class="xp-fig-value">${pt.tong_luot_gui ?? 0}</div>
              </div>
              <div>
                <div class="xp-fig-label">Xe đang trong bãi</div>
                <div class="xp-fig-value">${pt.so_xe_dang_gui ?? 0}</div>
              </div>
              <div>
                <div class="xp-fig-label">Tổng số vị trí</div>
                <div class="xp-fig-value">${pt.tong_so_vi_tri ?? 0}</div>
              </div>
              <div>
                <div class="xp-fig-label">Vé tháng hiệu lực</div>
                <div class="xp-fig-value">${pt.so_ve_thang_hieu_luc ?? 0}</div>
              </div>
            </div>`,
        })}
      </div>`;
  },

  async loadDaily() {
    const o = document.getElementById("tk-ngay");
    const nhan = document.getElementById("tk-nhan");
    const ngay = o.value;
    const q = ngay ? `?ngay=${ngay}` : "";

    nhan.textContent = ngay
      ? `Ngày ${App.ui.fmtDate(ngay)}`
      : "Toàn bộ thời gian";

    try {
      const [llRes, dtRes] = await Promise.all([
        App.api.get(`/api/thongke/luu-luong${q}`),
        App.api.get(`/api/thongke/doanh-thu${q}`),
      ]);
      const ll = llRes.data || {};
      const dt = dtRes.data || {};

      const daTra = dt.so_luot_da_tra ?? 0;
      const doanhThu = dt.tong_doanh_thu ?? 0;

      document.getElementById("tk-cards").innerHTML = `
        ${App.ui.stat({
          label: "Tổng lượt xe",
          value: ll.tong_luot ?? 0,
          icon: "trending",
          hint: ngay ? "trong ngày đã chọn" : "toàn bộ thời gian",
        })}
        ${App.ui.stat({
          label: "Doanh thu",
          value: App.ui.fmtMoney(doanhThu),
          icon: "wallet",
          hint: ngay ? "thu trong ngày" : "tổng đã thu",
        })}
        ${App.ui.stat({
          label: "Lượt đã trả",
          value: daTra,
          tone: "ok",
          icon: "check-circle",
          hint: "xe đã ra khỏi bãi",
        })}
        ${App.ui.stat({
          label: "Bình quân mỗi lượt",
          value: daTra ? App.ui.fmtMoney(Math.round(doanhThu / daTra)) : "—",
          icon: "chart",
          hint: "doanh thu chia số lượt trả",
        })}`;

      const theoGio = ll.theo_gio || {};
      const gio = Object.keys(theoGio);

      App.charts.bar(
        "chart-luuluong",
        gio.map((g) => g + "h"),
        [
          {
            label: "Lượt xe vào",
            data: gio.map((g) => theoGio[g]),
            backgroundColor: App.charts.MAU.accentNhat,
            borderRadius: 4,
            maxBarThickness: 34,
          },
        ],
        "luuluong"
      );
    } catch (err) {
      document.getElementById("tk-cards").innerHTML = App.ui.alertLoi(err);
    }
  },
};
