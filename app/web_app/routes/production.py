from flask import Blueprint, render_template

production_bp = Blueprint(
    "production", __name__, url_prefix="/production", template_folder="../templates"
)


@production_bp.route("/")
def index():
    return render_template("production/index.html")


@production_bp.route("/resources/create")
def production_resources_create():
    return render_template("production/resources/create.html")


@production_bp.route("/resources")
def production_resources_list():
    return render_template("production/resources/list.html")


@production_bp.route("/resources/<int:id>")
def production_resources_detail(id):
    return render_template("production/resources/detail.html", id=id)


@production_bp.route("/resources/<int:id>/edit")
def production_resources_edit(id):
    return render_template("production/resources/edit.html", id=id)


@production_bp.route("/operations")
def operations_list():
    return render_template("operations/list.html")


@production_bp.route("/operations/<int:id>")
def operations_detail(id):
    return render_template("operations/detail.html", id=id)


@production_bp.route("/operations/create")
def operations_create():
    return render_template("operations/create.html")


# ----------------------------WorkStations----------------------------------------
@production_bp.route("/work_stations/create")
def production_work_stations_create():
    return render_template("production/work_stations/create.html")


@production_bp.route("/work_stations")
def production_work_stations_list():
    return render_template("production/work_stations/list.html")


@production_bp.route("/work_stations/<int:id>")
def production_work_stations_detail(id):
    return render_template("production/work_stations/detail.html", id=id)


@production_bp.route("/work_stations/<int:id>/edit")
def production_work_stations_edit(id):
    return render_template("production/work_stations/edit.html", id=id)


# ------------------Capacidad instalada/Capacity-----------------------------------------
@production_bp.route("/capacity")
def capacity_index():
    return render_template("production/capacity/index.html")


@production_bp.route("/operations-sheet/create", methods=["GET", "POST"])
def operation_sheet_create():
    return render_template("operations/operations_sheet_create.html")


@production_bp.route("/operations-sheet/<int:id>")
def operation_sheet_detail():
    return render_template("operations/operations_sheet_detail.html")


@production_bp.route("/operations-sheet")
def operation_sheet_list():
    return render_template("operations/operations_sheet_list.html")


@production_bp.route("/routing")
def routing():
    return render_template("operations/routing.html")


@production_bp.route("/setup")
def setup():
    return render_template("production/setup_wizard.html")


# --------------------------LASTS--------------------------------


@production_bp.route("/resources/lasts")
def lasts():
    return render_template("production/resources/lasts/list.html")


@production_bp.route("/resources/lasts/<int:id>")
def lasts_detail(id):
    return render_template("production/resources/lasts/detail.html", id=id)


@production_bp.route("/resources/lasts/<int:id>/<field>/edit")
def lasts_edit(id, field):
    return render_template("production/resources/lasts/edit.html", id=id, field=field)
