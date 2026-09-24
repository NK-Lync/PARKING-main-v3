// ============================================================
// views/entry.js — ghi nhận xe vào bãi (thủ công + AI)
// ============================================================

App.views.entry = {
  _loaixe: [],

  async render() {
    App.router.setTitle("Ghi nhận xe vào");
    App.router.setContent(App.ui.spinner());
    await this.loadLoaixe();

    App.router.setContent(`
      <div class="row g-3">
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">Nhập tay</div>
            <div class="card-body">
              <form id="entry-form">
                <div class="mb-3">
                  <label class="form-label">Biển số xe</label>
                  <input type="text" class="form-control" name="bienso" placeholder="VD: 29A-12345" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Loại xe</label>
                  <select class="form-select" name="maloaixe" required>
                    <option value="">— Chọn loại xe —</option>
                    ${this._loaixe.map((l) => `<option value="${l.maloaixe}">${App.ui.escape(l.tenloaixe)} (${App.ui.fmtMoney(l.dongia)}/giờ)</option>`).join("")}
                  </select>
                </div>
                <button type="submit" class="btn btn-primary" id="entry-btn">
                  <i class="bi bi-box-arrow-in-right me-1"></i>Xe vào bãi
                </button>
              </form>
              <div id="entry-result" class="mt-3"></div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">Nhận diện bằng AI</div>
            <div class="card-body">
              <p class="text-muted small">Tải ảnh chụp xe tại cổng vào. AI sẽ nhận diện biển số, loại xe và vị trí đỗ.</p>
              <input type="file" class="form-control mb-3" id="entry-image" accept="image/*">
              <button class="btn btn-outline-primary" id="entry-ai-btn">
                <i class="bi bi-stars me-1"></i>Nhận diện & ghi nhận
              </button>
              <div id="entry-ai-result" class="mt-3"></div>
            </div>
          </div>
        </div>
      </div>`);

    document.getElementById("entry-form").addEventListener("submit", (e) => this._submitManual(e));
    document.getElementById("entry-ai-btn").addEventListener("click", () => this._submitAI());
  },

  async loadLoaixe() {
    try {
      const res = await App.api.get("/api/loaixe");
      this._loaixe = res.data || [];
    } catch (err) { /* xử lý ở render */ }
  },

  async _submitManual(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const btn = document.getElementById("entry-btn");
    const box = document.getElementById("entry-result");
    btn.disabled = true;
    box.innerHTML = "";

    try {
      const res = await App.api.post("/api/parking/entry", {
        bienso: fd.get("bienso").trim(),
        maloaixe: Number(fd.get("maloaixe")),
      });
      const d = res.data || {};
      const vitri = d.vitri || {};
      box.innerHTML = `
        <div class="alert alert-success">
          <i class="bi bi-check-circle me-1"></i>${App.ui.escape(res.message || "Xe vào bãi thành công")}
          <div class="small mt-1">Vị trí #${vitri.mavitri ?? d.luotgui?.mavitri ?? "—"} · Khu vực ${App.ui.escape(vitri.tenkhuvuc || "—")}</div>
        </div>`;
      e.target.reset();
    } catch (err) {
      box.innerHTML = `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    } finally {
      btn.disabled = false;
    }
  },

  async _submitAI() {
    const input = document.getElementById("entry-image");
    const btn = document.getElementById("entry-ai-btn");
    const box = document.getElementById("entry-ai-result");

    if (!input.files || !input.files[0]) {
      App.ui.toast("Vui lòng chọn ảnh trước.", "danger");
      return;
    }

    const formData = new FormData();
    formData.append("image", input.files[0]);

    btn.disabled = true;
    box.innerHTML = App.ui.spinner("AI đang nhận diện…");

    try {
      const res = await App.api.upload("/api/parking/ai-entry", formData);
      const ai = res.ai || {};
      box.innerHTML = `
        <div class="alert alert-success">
          <i class="bi bi-check-circle me-1"></i>${App.ui.escape(res.message || "Xe vào bãi thành công")}
          <div class="small mt-1">Biển số <b>${App.ui.escape(ai.bienso || "—")}</b> · Loại xe ${App.ui.escape(res.loaixe?.tenloaixe || "—")} · Vị trí AI #${res.mavitri_ai ?? "—"}</div>
        </div>`;
      input.value = "";
    } catch (err) {
      box.innerHTML = `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    } finally {
      btn.disabled = false;
    }
  },
};
