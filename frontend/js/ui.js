// ============================================================
// ui.js — các tiện ích hiển thị dùng chung
// ============================================================

App.ui = {
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

  // Toast thông báo (dùng Bootstrap Toast).
  toast(message, type) {
    const kind = type === "danger" ? "danger" : "success";
    const el = this.el(`
      <div class="toast align-items-center text-bg-${kind} border-0" role="alert">
        <div class="d-flex">
          <div class="toast-body">${this.escape(message)}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    `);
    document.getElementById("toast-root").appendChild(el);
    const t = new bootstrap.Toast(el, { delay: 3500 });
    t.show();
    el.addEventListener("hidden.bs.toast", () => el.remove());
  },

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

  // Badge màu bất kỳ.
  badge(text, color) {
    return `<span class="badge text-bg-${color}">${this.escape(text)}</span>`;
  },

  // Badge cho vai trò.
  roleBadge(vaitro) {
    const map = {
      QUAN_TRI_VIEN: "primary",
      NHAN_VIEN_BAI_XE: "info",
      NGUOI_QUAN_LY: "warning",
    };
    const color = map[vaitro] || "secondary";
    return this.badge(this.roleLabel(vaitro), color);
  },

  roleLabel(vaitro) {
    return (App.config.ROLES && App.config.ROLES[vaitro]) || vaitro;
  },

  // Badge trạng thái vị trí / lượt gửi.
  statusBadge(value) {
    const map = {
      "Còn trống": "success",
      "Đang sử dụng": "danger",
      "Đang gửi": "warning",
      "Đã trả": "success",
    };
    return this.badge(value, map[value] || "secondary");
  },

  // Badge boolean (vé tháng hiệu lực / khóa).
  boolBadge(value) {
    return value ? this.badge("Hiệu lực", "success") : this.badge("Hết hạn", "secondary");
  },

  // Spinner chờ dữ liệu.
  spinner(text) {
    return `
      <div class="text-center text-muted py-5">
        <div class="spinner-border" role="status"></div>
        <div class="mt-2">${this.escape(text || "Đang tải…")}</div>
      </div>`;
  },

  // Bảng dữ liệu chung.
  // headers: [{label, key, render?}]
  table(headers, rows) {
    if (!rows || rows.length === 0) {
      return `<div class="alert alert-light text-center text-muted">Chưa có dữ liệu.</div>`;
    }
    const thead = headers.map((h) => `<th>${this.escape(h.label)}</th>`).join("");
    const tbody = rows.map((row) => {
      const cells = headers.map((h) => {
        if (h.render) return `<td>${h.render(row[h.key], row)}</td>`;
        const val = row[h.key] === null || row[h.key] === undefined ? "" : String(row[h.key]);
        return `<td>${this.escape(val)}</td>`;
      }).join("");
      return `<tr>${cells}</tr>`;
    }).join("");
    return `
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light"><tr>${thead}</tr></thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>`;
  },

  // Cột nút Sửa/Xóa cho các màn CRUD.
  actionButtons(id) {
    return `
      <div class="d-flex gap-1">
        <button class="btn btn-sm btn-outline-primary" data-action="edit" data-id="${id}">
          <i class="bi bi-pencil"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${id}">
          <i class="bi bi-trash"></i>
        </button>
      </div>`;
  },

  // Modal Bootstrap dùng chung.
  modal({ title, body, footer }) {
    const el = this.el(`
      <div class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">${this.escape(title)}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">${body || ""}</div>
            <div class="modal-footer">${footer || ""}</div>
          </div>
        </div>
      </div>
    `);
    document.getElementById("modal-root").appendChild(el);
    const modal = new bootstrap.Modal(el);
    return {
      el,
      show() { modal.show(); },
      hide() { modal.hide(); },
      remove() { el.remove(); },
      find(sel) { return el.querySelector(sel); },
    };
  },

  // Nút "Lưu / Hủy" chuẩn cho form trong modal.
  formButtons() {
    return `
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
      <button type="button" class="btn btn-primary" data-action="save">Lưu</button>`;
  },

  // Nút "Thêm mới" ở đầu mỗi màn CRUD.
  addButton(label) {
    return `
      <button class="btn btn-primary" data-action="add">
        <i class="bi bi-plus-lg me-1"></i>${this.escape(label)}
      </button>`;
  },
};
