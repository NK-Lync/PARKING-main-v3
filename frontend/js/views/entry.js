// ============================================================
// views/entry.js — ghi nhận xe vào bãi (thủ công + AI)
// ------------------------------------------------------------
// Hai lối vào song song: gõ tay biển số, hoặc để AI đọc biển số
// từ ảnh camera / ảnh tải lên. Cả hai đều gọi API ghi nhận xe vào.
// ============================================================

App.views.entry = {
  _loaixe: [],

  async render() {
    const U = App.ui;
    App.router.setTitle("Ghi nhận xe vào");
    App.router.setContent(U.spinner());
    await this.loadLoaixe();

    App.router.setContent(`
      <div class="xp-split deu-cao">
        ${U.card({
          title: "Nhập tay",
          note: "Dùng khi camera không đọc được biển số",
          body: `
            <form id="entry-form" class="xp-stack">
              ${U.field("Biển số xe", U.input({
                name: "bienso",
                placeholder: "VD: 29A-12345",
                required: true,
                autofocus: true,
              }))}
              ${U.field("Loại xe", U.select({
                name: "maloaixe",
                required: true,
                placeholder: "— Chọn loại xe —",
                options: this._loaixe.map((l) => ({
                  value: l.maloaixe,
                  label: `${l.tenloaixe} (${U.fmtMoney(l.dongia)}/giờ)`,
                })),
              }), "Loại xe quyết định đơn giá tính phí khi xe ra")}
              <div>
                <button type="submit" class="xp-btn xp-btn-primary" id="entry-btn">
                  ${App.icons.svg("log-in", 16)}Xe vào bãi
                </button>
              </div>
            </form>
            <div id="entry-result" class="xp-mt"></div>`,
        })}

        ${U.card({
          title: "Quét biển số bằng camera",
          note: "AI đọc biển số, phân loại xe rồi tự chọn vị trí trống",
          body: `
            <p class="xp-small xp-muted" style="margin-top:0">
              Bật camera, đưa biển số vào khung rồi bấm chụp.
            </p>
            ${App.camera.html("entry")}
            <div id="entry-ai-result" class="xp-mt"></div>
            <div class="xp-divider xp-mt"></div>
            ${U.field(
              "Hoặc tải ảnh từ máy",
              `<input type="file" class="xp-input xp-file" id="entry-image" accept="image/*">`
            )}
            <button class="xp-btn xp-btn-outline xp-btn-sm" id="entry-ai-btn">
              ${App.icons.svg("sparkles", 15)}Nhận diện ảnh đã chọn
            </button>`,
        })}
      </div>`);

    document.getElementById("entry-form").addEventListener("submit", (e) => this._submitManual(e));
    document.getElementById("entry-ai-btn").addEventListener("click", () => this._submitAI());
    App.camera.mount("entry", { onAnh: (blob, ten) => this._goiAI(blob, ten) });
  },

  async loadLoaixe() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._loaixe = res.data || [];
    } catch (err) {
      /* Danh sách rỗng thì ô chọn không có lựa chọn nào; lỗi thật
         sẽ hiện khi bấm gửi. */
    }
  },

  // Khối báo xe đã vào bãi, kèm vị trí vừa được xếp.
  _ketQua(res) {
    const U = App.ui;
    const d = res.data || {};
    const vitri = d.vitri || {};
    const soViTri = vitri.mavitri ?? d.luotgui?.mavitri ?? "—";
    const khuVuc = vitri.tenkhuvuc || "—";

    return `
      <div class="xp-alert ok">
        ${U.icon("check-circle", 17)}
        <div>
          <div class="xp-alert-title">${U.escape(res.message || "Xe vào bãi thành công")}</div>
          <div class="xp-small">Vị trí <b>#${U.escape(soViTri)}</b> · Khu vực <b>${U.escape(khuVuc)}</b></div>
        </div>
      </div>`;
  },

  async _submitManual(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const btn = document.getElementById("entry-btn");
    const box = document.getElementById("entry-result");
    btn.disabled = true;
    box.innerHTML = App.ui.spinner("Đang ghi nhận…");

    try {
      const res = await App.api.post("/api/parking/entry", {
        bienso: String(fd.get("bienso") || "").trim(),
        maloaixe: Number(fd.get("maloaixe")),
      });
      box.innerHTML = this._ketQua(res);
      e.target.reset();
      App.ui.toast("Đã ghi nhận xe vào bãi.");
    } catch (err) {
      box.innerHTML = App.ui.alertLoi(err);
    } finally {
      btn.disabled = false;
    }
  },

  async _submitAI() {
    const input = document.getElementById("entry-image");

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
    const btn = document.getElementById("entry-ai-btn");
    const box = document.getElementById("entry-ai-result");

    const formData = new FormData();
    formData.append("image", blob, ten || "image.jpg");

    btn.disabled = true;
    box.innerHTML = U.spinner("AI đang nhận diện…");

    try {
      const res = await App.api.upload("/api/parking/ai-entry", formData);
      const ai = res.ai || {};
      box.innerHTML = `
        <div class="xp-alert ok">
          ${U.icon("check-circle", 17)}
          <div>
            <div class="xp-alert-title">${U.escape(res.message || "Xe vào bãi thành công")}</div>
            <div class="xp-small">
              Biển số <b>${U.escape(ai.bienso || "—")}</b>
              · Loại xe <b>${U.escape(res.loaixe?.tenloaixe || "—")}</b>
              · Vị trí AI <b>#${U.escape(res.mavitri_ai ?? "—")}</b>
            </div>
          </div>
        </div>`;
    } catch (err) {
      box.innerHTML = U.alertLoi(err);
    } finally {
      btn.disabled = false;
    }
  },
};
