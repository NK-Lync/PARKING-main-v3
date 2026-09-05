from flask import Flask

from routes.loai_xe import loai_xe_bp
from routes.vi_tri_do import vi_tri_bp
from routes.luot_gui_xe import luot_gui_bp
from routes.ve_thang import ve_thang_bp
from routes.parking import parking_bp


app = Flask(__name__)

app.json.ensure_ascii = False

app.register_blueprint(loai_xe_bp)
app.register_blueprint(vi_tri_bp)
app.register_blueprint(luot_gui_bp)
app.register_blueprint(ve_thang_bp)
app.register_blueprint(parking_bp)


@app.route("/")
def home():
    return {
        "success": True,
        "message": "XeParking API đang hoạt động"
    }


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )