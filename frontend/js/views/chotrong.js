// ============================================================
// views/chotrong.js — theo dõi chỗ trống (sơ đồ vị trí + tổng hợp)
// ============================================================

App.views.chotrong = {
  async render() {
    App.router.setTitle("Theo dõi chỗ trống");
    App.router.setContent(App.ui.spinner());

    try {
      const [kvRes, vtRes, dsKvRes] = await Promise.all([
        App.api.get("/api/khuvuc/cho-trong"),
        App.api.get("/api/vitrido"),
        App.api.get("/api/khuvuc"),
      ]);

      const khuVucs = kvRes.data || [];
      const viTris = vtRes.data || [];

      // Bảng vitrido chỉ lưu khóa ngoại makhuvuc, nên phải tra tên
      // khu vực qua danh sách khu vực.
      const tenKhuVuc = {};
      (dsKvRes.data || []).forEach((k) => {
        tenKhuVuc[k.makhuvuc] = k.tenkhuvuc;
      });
      const khuVucCua = (v) => tenKhuVuc[v.makhuvuc] || "—";

      App.router.setContent(this._khung(khuVucs, viTris, khuVucCua));
    } catch (err) {
      App.router.setContent(App.ui.alertLoi(err));
    }
  },

  _khung(khuVucs, viTris, khuVucCua) {
    const U = App.ui;

    const tongCho = viTris.length;
    const conTrong = viTris.filter((v) => v.trangthai === "Còn trống").length;
    const dangDung = tongCho - conTrong;

    // ---- Tổng hợp theo khu vực ----
    const theKhuVuc = khuVucs.length
      ? `<div class="xp-grid cols-4">
          ${khuVucs
            .map((k) =>
              U.stat({
                label: k.tenkhuvuc,
                value: k.so_cho_trong ?? 0,
                tone: (k.so_cho_trong ?? 0) > 0 ? "ok" : "err",
                icon: "parking",
                hint: `trống trên ${k.tong_so_vi_tri ?? 0} chỗ`,
              })
            )
            .join("")}
        </div>`
      : U.empty("Chưa có khu vực nào.");

    // ---- Sơ đồ từng vị trí ----
    const soDo = viTris.length
      ? `<div class="xp-slots">
          ${viTris
            .map((v) => {
              const trong = v.trangthai === "Còn trống";
              const khu = khuVucCua(v);
              return `
                <div class="xp-slot ${trong ? "trong" : "dung"}"
                     title="${U.escape(khu)} · vị trí #${v.mavitri}">
                  <span class="xp-slot-mark">
                    ${App.icons.svg(trong ? "check-circle" : "car", 17)}
                  </span>
                  <div class="xp-slot-code">#${v.mavitri}</div>
                  <div class="xp-slot-zone">${U.escape(khu)}</div>
                  <div class="xp-slot-state">${trong ? "Trống" : "Có xe"}</div>
                </div>`;
            })
            .join("")}
        </div>`
      : U.empty("Chưa có vị trí đỗ nào.");

    return `
      <div class="xp-stack">
        <div class="xp-grid cols-4">
          ${U.stat({
            label: "Tổng số chỗ",
            value: tongCho,
            icon: "parking",
            hint: "toàn bộ bãi xe",
          })}
          ${U.stat({
            label: "Đang có xe",
            value: dangDung,
            tone: "warn",
            icon: "car",
            hint: "chỗ đã bị chiếm",
          })}
          ${U.stat({
            label: "Còn trống",
            value: conTrong,
            tone: conTrong > 0 ? "ok" : "err",
            icon: "check-circle",
            hint: conTrong > 0 ? "có thể nhận xe vào" : "bãi đã kín",
          })}
          ${U.stat({
            label: "Số khu vực",
            value: khuVucs.length,
            icon: "map",
            hint: "khu đang hoạt động",
          })}
        </div>

        ${U.card({
          title: "Chỗ trống theo khu vực",
          note: "Số liệu lấy từ bảng khu vực",
          body: theKhuVuc,
        })}

        ${U.card({
          title: "Sơ đồ vị trí đỗ",
          note: `Cập nhật theo trạng thái hiện tại của từng vị trí`,
          actions: `
            <div class="xp-slot-legend">
              <span><i class="xp-swatch trong"></i>Trống</span>
              <span><i class="xp-swatch dung"></i>Đang có xe</span>
            </div>`,
          body: soDo,
        })}
      </div>`;
  },
};
