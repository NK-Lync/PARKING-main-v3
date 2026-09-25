// ============================================================
// views/ai.js — AI hỗ trợ phân tích (GenAI)
// ------------------------------------------------------------
// Ba phân tích dựng sẵn, cộng một ô hỏi đáp tự do. Câu trả lời có
// thể do Gemini sinh ra hoặc do lớp phân tích nội bộ tính, nên
// mỗi kết quả đều ghi rõ nguồn.
// ============================================================

App.views.ai = {
  _phanTich: [
    {
      key: "bao-cao",
      title: "Báo cáo lưu lượng",
      desc: "Tổng hợp số liệu lượt xe gửi thành báo cáo ngắn gọn.",
      icon: "file",
      path: "/api/ai/bao-cao-luu-luong",
    },
    {
      key: "gio-cao-diem",
      title: "Phân tích giờ cao điểm",
      desc: "Xác định khung giờ có lưu lượng xe cao nhất.",
      icon: "trending",
      path: "/api/ai/gio-cao-diem",
    },
    {
      key: "nhan-su",
      title: "Gợi ý bố trí nhân sự",
      desc: "Đề xuất bố trí nhân viên theo lưu lượng từng khung giờ.",
      icon: "users",
      path: "/api/ai/goi-y-nhan-su",
    },
  ],

  async render() {
    const U = App.ui;
    App.router.setTitle("AI hỗ trợ");

    App.router.setContent(`
      <div class="xp-stack">
        <div class="xp-grid">${this._phanTich.map((p) => this._the(p)).join("")}</div>

        <div class="xp-split">
          ${U.card({
            title: "Hỏi đáp dữ liệu",
            note: "Hỏi về doanh thu, số xe đang gửi, số vị trí hoặc vé tháng",
            body: `
              <div class="xp-input-group">
                <input type="text" class="xp-input" id="ai-question"
                       placeholder="VD: Hôm nay doanh thu bao nhiêu?">
                <button class="xp-btn xp-btn-primary" id="ai-ask">
                  ${App.icons.svg("send", 15)}Hỏi
                </button>
              </div>
              <div id="ai-answer" class="xp-mt"></div>`,
          })}

          ${U.card({
            title: "Kết quả phân tích",
            note: "Do AI sinh ra, hoặc do lớp phân tích nội bộ tính khi AI hết hạn mức",
            body: `<div id="ai-result">${U.empty("Chọn một phân tích ở trên để bắt đầu.")}</div>`,
          })}
        </div>
      </div>`);

    document.getElementById("ai-ask").addEventListener("click", () => this.ask());
    document.getElementById("ai-question").addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.ask();
    });

    this._phanTich.forEach((p) => {
      document.getElementById(`ai-${p.key}`).addEventListener("click", () => this.runAction(p));
    });
  },

  // Thẻ mô tả một phân tích dựng sẵn.
  _the(p) {
    const U = App.ui;
    return `
      <div class="xp-card">
        <div class="xp-card-body xp-stack" style="gap:10px">
          <div class="xp-row" style="flex-wrap:nowrap">
            <span style="display:flex;color:var(--xp-accent)">${U.icon(p.icon, 18)}</span>
            <span class="xp-bold">${U.escape(p.title)}</span>
          </div>
          <p class="xp-small xp-muted" style="margin:0">${U.escape(p.desc)}</p>
          <div>
            <button class="xp-btn xp-btn-outline xp-btn-sm" id="ai-${p.key}">
              ${U.icon("sparkles", 14)}Chạy phân tích
            </button>
          </div>
        </div>
      </div>`;
  },

  // Nguồn của câu trả lời: Gemini hay lớp tính toán nội bộ.
  _nguon(r) {
    if (!r || !r.nguon) return "";
    return r.nguon === "genai"
      ? App.ui.badge("Gemini", "info")
      : App.ui.badge("Phân tích nội bộ", "neutral");
  },

  _ketQua(title, r) {
    const U = App.ui;
    const noiDung = (r && (r.noi_dung || r.cau_tra_loi)) || "—";
    return `
      <div class="xp-row" style="justify-content:space-between;margin-bottom:10px">
        <span class="xp-bold">${U.escape(title)}</span>
        ${this._nguon(r)}
      </div>
      <div class="xp-bubble tra-loi md">${App.md.render(noiDung)}</div>`;
  },

  async runAction(p) {
    const box = document.getElementById("ai-result");
    box.innerHTML = App.ui.spinner("AI đang phân tích…");

    try {
      const res = await App.api.post(p.path);
      box.innerHTML = this._ketQua(p.title, res.data);
    } catch (err) {
      box.innerHTML = App.ui.alertLoi(err);
    }
  },

  async ask() {
    const input = document.getElementById("ai-question");
    const box = document.getElementById("ai-answer");
    const cauHoi = input.value.trim();
    if (!cauHoi) return;

    box.innerHTML = App.ui.spinner("Đang trả lời…");

    try {
      const res = await App.api.post("/api/ai/hoi-dap", { cau_hoi: cauHoi });
      const r = res.data || {};
      box.innerHTML = `
        <div class="xp-stack" style="gap:10px">
          <div class="xp-bubble cau-hoi">${App.ui.escape(cauHoi)}</div>
          <div class="xp-row">${this._nguon(r)}</div>
          <div class="xp-bubble tra-loi md">${App.md.render(r.cau_tra_loi || "—")}</div>
        </div>`;
      input.value = "";
    } catch (err) {
      box.innerHTML = App.ui.alertLoi(err);
    }
  },
};
