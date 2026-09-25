// ============================================================
// charts.js — bọc Chart.js cho khớp giao diện
// ------------------------------------------------------------
// Chart.js được nhúng sẵn ở frontend/vendor, không nạp từ CDN.
//
// Ở đây chủ yếu là đặt mặc định chung (chữ, lưới, chú giải) theo
// token của xp.css, để biểu đồ không lệch tông với phần còn lại.
// ============================================================

App.charts = (function () {
  // Bảng màu lấy đúng token trong css/xp.css.
  const MAU = {
    accent: "#15507a",
    accentNhat: "rgba(21, 80, 122, 0.72)",
    ok: "#067647",
    warn: "#b54708",
    err: "#b42318",
    info: "#175cd3",
    tim: "#6941c6",
    xam: "#98a2b3",
    chu: "#667085",
    luoi: "#f2f4f7",
    vien: "#e4e7ec",
  };

  const instances = {};

  // Áp mặc định một lần cho toàn bộ biểu đồ.
  let daDat = false;
  function datMacDinh() {
    if (daDat || typeof Chart === "undefined") return;
    daDat = true;

    Chart.defaults.font.family =
      '"Be Vietnam Pro", "Segoe UI", system-ui, -apple-system, sans-serif';
    Chart.defaults.font.size = 12;
    Chart.defaults.color = MAU.chu;
    Chart.defaults.borderColor = MAU.luoi;
    Chart.defaults.plugins.legend.labels.boxWidth = 10;
    Chart.defaults.plugins.legend.labels.boxHeight = 10;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 14;
    Chart.defaults.plugins.tooltip.backgroundColor = "#101828";
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
    Chart.defaults.plugins.tooltip.titleFont = { weight: "600", size: 12 };
    Chart.defaults.plugins.tooltip.displayColors = false;
    // Không cần hiệu ứng vẽ lại khi mở màn, chỉ làm chậm.
    Chart.defaults.animation.duration = 420;
  }

  // Trục tung chỉ toàn số lượt xe: bỏ lưới dọc, giữ lưới ngang.
  function trucY(nhan) {
    return {
      beginAtZero: true,
      border: { display: false },
      grid: { color: MAU.luoi, drawTicks: false },
      ticks: { padding: 8, precision: 0 },
      title: nhan ? { display: true, text: nhan, color: MAU.xam, font: { size: 11 } } : undefined,
    };
  }

  function trucX() {
    return {
      border: { display: false },
      grid: { display: false },
      ticks: { padding: 6 },
    };
  }

  return {
    MAU,

    destroy(key) {
      if (key) {
        if (instances[key]) {
          instances[key].destroy();
          delete instances[key];
        }
        return;
      }
      Object.keys(instances).forEach((k) => {
        instances[k].destroy();
        delete instances[k];
      });
    },

    _mount(canvasId, config, key) {
      datMacDinh();
      this.destroy(key);

      const canvas = document.getElementById(canvasId);
      if (!canvas) return null;

      instances[key] = new Chart(canvas, config);
      return instances[key];
    },

    line(canvasId, labels, datasets, key) {
      return this._mount(
        canvasId,
        {
          type: "line",
          data: { labels, datasets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: { legend: { display: datasets.length > 1, position: "bottom" } },
            scales: { x: trucX(), y: trucY() },
          },
        },
        key || canvasId
      );
    },

    bar(canvasId, labels, datasets, key) {
      return this._mount(
        canvasId,
        {
          type: "bar",
          data: { labels, datasets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: datasets.length > 1, position: "bottom" } },
            scales: { x: trucX(), y: trucY() },
          },
        },
        key || canvasId
      );
    },

    // Vòng tròn tỉ lệ. `labels` và `data` phải cùng độ dài.
    doughnut(canvasId, labels, data, key) {
      const mau = [MAU.ok, MAU.warn, MAU.accent, MAU.info, MAU.tim, MAU.xam];
      return this._mount(
        canvasId,
        {
          type: "doughnut",
          data: {
            labels,
            datasets: [
              {
                data,
                backgroundColor: mau.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 4,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
              legend: { display: true, position: "bottom" },
              tooltip: {
                callbacks: {
                  label(ctx) {
                    const tong = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                    const phan = Math.round((ctx.parsed / tong) * 100);
                    return ` ${ctx.label}: ${ctx.parsed} (${phan}%)`;
                  },
                },
              },
            },
          },
        },
        key || canvasId
      );
    },
  };
})();
