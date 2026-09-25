// ============================================================
// md.js — chuyển văn bản Markdown đơn giản thành HTML
// ------------------------------------------------------------
// Câu trả lời của AI (Gemini, hoặc lớp phân tích nội bộ khi hết hạn
// mức) là văn bản có định dạng. Nếu hiện thẳng ra thì người dùng đọc
// thấy cả dấu ### và ** — đúng như một tệp văn bản thô, không phải
// một câu trả lời. Bộ chuyển đổi này biến nó thành tiêu đề, danh
// sách, chữ đậm... để đọc được như một văn bản hoàn chỉnh.
//
// Cố ý KHÔNG nạp thư viện Markdown từ Internet: cả ứng dụng phải chạy
// được khi mất mạng. Ở đây chỉ làm đúng những gì văn bản của AI dùng
// tới:
//
//   # ## ###      tiêu đề          **đậm**     *nghiêng*     `mã`
//   - * +         danh sách        1. 2.       danh sách số
//   | ô | ô |     bảng             ---         đường kẻ ngang
//
// AN TOÀN: văn bản được thoát ký tự HTML TRƯỚC khi phân tích, nên nội
// dung do AI sinh ra không thể chèn thẻ vào trang. Không được đảo thứ
// tự đó, và không được nối thêm chuỗi chưa thoát vào kết quả.
// ============================================================

App.md = {
  // Định dạng trong phạm vi một dòng. Nhận chuỗi ĐÃ được thoát HTML.
  //
  // Thứ tự có ý nghĩa: `mã` trước để dấu * bên trong không bị hiểu là
  // nghiêng, rồi **đậm** trước *nghiêng* để cặp ** không bị ăn thành
  // hai lần nghiêng.
  _trongDong(s) {
    return String(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      // (^|[^*]) để không khớp vào phần còn lại của một cặp ** nào đó;
      // [^*\s] để "* " của dấu đầu dòng không bị coi là mở nghiêng.
      .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>");
  },

  _oBang(dong) {
    return dong
      .trim()
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((o) => o.trim());
  },

  // Chuyển văn bản Markdown thành HTML. Trả về một <div class="xp-md">.
  render(text) {
    let nguon = String(text === null || text === undefined ? "" : text).trim();

    // Đôi khi AI bọc cả câu trả lời trong khối ``` — bỏ lớp vỏ đó đi,
    // không thì nó hiện ra thành một đoạn văn đầy dấu backtick.
    const boc = nguon.match(/^```[a-zA-Z]*\n([\s\S]*?)\n?```$/);
    if (boc) nguon = boc[1];

    nguon = App.ui.escape(nguon).replace(/\r\n?/g, "\n");

    const ra = []; // các khối HTML đã đóng
    let doan = []; // dòng đang gom thành đoạn văn
    let bang = []; // dòng đang gom thành bảng
    const ds = []; // ngăn xếp danh sách đang mở: {loai, thut, muc}

    const chotDoan = () => {
      if (!doan.length) return;
      ra.push(`<p>${this._trongDong(doan.join(" "))}</p>`);
      doan = [];
    };

    const chotBang = () => {
      if (!bang.length) return;
      const hang = bang.map((d) => this._oBang(d));
      bang = [];

      // Hàng thứ hai là dòng kẻ |---|---| thì bỏ, đó không phải dữ liệu.
      const coKe = hang.length > 1 && hang[1].every((o) => /^:?-{2,}:?$/.test(o));
      const dau = coKe ? hang[0] : null;
      const than = coKe ? hang.slice(2) : hang;

      ra.push(`
        <div class="xp-md-bang">
          <table>
            ${
              dau
                ? `<thead><tr>${dau
                    .map((o) => `<th>${this._trongDong(o)}</th>`)
                    .join("")}</tr></thead>`
                : ""
            }
            <tbody>${than
              .map(
                (r) =>
                  `<tr>${r.map((o) => `<td>${this._trongDong(o)}</td>`).join("")}</tr>`
              )
              .join("")}</tbody>
          </table>
        </div>`);
    };

    // Đóng danh sách cho tới khi ngăn xếp chỉ còn `giuLai` mức. Danh
    // sách bị đóng sẽ lồng vào mục cuối cùng của danh sách cha.
    const chotDs = (giuLai) => {
      while (ds.length > giuLai) {
        const d = ds.pop();
        const khoi = `<${d.loai}>${d.muc
          .map((m) => `<li>${m}</li>`)
          .join("")}</${d.loai}>`;

        if (ds.length) {
          const cha = ds[ds.length - 1];
          cha.muc[cha.muc.length - 1] += khoi;
        } else {
          ra.push(khoi);
        }
      }
    };

    for (const d of nguon.split("\n")) {
      // Dòng trống chỉ chốt đoạn văn. Danh sách và bảng để mở, vì AI
      // hay chèn dòng trống giữa các mục.
      if (!d.trim()) {
        chotDoan();
        chotBang();
        continue;
      }

      if (/^\s*\|.*\|\s*$/.test(d)) {
        chotDoan();
        chotDs(0);
        bang.push(d);
        continue;
      }
      chotBang();

      const tieuDe = d.match(/^\s*(#{1,6})\s+(.*?)\s*#*\s*$/);
      if (tieuDe) {
        chotDoan();
        chotDs(0);
        const cap = tieuDe[1].length;
        ra.push(`<h${cap}>${this._trongDong(tieuDe[2])}</h${cap}>`);
        continue;
      }

      // Đường kẻ ngang. Phải đứng trước danh sách, không thì "- - -"
      // bị hiểu là một mục có nội dung "- -".
      if (/^\s*([-*_])\s*(\1\s*){2,}$/.test(d)) {
        chotDoan();
        chotDs(0);
        ra.push("<hr>");
        continue;
      }

      const mUl = d.match(/^(\s*)[-*+]\s+(.*)$/);
      const mOl = d.match(/^(\s*)\d+[.)]\s+(.*)$/);
      const muc = mUl || mOl;
      if (muc) {
        chotDoan();
        const loai = mUl ? "ul" : "ol";
        const thut = (muc[1] || "").replace(/\t/g, "    ").length;

        // Thụt lề ít hơn mức đang mở thì đóng bớt cho tới khi khớp.
        while (ds.length && thut < ds[ds.length - 1].thut) chotDs(ds.length - 1);

        // Cùng mức thụt mà khác kiểu — danh sách số nối tiếp danh sách
        // chấm — thì phải đóng lại rồi mở danh sách mới. Không kiểm tra
        // chỗ này thì các mục "1." bị hiện thành dấu chấm.
        const dinh = ds[ds.length - 1];
        if (dinh && dinh.thut === thut && dinh.loai !== loai) chotDs(ds.length - 1);

        const mo = ds[ds.length - 1];
        if (!mo || thut > mo.thut || mo.loai !== loai) {
          ds.push({ loai, thut, muc: [] });
        }
        ds[ds.length - 1].muc.push(this._trongDong(muc[2]));
        continue;
      }

      // Dòng thụt lề nằm trong một mục: viết tiếp nội dung cho mục đó.
      if (ds.length && /^\s+\S/.test(d)) {
        const dangMo = ds[ds.length - 1];
        dangMo.muc[dangMo.muc.length - 1] += " " + this._trongDong(d.trim());
        continue;
      }

      chotDs(0);
      doan.push(d.trim());
    }

    chotDoan();
    chotBang();
    chotDs(0);

    return `<div class="xp-md">${ra.join("")}</div>`;
  },
};
