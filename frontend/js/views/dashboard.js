// ============================================================
// views/dashboard.js — màn hình tổng quan
// ------------------------------------------------------------
// Gọi hai API:
//   GET /api/parking/status     -> tình trạng chỗ đỗ + xe đang gửi
//   GET /api/thongke/phan-tich  -> số liệu tổng hợp
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

      App.router.setContent(this._khung(s, pt));
      this._veBieuDo(s, pt);
    } catch (err) {
      App.router.setContent(App.ui.alertLoi(err));
    }
  },

  // Định dạng phần trăm kiểu Việt Nam: dấu phẩy làm dấu thập phân.
  _pc(x) {
    const n = Number(x) || 0;
    return n.toLocaleString("vi-VN", { maximumFractionDigits: 2 }) + "%";
  },

  _khung(s, pt) {
    const U = App.ui;

    const tongViTri = s.tong_vi_tri ?? 0;
    const dangDung = s.dang_su_dung ?? 0;
    const conTrong = s.con_trong ?? 0;
    const tyLe = Number(s.ty_le_lap_day) || 0;

    // Bãi chật thì đổi màu thẻ tỉ lệ lấp đầy để cảnh báo sớm.
    const toneTyLe = tyLe >= 90 ? "err" : tyLe >= 70 ? "warn" : "ok";

    const theSoLieu = `
      <div class="xp-grid cols-4">
        ${U.stat({
          label: "Tổng vị trí",
          value: tongViTri,
          icon: "parking",
          hint: "Toàn bộ bãi xe",
        })}
        ${U.stat({
          label: "Đang sử dụng",
          value: dangDung,
          tone: "warn",
          icon: "car",
          hint: `${dangDung}/${tongViTri} chỗ đã có xe`,
        })}
        ${U.stat({
          label: "Còn trống",
          value: conTrong,
          tone: conTrong > 0 ? "ok" : "err",
          icon: "check-circle",
          hint: conTrong > 0 ? "Sẵn sàng đón xe" : "Bãi đã kín",
        })}
        ${U.stat({
          label: "Tỷ lệ lấp đầy",
          value: this._pc(tyLe),
          tone: toneTyLe,
          icon: "chart",
          hint: tyLe >= 90 ? "Bãi gần như kín" : "Mức sử dụng hiện tại",
        })}
      </div>`;

    const bangXe = U.table(
      [
        { label: "Biển số", key: "bienso", strong: true },
        { label: "Khu vực", key: "tenkhuvuc", render: (v) => U.escape(v || "—") },
        { label: "Vị trí", key: "mavitri", render: (v) => (v == null ? "—" : `#${v}`) },
        { label: "Giờ vào", key: "thoigianvao", render: (v) => U.fmtDateTime(v) },
        { label: "Trạng thái", key: "tinhtrang", render: (v) => U.statusBadge(v) },
      ],
      s.xe_dang_gui || [],
      "Hiện không có xe nào trong bãi."
    );

    return `
      <div class="xp-stack">
        ${theSoLieu}

        <div class="xp-split narrow-left">
          ${U.card({
            title: "Cơ cấu chỗ đỗ",
            note: `${dangDung} chỗ đang dùng · ${conTrong} chỗ trống`,
            body: `<div class="xp-chart"><canvas id="chart-occupancy"></canvas></div>`,
          })}

          ${U.card({
            title: "Lượt xe vào theo giờ",
            note: "Tính từ lúc ghi nhận xe vào",
            body: `<div class="xp-chart"><canvas id="chart-luuluong"></canvas></div>`,
          })}
        </div>

        ${U.card({
          title: "Xe đang gửi trong bãi",
          note: `${(s.xe_dang_gui || []).length} lượt chưa trả`,
          actions: `<a class="xp-btn xp-btn-outline xp-btn-sm" href="#/lichsu">
            ${App.icons.svg("history", 15)}Tra cứu lịch sử
          </a>`,
          flush: true,
          body: bangXe,
        })}

        ${U.card({
          title: "Hoạt động tích lũy",
          note: "Số liệu tính từ trước tới nay",
          body: `
            <div class="xp-grid cols-4">
              <div>
                <div class="xp-fig-label">Tổng lượt gửi xe</div>
                <div class="xp-fig-value">${pt.tong_luot_gui ?? 0}</div>
                <div class="xp-fig-note">lượt đã ghi nhận</div>
              </div>
              <div>
                <div class="xp-fig-label">Lượt đã trả</div>
                <div class="xp-fig-value">${pt.so_luot_da_tra ?? 0}</div>
                <div class="xp-fig-note">xe đã ra khỏi bãi</div>
              </div>
              <div>
                <div class="xp-fig-label">Doanh thu</div>
                <div class="xp-fig-value">${App.ui.fmtMoney(pt.tong_doanh_thu)}</div>
                <div class="xp-fig-note">tổng phí đã thu</div>
              </div>
              <div>
                <div class="xp-fig-label">Vé tháng hiệu lực</div>
                <div class="xp-fig-value">${pt.so_ve_thang_hieu_luc ?? 0}</div>
                <div class="xp-fig-note">khách đăng ký dài hạn</div>
              </div>
            </div>`,
        })}
      </div>`;
  },

  _veBieuDo(s, pt) {
    // Vòng tròn cơ cấu chỗ đỗ. Thứ tự khớp bảng màu của App.charts:
    // ô đầu là màu xanh (trống), ô sau là màu hổ phách (đang dùng).
    App.charts.doughnut(
      "chart-occupancy",
      ["Còn trống", "Đang sử dụng"],
      [s.con_trong ?? 0, s.dang_su_dung ?? 0],
      "occupancy"
    );

    const theoGio = pt.luu_luong_theo_gio || {};
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
          maxBarThickness: 26,
        },
      ],
      "luuluong"
    );
  },
};
