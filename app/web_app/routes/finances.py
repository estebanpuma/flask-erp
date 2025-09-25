from flask import Blueprint, render_template

finances_bp = Blueprint(
    "finances", __name__, url_prefix="/finances", template_folder="../templates"
)


@finances_bp.route("/")
def index():
    return render_template("finances/index.html")
