// ============================================================
// charts.js — helper vẽ biểu đồ bằng Chart.js
// ============================================================

App.charts = {
  // Biểu đồ được tạo sẽ lưu lại để huỷ trước khi vẽ lại.
  _instances: {},

  // Huỷ một biểu đồ đã tạo (hoặc tất cả).
  destroy(key) {
    if (key) {
      if (this._instances[key]) {
        this._instances[key].destroy();
        delete this._instances[key];
      }
      return;
    }
    Object.values(this._instances).forEach((c) => c.destroy());
    this._instances = {};
  },

  _base(options) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#6c757d" } },
      },
      ...options,
    };
  },

  line(canvasId, labels, datasets, key) {
    this.destroy(key);
    const el = document.getElementById(canvasId);
    if (!el) return;
    this._instances[key || canvasId] = new Chart(el, {
      type: "line",
      data: { labels, datasets },
      options: this._base({
        scales: {
          x: { ticks: { color: "#6c757d" }, grid: { color: "rgba(0,0,0,0.05)" } },
          y: { beginAtZero: true, ticks: { color: "#6c757d" }, grid: { color: "rgba(0,0,0,0.05)" } },
        },
      }),
    });
  },

  bar(canvasId, labels, datasets, key) {
    this.destroy(key);
    const el = document.getElementById(canvasId);
    if (!el) return;
    this._instances[key || canvasId] = new Chart(el, {
      type: "bar",
      data: { labels, datasets },
      options: this._base({
        scales: {
          x: { ticks: { color: "#6c757d" }, grid: { color: "rgba(0,0,0,0.05)" } },
          y: { beginAtZero: true, ticks: { color: "#6c757d" }, grid: { color: "rgba(0,0,0,0.05)" } },
        },
      }),
    });
  },

  doughnut(canvasId, labels, data, key) {
    this.destroy(key);
    const el = document.getElementById(canvasId);
    if (!el) return;
    this._instances[key || canvasId] = new Chart(el, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: ["#198754", "#dc3545", "#ffc107", "#0d6efd", "#6f42c1"],
          borderWidth: 0,
        }],
      },
      options: this._base({ cutout: "62%" }),
    });
  },
};
