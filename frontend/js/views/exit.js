// ============================================================
// views/exit.js — ghi nhận xe ra khỏi bãi (thủ công + AI)
// ============================================================

App.views.exit = {
  async render() {
    App.router.setTitle("Ghi nhận xe ra");
    App.router.setContent(`
      <div class="row g-3">
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">Nhập tay</div>
            <div class="card-body">
              <form id="exit-form">
                <div class="mb-3">
                  <label class="form-label">Biển số xe</label>
                  <input type="text" class="form-control" name="bienso" placeholder="VD: 29A-12345" required>
                </div>
                <button type="submit" class="btn btn-primary" id="exit-btn">
                  <i class="bi bi-box-arrow-right me-1"></i>Xe ra bãi
                </button>
              </form>
              <div id="exit-result" class="mt-3"></div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">Nhận diện bằng AI</div>
            <div class="card-body">
              <p class="text-muted small">Tải ảnh chụp xe tại cổng ra. AI sẽ nhận diện biển số rồi tính phí và giải phóng vị trí.</p>
              <input type="file" class="form-control mb-3" id="exit-image" accept="image/*">
              <button class="btn btn-outline-primary" id="exit-ai-btn">
                <i class="bi bi-stars me-1"></i>Nhận diện & ghi nhận
              </button>
              <div id="exit-ai-result" class="mt-3"></div>
            </div>
          </div>
        </div>
      </div>`);

    document.getElementById("exit-form").addEventListener("submit", (e) => this._submitManual(e));
    document.getElementById("exit-ai-btn").addEventListener("click", () => this._submitAI());
  },

  _receipt(d) {
    return `
      <div class="alert alert-success">
        <div class="d-flex justify-content-between align-items-center">
          <span><i class="bi bi-check-circle me-1"></i>Xe ra khỏi bãi thành công</span>
          <span class="h4 mb-0">${App.ui.fmtMoney(d.tongphi)}</span>
        </div>
        <hr>
        <div class="small row g-2">
          <div class="col-6">Biển số: <b>${App.ui.escape(d.bienso)}</b></div>
          <div class="col-6">Vị trí: <b>#${d.mavitri ?? "—"}</b></div>
          <div class="col-6">Vào: ${App.ui.fmtDateTime(d.thoigianvao)}</div>
          <div class="col-6">Ra: ${App.ui.fmtDateTime(d.thoigianra)}</div>
          <div class="col-6">Thời gian gửi: ${d.thoigian_gui_phut ?? 0} phút</div>
          <div class="col-6">Số giờ tính phí: ${d.so_gio_tinh_phi ?? 0} giờ</div>
          <div class="col-12">${d.co_ve_thang ? App.ui.badge("Có vé tháng — miễn phí", "info") : ""}</div>
        </div>
      </div>`;
  },

  async _submitManual(e) {
    e.preventDefault();
    const fd = new FormData(e.target);
    const btn = document.getElementById("exit-btn");
    const box = document.getElementById("exit-result");
    btn.disabled = true;
    box.innerHTML = "";

    try {
      const res = await App.api.post("/api/parking/exit", { bienso: fd.get("bienso").trim() });
      box.innerHTML = this._receipt(res.data || {});
      e.target.reset();
    } catch (err) {
      box.innerHTML = `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    } finally {
      btn.disabled = false;
    }
  },

  async _submitAI() {
    const input = document.getElementById("exit-image");
    const btn = document.getElementById("exit-ai-btn");
    const box = document.getElementById("exit-ai-result");

    if (!input.files || !input.files[0]) {
      App.ui.toast("Vui lòng chọn ảnh trước.", "danger");
      return;
    }

    const formData = new FormData();
    formData.append("image", input.files[0]);

    btn.disabled = true;
    box.innerHTML = App.ui.spinner("AI đang nhận diện…");

    try {
      const res = await App.api.upload("/api/parking/ai-exit", formData);
      const d = res.parking?.data || {};
      box.innerHTML = this._receipt(d);
      input.value = "";
    } catch (err) {
      box.innerHTML = `<div class="alert alert-danger">${App.ui.escape(err.message)}</div>`;
    } finally {
      btn.disabled = false;
    }
  },
};
