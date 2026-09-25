// ============================================================
// camera.js — quét biển số bằng camera trực tiếp + ảnh mẫu
//
// Dùng chung cho views/entry.js và views/exit.js:
//
//   App.camera.html("entry")
//   App.camera.mount("entry", { onAnh: (blob, ten) => {...} })
//
// Ảnh lấy từ camera hay từ bộ ảnh mẫu đều được đưa về cùng một
// hàm onAnh(blob, ten), nên view chỉ cần gửi blob đó lên đúng
// endpoint AI đang có (/api/parking/ai-entry hoặc ai-exit).
// ============================================================

App.camera = {
  MANIFEST: "img/mau/manifest.json",
  THU_MUC_MAU: "img/mau/",

  _mau: null,
  _stream: null,

  // ----------------------------------------------------------
  // Camera chỉ mở được khi trang chạy trên https hoặc localhost.
  // Trả về lý do nếu không dùng được, null nếu dùng được.
  // ----------------------------------------------------------
  lyDoKhongDungDuoc() {
    if (!window.isSecureContext) {
      return "Trình duyệt chỉ cho phép mở camera khi trang chạy trên https hoặc localhost. Hãy mở ứng dụng bằng http://127.0.0.1:5000, hoặc dùng ảnh mẫu bên dưới.";
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return "Trình duyệt này không hỗ trợ mở camera trực tiếp. Hãy dùng ảnh mẫu bên dưới.";
    }
    return null;
  },

  // ----------------------------------------------------------
  // HTML của khối camera + ảnh mẫu.
  // ----------------------------------------------------------
  html(id) {
    const U = App.ui;
    const loi = this.lyDoKhongDungDuoc();

    return `
      <div class="xp-cam-stage" id="${id}-stage">
        <video id="${id}-video" playsinline autoplay muted></video>
        <img id="${id}-xem" alt="Ảnh vừa chọn" hidden>
        <div class="xp-cam-off" id="${id}-cho">
          ${U.icon("camera-off", 30)}
          <div>Camera chưa bật</div>
        </div>
        <div class="xp-cam-frame" id="${id}-khung" hidden>
          <i></i><i></i><i></i><i></i>
        </div>
      </div>

      <div class="xp-cam-bar">
        <button type="button" class="xp-btn xp-btn-primary xp-btn-sm" id="${id}-mo" ${loi ? "disabled" : ""}>
          ${U.icon("camera", 15)}Bật camera
        </button>
        <button type="button" class="xp-btn xp-btn-soft xp-btn-sm" id="${id}-chup" disabled>
          ${U.icon("sparkles", 15)}Chụp &amp; nhận diện
        </button>
        <button type="button" class="xp-btn xp-btn-outline xp-btn-sm" id="${id}-tat" disabled>
          ${U.icon("x", 15)}Tắt
        </button>
      </div>

      ${loi ? U.alert(loi, "warn") : ""}

      <div class="xp-divider xp-mt"></div>

      <div class="xp-row" style="justify-content:space-between">
        <span class="xp-bold xp-small">Hoặc chọn ảnh mẫu</span>
        <span class="xp-small xp-muted" id="${id}-mau-tt"></span>
      </div>
      <div class="xp-cam-mau" id="${id}-mau"></div>`;
  },

  // ----------------------------------------------------------
  // Gắn sự kiện. onAnh(blob, ten) được gọi mỗi khi có ảnh.
  // ----------------------------------------------------------
  async mount(id, { onAnh } = {}) {
    const $ = (h) => document.getElementById(`${id}-${h}`);

    const video = $("video");
    const xem = $("xem");
    const cho = $("cho");
    const khung = $("khung");

    // Ảnh đang xem thay cho khung hình trực tiếp; khung ngắm chỉ
    // có nghĩa khi camera đang chạy.
    const hienAnh = (nguon) => {
      xem.src = nguon;
      xem.hidden = false;
      cho.hidden = true;
      khung.hidden = true;
      video.style.visibility = "hidden";
    };

    // --- Bật camera -----------------------------------------
    $("mo").addEventListener("click", async () => {
      try {
        this._stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: "environment" },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        });

        video.srcObject = this._stream;
        video.style.visibility = "visible";
        await video.play();

        xem.hidden = true;
        cho.hidden = true;
        khung.hidden = false;
        $("chup").disabled = false;
        $("tat").disabled = false;
        $("mo").disabled = true;
      } catch (err) {
        const ten = err && err.name;
        let msg = "Không mở được camera.";
        if (ten === "NotAllowedError") {
          msg = "Bạn đã từ chối quyền dùng camera. Hãy bật lại quyền trong cài đặt trình duyệt rồi thử lại.";
        } else if (ten === "NotFoundError") {
          msg = "Không tìm thấy camera nào trên thiết bị này.";
        } else if (ten === "NotReadableError") {
          msg = "Camera đang bị ứng dụng khác chiếm dụng.";
        }
        App.ui.toast(msg, "danger");
      }
    });

    // --- Tắt camera -----------------------------------------
    $("tat").addEventListener("click", () => {
      this.tat();
      video.style.visibility = "hidden";
      cho.hidden = false;
      khung.hidden = true;
      $("chup").disabled = true;
      $("tat").disabled = true;
      $("mo").disabled = false;
    });

    // --- Chụp một khung hình --------------------------------
    $("chup").addEventListener("click", async () => {
      if (!video.videoWidth) {
        App.ui.toast("Camera chưa sẵn sàng.", "danger");
        return;
      }

      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise((res) => canvas.toBlob(res, "image/jpeg", 0.92));

      if (!blob) {
        App.ui.toast("Không chụp được ảnh.", "danger");
        return;
      }

      hienAnh(URL.createObjectURL(blob));
      onAnh(blob, "camera.jpg");
    });

    // --- Ảnh mẫu --------------------------------------------
    const ds = await this.loadManifest();
    const hop = $("mau");
    const tt = $("mau-tt");

    if (!ds.length) {
      tt.textContent = "";
      hop.innerHTML = `<div class="xp-small xp-muted">Chưa có ảnh mẫu.</div>`;
      return;
    }

    tt.textContent = `${ds.length} ảnh`;
    hop.innerHTML = ds
      .map((m, i) => {
        const url = this.THU_MUC_MAU + encodeURIComponent(m.file);
        return `
          <button type="button" class="xp-cam-mau-item" data-i="${i}"
                  title="${App.ui.escape(m.loaixe || m.file)}">
            <img src="${url}" alt="${App.ui.escape(m.file)}" loading="lazy">
          </button>`;
      })
      .join("");

    hop.addEventListener("click", async (e) => {
      const nut = e.target.closest(".xp-cam-mau-item");
      if (!nut) return;

      const m = ds[Number(nut.dataset.i)];
      const url = this.THU_MUC_MAU + encodeURIComponent(m.file);

      try {
        const r = await fetch(url);
        if (!r.ok) throw new Error(String(r.status));
        const blob = await r.blob();
        hienAnh(url);
        onAnh(blob, m.file);
      } catch (err) {
        App.ui.toast("Không tải được ảnh mẫu.", "danger");
      }
    });
  },

  // ----------------------------------------------------------
  // Tắt camera và giải phóng thiết bị.
  // Router gọi hàm này mỗi lần chuyển màn hình, nếu không đèn
  // camera sẽ vẫn sáng sau khi rời trang.
  // ----------------------------------------------------------
  tat() {
    if (this._stream) {
      this._stream.getTracks().forEach((t) => t.stop());
      this._stream = null;
    }
  },

  async loadManifest() {
    if (this._mau) return this._mau;

    try {
      const res = await fetch(this.MANIFEST, { cache: "no-store" });
      const data = await res.json();
      this._mau = Array.isArray(data.mau) ? data.mau : [];
    } catch (err) {
      this._mau = [];
    }

    return this._mau;
  },
};
