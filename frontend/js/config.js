// ============================================================
// config.js — cấu hình chung của frontend
// ============================================================

const App = window.App || {};
App.views = App.views || {};

App.config = {
  // Cùng origin với Flask nên dùng đường dẫn tương đối.
  API_BASE: "",
  STORAGE_KEY: "xeparking_session",
  DEFAULT_ROUTE: "dashboard",

  // Nhãn hiển thị của từng vai trò.
  ROLES: {
    QUAN_TRI_VIEN: "Quản trị viên",
    NHAN_VIEN_BAI_XE: "Nhân viên bãi xe",
    NGUOI_QUAN_LY: "Người quản lý",
  },

  // Ánh xạ vai trò -> danh sách route được phép truy cập.
  // (route = hash không có dấu "#", khớp với MENU bên dưới)
  PERMISSIONS: {
    QUAN_TRI_VIEN: [
      "dashboard", "taikhoan", "khuvuc", "loaixe", "vitrido",
      "entry", "exit", "vethang", "lichsu", "chotrong",
      "thongke", "ai"
    ],
    NHAN_VIEN_BAI_XE: [
      "dashboard", "vitrido", "entry", "exit", "vethang", "lichsu", "chotrong"
    ],
    NGUOI_QUAN_LY: [
      "dashboard", "lichsu", "chotrong", "thongke", "ai"
    ],
  },

  // Danh sách mục menu (hiển thị theo thứ tự này).
  MENU: [
    { route: "dashboard", label: "Dashboard",        icon: "bi-speedometer2" },
    { route: "entry",     label: "Ghi nhận xe vào",  icon: "bi-box-arrow-in-right" },
    { route: "exit",      label: "Ghi nhận xe ra",   icon: "bi-box-arrow-right" },
    { route: "chotrong",  label: "Theo dõi chỗ trống", icon: "bi-grid-3x3-gap" },
    { route: "lichsu",    label: "Tra cứu lịch sử",  icon: "bi-clock-history" },
    { route: "vethang",   label: "Quản lý vé tháng", icon: "bi-calendar-check" },
    { route: "taikhoan",  label: "Quản lý tài khoản", icon: "bi-people" },
    { route: "khuvuc",    label: "Quản lý khu vực",  icon: "bi-map" },
    { route: "vitrido",   label: "Quản lý vị trí đỗ", icon: "bi-p-square" },
    { route: "loaixe",    label: "Quản lý loại xe",  icon: "bi-car-front" },
    { route: "thongke",   label: "Thống kê",         icon: "bi-bar-chart-line" },
    { route: "ai",        label: "AI hỗ trợ",        icon: "bi-stars" },
  ],

  // Các giá trị trạng thái hay dùng.
  TRANG_THAI_VI_TRI: ["Còn trống", "Đang sử dụng"],
  TINH_TRANG_LUOT_GUI: ["Đang gửi", "Đã trả"],
  LOAI_VE: ["VE_LUOT", "VE_THANG"],
};
