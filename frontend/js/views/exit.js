// ============================================================
// views/exit.js — ghi nhận xe ra khỏi bãi (thủ công + AI)
// ------------------------------------------------------------
// Khi xe ra, hệ thống tính phí theo số giờ gửi và giải phóng vị
// trí. Xe có vé tháng còn hiệu lực được miễn phí.
// ============================================================

App.views.exit = {
  async render() {
    const U = App.ui;
    App.router.setTitle("Ghi nhận xe ra");
    App.router.setContent(`
      <div class="xp-split deu-cao">
        ${U.card({
          title: "Nhập tay",
          note: "Dùng khi camera không đọc được biển số",
          body: `
            <form id="exit-form" class="xp-stack">
              ${U.field("Biển số xe", U.input({
                name: "bienso",
                placeholder: "VD: 29A-12345",
                required: true,
                autofocus: true,
              }), "Phải khớp với biển số lúc xe vào thì mới tìm ra lượt gửi")}
              <div>
                <button type="submit" class="xp-btn xp-btn-primary" id="exit-btn">
                  ${App.icons.svg("log-out", 16)}Xe ra bãi
                </button>
              </div>
            </form>
            <div id="exit-result" class="xp-mt"></div>`,
        })}

        ${U.card({
          title: "Quét biển số bằng camera",
          note: "AI đọc biển số rồi tính phí và giải phóng vị trí",
          body: `
            <p class="xp-small xp-muted" style="margin-top:0">
              Bật camera, đưa biển số vào khung rồi bấm chụp.
            </p>
            ${App.camera.html("exit")}
            <div id="exit-ai-result" class="xp-mt"></div>
            <div class="xp-divider xp-mt"></div>
            ${U.field(
              "Hoặc tải ảnh từ máy",
              `<input type="file" class="xp-input xp-file" id="exit-image" accept="image/*">`
            )}
            <button class="xp-btn xp-btn-outline xp-btn-sm" id="exit-ai-btn">
              ${App.icons.svg("sparkles", 15)}Nhận diện ảnh đã chọn
            </button>`,
        })}
      </div>`);

    document.getElementById("exit-form").addEventListener("submit", (e) => this._submitManual(e));
    document.getElementById("exit-ai-btn").addEventListener("click", () => this._submitAI());
    App.camera.mount("exit", { onAnh: (blob, ten) => this._goiAI(blob, ten) });
  },

  // Phiếu tính phí sau khi xe ra.
  _receipt(d) {
    const U = App.ui;
    return `
      <div class="xp-receipt">
        <div class="xp-receipt-head">
          <span style="display:flex;color:var(--xp-ok)">${U.icon("check-circle", 18)}</span>
          <span class="xp-bold">Xe ra khỏi bãi thành công</span>
          <span class="xp-receipt-total">${U.fmtMoney(d.tongphi)}</span>
        </div>
        <div class="xp-receipt-rows">
          <div>Biển số: <b>${U.escape(d.bienso || "—")}</b></div>
          <div>Vị trí: <b>#${U.escape(d.mavitri ?? "—")}</b></div>
          <div>Vào: ${U.fmtDateTime(d.thoigianvao)}</div>
          <div>Ra: ${U.fmtDateTime(d.thoigianra)}</div>
          <div>Thời gian gửi: <b>${d.thoigian_gui_phut ?? 0}</b> phút</div>
          <div>Số giờ tính phí: <b>${d.so_gio_tinh_phi ?? 0}</b> giờ</div>
          ${
            d.co_ve_thang
              ? `<div style="grid-column:1/-1">${U.badge("Có vé tháng — miễn phí", "info")}</div>`
              : ""
          }
        </div>
      </div>`;
  },

  async _submitManual(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const btn = document.getElementById("exit-btn");
    const box = document.getElementById("exit-result");
    btn.disabled = true;
    box.innerHTML = App.ui.spinner("Đang tính phí…");

    try {
      const res = await App.api.post("/api/parking/exit", {
        bienso: String(fd.get("bienso") || "").trim(),
      });
      box.innerHTML = this._receipt(res.data || {});
      e.target.reset();
    } catch (err) {
      box.innerHTML = App.ui.alertLoi(err);
    } finally {
      btn.disabled = false;
    }
  },

  async _submitAI() {
    const input = document.getElementById("exit-image");

    if (!input.files || !input.files[0]) {
      App.ui.toast("Vui lòng chọn ảnh trước.", "danger");
      return;
    }

    const f = input.files[0];
    await this._goiAI(f, f.name);
    input.value = "";
  },

  // Gửi một ảnh (từ camera, ảnh mẫu, hay file chọn tay) lên AI.
  async _goiAI(blob, ten) {
    const U = App.ui;
    const btn = document.getElementById("exit-ai-btn");
    const box = document.getElementById("exit-ai-result");

    const formData = new FormData();
    formData.append("image", blob, ten || "image.jpg");

    btn.disabled = true;
    box.innerHTML = U.spinner("AI đang nhận diện…");

    try {
      const res = await App.api.upload("/api/parking/ai-exit", formData);
      const d = res.parking?.data || {};
      box.innerHTML = this._receipt(d);
    } catch (err) {
      box.innerHTML = U.alertLoi(err);
    } finally {
      btn.disabled = false;
    }
  },
};
