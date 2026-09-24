import os

from flask import Flask, send_from_directory

from routes.loai_xe import loai_xe_bp
from routes.vi_tri_do import vi_tri_bp
from routes.luot_gui_xe import luot_gui_bp
from routes.ve_thang import ve_thang_bp
from routes.parking import parking_bp
from routes.tai_khoan import tai_khoan_bp
from routes.khu_vuc import khu_vuc_bp
from routes.thong_ke import thong_ke_bp
from routes.he_thong_ai import he_thong_ai_bp


app = Flask(__name__)

app.json.ensure_ascii = False

app.register_blueprint(loai_xe_bp)
app.register_blueprint(vi_tri_bp)
app.register_blueprint(luot_gui_bp)
app.register_blueprint(ve_thang_bp)
app.register_blueprint(parking_bp)
app.register_blueprint(tai_khoan_bp)
app.register_blueprint(khu_vuc_bp)
app.register_blueprint(thong_ke_bp)
app.register_blueprint(he_thong_ai_bp)


FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "frontend"
)


@app.route("/")
def index():
    """Serve giao diện chính (SPA)."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_frontend(filename):
    """Serve các file tĩnh của frontend (css/js/assets)."""
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )