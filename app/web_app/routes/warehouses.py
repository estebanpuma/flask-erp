from flask import Blueprint, render_template

warehouses_bp = Blueprint(
    "warehouses_bp", __name__, url_prefix="/warehouses", template_folder="../templates"
)


@warehouses_bp.route("/")
def warehouses_list():
    return render_template("warehouses/warehouses_list.html")


@warehouses_bp.route("/<int:id>")
def warehouses_detail(id):
    return render_template("warehouses/warehouses_detail.html", warehouse_id=id)


@warehouses_bp.route("/create", methods=["GET"])
def create_warehouses_view():
    return render_template("warehouses/warehouses_create.html")


@warehouses_bp.route("/<int:id>/edit")
def edit_warehouses(id):
    return render_template("warehouses/warehouses_edit.html", warehouse_id=id)
