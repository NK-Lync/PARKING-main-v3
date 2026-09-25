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

  // Thứ tự các nhóm trên sidebar. Mục nào không được phép thì
  // cả nhóm đó biến mất, nên không bao giờ có tiêu đề trống.
  NHOM: ["Vận hành", "Nghiệp vụ", "Danh mục", "Trợ lý"],

  // Danh sách mục menu (hiển thị theo thứ tự này).
  // `icon` là tên icon trong App.icons.
  MENU: [
    { route: "dashboard", label: "Dashboard",           icon: "grid",     nhom: "Vận hành" },
    { route: "entry",     label: "Ghi nhận xe vào",     icon: "log-in",   nhom: "Vận hành" },
    { route: "exit",      label: "Ghi nhận xe ra",      icon: "log-out",  nhom: "Vận hành" },
    { route: "chotrong",  label: "Theo dõi chỗ trống",  icon: "parking",  nhom: "Vận hành" },
    { route: "lichsu",    label: "Tra cứu lịch sử",     icon: "history",  nhom: "Nghiệp vụ" },
    { route: "vethang",   label: "Quản lý vé tháng",    icon: "calendar", nhom: "Nghiệp vụ" },
    { route: "thongke",   label: "Thống kê",            icon: "chart",    nhom: "Nghiệp vụ" },
    { route: "khuvuc",    label: "Quản lý khu vực",     icon: "map",      nhom: "Danh mục" },
    { route: "vitrido",   label: "Quản lý vị trí đỗ",   icon: "pin",      nhom: "Danh mục" },
    { route: "loaixe",    label: "Quản lý loại xe",     icon: "car",      nhom: "Danh mục" },
    { route: "taikhoan",  label: "Quản lý tài khoản",   icon: "users",    nhom: "Danh mục" },
    { route: "ai",        label: "AI hỗ trợ",           icon: "sparkles", nhom: "Trợ lý" },
  ],

  // Các giá trị trạng thái hay dùng.
  TRANG_THAI_VI_TRI: ["Còn trống", "Đang sử dụng"],
  TINH_TRANG_LUOT_GUI: ["Đang gửi", "Đã trả"],
  LOAI_VE: ["VE_LUOT", "VE_THANG"],

  // Nhãn tiếng Việt cho loại vé, dùng khi hiển thị.
  NHAN_LOAI_VE: {
    VE_LUOT: "Vé lượt",
    VE_THANG: "Vé tháng",
  },
};
