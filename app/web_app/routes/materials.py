from flask import Blueprint, render_template

materials_bp = Blueprint(
    "materials", __name__, url_prefix="/materials", template_folder="../templates"
)


@materials_bp.route("/")
def materials_list():
    return render_template("materials/material_list.html")


@materials_bp.route("/<int:id>")
def materials_detail(id):
    return render_template("materials/material_detail.html", id=id)


@materials_bp.route("/create", methods=["GET"])
def create_material_view():
    return render_template("materials/material_create.html")


@materials_bp.route("/<int:id>/edit")
def edit_material(id):
    return render_template("materials/material_edit.html", id=id)


# ***************Lots**********************


@materials_bp.route("/<int:id>/lots")
def materials_lots(id):
    return render_template("materials/material_lots.html", material_id=id)


@materials_bp.route("/lots/<int:id>")
def material_lots_detail(id):
    return render_template("materials/lot_detail.html", lot_id=id)


@materials_bp.route("/lots/create")
def create_lot():
    return render_template("materials/lot_create.html")


@materials_bp.route("/<int:id>/lots/create")
def create_material_lot(id):
    return render_template("materials/lot_create.html", material_id=id)


# ----------------------------Groups--------------------------------------------
# ------------------------------------------------------------------------------
@materials_bp.route("/groups/")
def groups_list():
    return render_template("materials/groups/groups_list.html")


@materials_bp.route("/groups/<int:id>")
def groups_detail(id):
    return render_template("materials/groups/groups_detail.html", id=id)


@materials_bp.route("/groups/create", methods=["GET"])
def create_group_view():
    return render_template("materials/groups/groups_create.html")


# ----------------------------SubGroups--------------------------------------------
# ------------------------------------------------------------------------------
@materials_bp.route("/subgroups/")
def subgroups_list():
    return render_template("materials/subgroups/subgroups_list.html")


@materials_bp.route("/subgroups/<int:id>")
def subgroups_detail(id):
    return render_template("materials/subgroups/subgroups_detail.html", id=id)


@materials_bp.route("/subgroups/create", methods=["GET"])
def subcreate_group_view():
    return render_template("materials/subgroups/subgroups_create.html")
