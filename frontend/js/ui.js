// ============================================================
// ui.js — các tiện ích hiển thị dùng chung
// ------------------------------------------------------------
// Trước đây file này gọi bootstrap.Modal và bootstrap.Toast. Hai
// thứ đó là chỗ duy nhất trong toàn bộ giao diện phụ thuộc
// Bootstrap JS, nên chúng được viết lại ở đây và Bootstrap được
// gỡ hẳn.
//
// Tên hàm cũ giữ nguyên, chỉ thêm hàm mới:
//
//   Cũ  : el escape toast fmtMoney fmtDateTime badge roleBadge
//         roleLabel statusBadge boolBadge spinner alertLoi
//         table actionButtons modal formButtons addButton
//   Mới : card page field input select stat empty confirm icon
//
// Nhờ vậy phần lớn màn hình không phải sửa gì, còn màn mới thì
// dựng nhanh hơn nhiều.
// ============================================================

App.ui = {
  // ----------------------------------------------------------
  // Nền tảng
  // ----------------------------------------------------------

  // Tạo element đầu tiên từ chuỗi HTML.
  el(html) {
    const tpl = document.createElement("template");
    tpl.innerHTML = html.trim();
    return tpl.content.firstElementChild;
  },

  // Thoát ký tự HTML để chống XSS khi chèn dữ liệu vào bảng.
  escape(s) {
    if (s === null || s === undefined) return "";
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  },

  // Lối tắt lấy icon, đỡ phải gõ App.icons ở mọi nơi.
  icon(name, size) {
    return App.icons.svg(name, size);
  },

  // ----------------------------------------------------------
  // Định dạng
  // ----------------------------------------------------------

  // Format tiền VNĐ.
  fmtMoney(n) {
    const num = Number(n);
    if (!isFinite(num)) return "0 ₫";
    return num.toLocaleString("vi-VN") + " ₫";
  },

  // Format ngày giờ từ chuỗi ISO.
  fmtDateTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return String(iso);
    const p = (x) => String(x).padStart(2, "0");
    return `${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}`;
  },

  // Chỉ ngày, không giờ.
  fmtDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return String(iso);
    const p = (x) => String(x).padStart(2, "0");
    return `${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()}`;
  },

  // ----------------------------------------------------------
  // Nhãn
  // ----------------------------------------------------------

  // Nhãn màu. Nhận cả tên màu Bootstrap cũ để chỗ nào chưa đổi
  // vẫn chạy đúng.
  badge(text, tone) {
    const doi = {
      primary: "info",
      secondary: "neutral",
      success: "ok",
      danger: "err",
      warning: "warn",
      light: "neutral",
      dark: "neutral",
    };
    const t = doi[tone] || tone || "neutral";
    return `<span class="xp-pill ${t}">${this.escape(text)}</span>`;
  },

  // Nhãn không có chấm tròn, dùng cho nhãn phụ.
  chip(text, tone) {
    const t = tone || "neutral";
    return `<span class="xp-pill plain ${t}">${this.escape(text)}</span>`;
  },

  roleBadge(vaitro) {
    const map = {
      QUAN_TRI_VIEN: "info",
      NHAN_VIEN_BAI_XE: "ok",
      NGUOI_QUAN_LY: "warn",
    };
    return this.badge(this.roleLabel(vaitro), map[vaitro] || "neutral");
  },

  roleLabel(vaitro) {
    return (App.config.ROLES && App.config.ROLES[vaitro]) || vaitro;
  },

  // Nhãn trạng thái vị trí / lượt gửi.
  //
  // "Còn trống" và "Đã trả" là trạng thái tốt nên dùng màu xanh;
  // "Đang sử dụng" và "Đang gửi" là đang chiếm chỗ nên dùng màu
  // hổ phách. Cố ý không dùng màu đỏ: đỏ là dành cho lỗi.
  statusBadge(value) {
    const map = {
      "Còn trống": "ok",
      "Đang sử dụng": "warn",
      "Đang gửi": "warn",
      "Đã trả": "ok",
    };
    return this.badge(value, map[value] || "neutral");
  },

  // Nhãn boolean (vé tháng hiệu lực / tài khoản bị khóa).
  boolBadge(value) {
    return value ? this.badge("Hiệu lực", "ok") : this.badge("Hết hạn", "neutral");
  },

  // ----------------------------------------------------------
  // Khối trạng thái
  // ----------------------------------------------------------

  // Khối chờ dữ liệu.
  spinner(text) {
    return `
      <div class="xp-loading">
        <span class="xp-spin"></span>
        <span>${this.escape(text || "Đang tải…")}</span>
      </div>`;
  },

  // Khối rỗng, dùng khi danh sách không có dòng nào.
  empty(text) {
    return `
      <div class="xp-empty">
        ${this.icon("inbox", 28)}
        <div>${this.escape(text || "Chưa có dữ liệu.")}</div>
      </div>`;
  },

  // Khối báo lỗi.
  //
  // Các API AI trả kèm trường `error` là thông báo gốc của exception.
  // Hiện luôn ra đây: chỉ có `message` chung chung thì không biết
  // hỏng ở đâu, phải mở DevTools mới xem được.
  alertLoi(err) {
    const goc = err && err.data && err.data.error;
    return `
      <div class="xp-alert err">
        ${this.icon("warning", 17)}
        <div>
          <div>${this.escape((err && err.message) || "Đã xảy ra lỗi")}</div>
          ${goc ? `<div class="xp-small xp-mt-sm" style="opacity:.8">${this.escape(goc)}</div>` : ""}
        </div>
      </div>`;
  },

  // Khối thông báo chung.
  alert(text, tone, title) {
    const t = tone || "info";
    const ic = { ok: "check-circle", err: "warning", warn: "warning", info: "info" }[t] || "info";
    return `
      <div class="xp-alert ${t}">
        ${this.icon(ic, 17)}
        <div>
          ${title ? `<div class="xp-alert-title">${this.escape(title)}</div>` : ""}
          <div>${this.escape(text)}</div>
        </div>
      </div>`;
  },

  // ----------------------------------------------------------
  // Thẻ và bố cục
  // ----------------------------------------------------------

  // Một thẻ có tiêu đề, vùng nút bên phải và phần thân.
  //
  //   card({ title, note, actions, body, flush })
  //
  // `flush: true` bỏ đệm thân thẻ — dùng cho bảng vì bảng đã có
  // đệm riêng trong từng ô.
  card(o) {
    const c = o || {};
    const head = c.title || c.actions || c.note
      ? `
        <div class="xp-card-head">
          <div>
            ${c.title ? `<div class="xp-card-title">${this.escape(c.title)}</div>` : ""}
            ${c.note ? `<div class="xp-card-note">${this.escape(c.note)}</div>` : ""}
          </div>
          ${c.actions ? `<div class="xp-card-head-right">${c.actions}</div>` : ""}
        </div>`
      : "";
    return `
      <div class="xp-card">
        ${head}
        <div class="xp-card-body${c.flush ? " flush" : ""}">${c.body || ""}</div>
      </div>`;
  },

  // Thẻ số liệu.
  //
  //   stat({ label, value, tone, hint, icon })
  //
  // `tone` quyết định màu vạch bên trái và màu con số:
  //   ok = tốt (còn trống, đã trả) · warn = đang chiếm chỗ
  //   err = quá tải · mặc định là màu nhấn
  stat(o) {
    const s = o || {};
    const tone = s.tone ? ` ${s.tone}` : "";
    return `
      <div class="xp-stat${tone}">
        <div class="xp-stat-top">
          <span class="xp-stat-label">${this.escape(s.label)}</span>
          ${s.icon ? `<span class="xp-stat-icon">${this.icon(s.icon, 16)}</span>` : ""}
        </div>
        <div class="xp-stat-value">${s.value === undefined || s.value === null ? "—" : s.value}</div>
        ${s.hint ? `<div class="xp-stat-hint">${this.escape(s.hint)}</div>` : ""}
      </div>`;
  },

  // ----------------------------------------------------------
  // Biểu mẫu
  // ----------------------------------------------------------

  // Bọc một ô nhập kèm nhãn.
  field(label, control, hint) {
    return `
      <div class="xp-field">
        ${label ? `<label class="xp-label">${this.escape(label)}</label>` : ""}
        ${control}
        ${hint ? `<div class="xp-hint">${this.escape(hint)}</div>` : ""}
      </div>`;
  },

  // Ô nhập text/số/ngày.
  input(o) {
    const i = o || {};
    return `<input
      type="${i.type || "text"}"
      class="xp-input"
      name="${this.escape(i.name || "")}"
      ${i.id ? `id="${this.escape(i.id)}"` : ""}
      ${i.value !== undefined && i.value !== null ? `value="${this.escape(i.value)}"` : ""}
      ${i.placeholder ? `placeholder="${this.escape(i.placeholder)}"` : ""}
      ${i.min !== undefined ? `min="${i.min}"` : ""}
      ${i.max !== undefined ? `max="${i.max}"` : ""}
      ${i.step !== undefined ? `step="${i.step}"` : ""}
      ${i.required ? "required" : ""}
      ${i.autofocus ? "autofocus" : ""}>`;
  },

  // Ô chọn.
  //
  //   select({ name, options, value, placeholder })
  //
  // `options` là mảng chuỗi hoặc mảng {value,label}.
  select(o) {
    const s = o || {};
    const opts = (s.options || [])
      .map((op) => {
        const v = typeof op === "object" ? op.value : op;
        const l = typeof op === "object" ? op.label : op;
        const sel = String(v) === String(s.value) ? " selected" : "";
        return `<option value="${this.escape(v)}"${sel}>${this.escape(l)}</option>`;
      })
      .join("");
    const dau = s.placeholder
      ? `<option value="">${this.escape(s.placeholder)}</option>`
      : "";
    return `<select
      class="xp-select"
      name="${this.escape(s.name || "")}"
      ${s.id ? `id="${this.escape(s.id)}"` : ""}
      ${s.required ? "required" : ""}>${dau}${opts}</select>`;
  },

  // Nút "Lưu / Hủy" chuẩn cho form trong hộp thoại.
  formButtons(luu) {
    return `
      <button type="button" class="xp-btn xp-btn-outline" data-action="cancel">Hủy</button>
      <button type="button" class="xp-btn xp-btn-primary" data-action="save">${this.escape(luu || "Lưu")}</button>`;
  },

  // Nút "Thêm mới" ở đầu mỗi màn CRUD.
  addButton(label) {
    return `
      <button class="xp-btn xp-btn-primary" data-action="add">
        ${this.icon("plus", 16)}${this.escape(label)}
      </button>`;
  },

  // ----------------------------------------------------------
  // Bảng
  // ----------------------------------------------------------

  // Bảng dữ liệu chung.
  //
  //   headers: [{ label, key, render?, act?, strong? }]
  //
  // Cột nào có `act: true` (hoặc nhãn rỗng) được coi là cột thao
  // tác: canh phải, co hết mức, không xuống dòng.
  table(headers, rows, thongBaoRong) {
    if (!rows || rows.length === 0) {
      return this.empty(thongBaoRong);
    }

    const laAct = (h) => h.act === true || h.label === "";

    const thead = headers
      .map((h) => `<th${laAct(h) ? ' class="xp-col-act"' : ""}>${this.escape(h.label || "")}</th>`)
      .join("");

    const tbody = rows
      .map((row) => {
        const cells = headers
          .map((h) => {
            const cls = [laAct(h) ? "xp-col-act" : "", h.strong ? "xp-cell-strong" : ""]
              .filter(Boolean)
              .join(" ");
            const attr = cls ? ` class="${cls}"` : "";
            if (h.render) return `<td${attr}>${h.render(row[h.key], row)}</td>`;
            const val = row[h.key] === null || row[h.key] === undefined ? "" : String(row[h.key]);
            return `<td${attr}>${this.escape(val)}</td>`;
          })
          .join("");
        return `<tr>${cells}</tr>`;
      })
      .join("");

    return `
      <div class="xp-table-wrap">
        <table class="xp-table">
          <thead><tr>${thead}</tr></thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>`;
  },

  // Cột nút Sửa/Xóa cho các màn CRUD.
  actionButtons(id) {
    return `
      <div class="xp-row end" style="flex-wrap:nowrap">
        <button class="xp-btn xp-btn-outline xp-btn-sm xp-btn-icon" data-action="edit" data-id="${this.escape(id)}" title="Sửa">
          ${this.icon("pencil", 14)}
        </button>
        <button class="xp-btn xp-btn-danger xp-btn-sm xp-btn-icon" data-action="delete" data-id="${this.escape(id)}" title="Xóa">
          ${this.icon("trash", 14)}
        </button>
      </div>`;
  },

  // ----------------------------------------------------------
  // Hộp thoại
  // ----------------------------------------------------------

  _z: 90,

  // Hộp thoại dùng chung.
  //
  // Trả về { el, show, hide, remove, find }. Hộp thoại được tạo ra
  // ở trạng thái ẩn; gọi show() mới hiện. Đóng bằng nút X, phím
  // Esc, hoặc bấm ra ngoài.
  modal({ title, body, footer }) {
    const z = ++this._z;
    const el = this.el(`
      <div class="xp-modal-layer" hidden>
        <div class="xp-modal" role="dialog" aria-modal="true" style="z-index:${z}">
          <div class="xp-modal-head">
            <div class="xp-modal-title">${this.escape(title)}</div>
            <button type="button" class="xp-modal-x" data-action="close" aria-label="Đóng">
              ${this.icon("x", 17)}
            </button>
          </div>
          <div class="xp-modal-body">${body || ""}</div>
          ${footer ? `<div class="xp-modal-foot">${footer}</div>` : ""}
        </div>
      </div>
    `);

    const layer = el;
    document.getElementById("modal-root").appendChild(layer);

    const dong = () => {
      layer.hidden = true;
      this._z = Math.max(90, this._z - 1);
      document.removeEventListener("keydown", esc);
      layer.remove();
    };

    const esc = (e) => {
      if (e.key === "Escape") dong();
    };

    // Bấm ra ngoài thì đóng, bấm vào thân hộp thoại thì không.
    layer.addEventListener("mousedown", (e) => {
      if (e.target === layer) dong();
    });
    layer.querySelector('[data-action="close"]').addEventListener("click", dong);

    return {
      el: layer,
      show() {
        layer.hidden = false;
        document.addEventListener("keydown", esc);
        // Đưa con trỏ vào ô nhập đầu tiên cho đỡ phải bấm chuột.
        const dau = layer.querySelector("input, select, textarea");
        if (dau) dau.focus();
      },
      hide: dong,
      remove: dong,
      find(sel) {
        return layer.querySelector(sel);
      },
    };
  },

  // Hộp thoại xác nhận, thay cho window.confirm().
  //
  //   const dongY = await App.ui.confirm({ title, message, okLabel, tone })
  //
  // Trả về Promise<boolean>. Hộp thoại mặc định của trình duyệt
  // hiện tên miền và không đổi được nút, nhìn lệch hẳn với phần
  // còn lại của giao diện.
  confirm({ title, message, okLabel, tone }) {
    return new Promise((xong) => {
      const nguy = tone === "err";
      let daTraLoi = false;

      const m = this.modal({
        title: title || "Xác nhận",
        body: `<div class="xp-small" style="color:var(--xp-muted)">${this.escape(message || "")}</div>`,
        footer: `
          <button type="button" class="xp-btn xp-btn-outline" data-action="khong">Hủy</button>
          <button type="button" class="xp-btn ${nguy ? "xp-btn-danger" : "xp-btn-primary"}" data-action="co">
            ${this.escape(okLabel || "Đồng ý")}
          </button>`,
      });

      const traLoi = (v) => {
        if (daTraLoi) return;
        daTraLoi = true;
        m.hide();
        xong(v);
      };

      m.find('[data-action="khong"]').addEventListener("click", () => traLoi(false));
      m.find('[data-action="co"]').addEventListener("click", () => traLoi(true));
      // Đóng bằng Esc hoặc bấm ra ngoài cũng tính là không đồng ý.
      m.el.addEventListener("mousedown", (e) => {
        if (e.target === m.el) traLoi(false);
      });
      m.el.querySelector('[data-action="close"]').addEventListener("click", () => traLoi(false));

      m.show();
    });
  },

  // ----------------------------------------------------------
  // Thông báo nổi
  // ----------------------------------------------------------

  // Thông báo nổi ở góc dưới phải, tự tắt sau 3,5 giây.
  //
  // `type` nhận "success" | "danger" | "warning" | "info" cho hợp
  // với chỗ gọi cũ.
  toast(message, type) {
    const doi = { success: "ok", danger: "err", warning: "warn", info: "info" };
    const t = doi[type] || type || "ok";

    let root = document.getElementById("toast-root");
    if (!root) {
      root = this.el('<div id="toast-root" class="xp-toasts"></div>');
      document.body.appendChild(root);
    }

    const ic = { ok: "check-circle", err: "warning", warn: "warning", info: "info" }[t] || "info";
    const el = this.el(`
      <div class="xp-toast ${t}" role="status">
        <span class="xp-toast-icon">${this.icon(ic, 17)}</span>
        <span class="xp-toast-msg">${this.escape(message)}</span>
      </div>
    `);

    root.appendChild(el);

    const tat = () => {
      if (el.dataset.dangRa) return;
      el.dataset.dangRa = "1";
      el.classList.add("ra");
      setTimeout(() => el.remove(), 200);
    };

    const hen = setTimeout(tat, 3500);
    el.addEventListener("click", () => {
      clearTimeout(hen);
      tat();
    });
  },
};
