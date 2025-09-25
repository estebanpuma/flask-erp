from flask import Blueprint, render_template

quality_bp = Blueprint(
    "quality", __name__, url_prefix="/quality", template_folder="../templates"
)


@quality_bp.route("/")
def index():
    return render_template("quality/index.html")
