from flask import Blueprint

users_bp = Blueprint(
    "users", __name__, url_prefix="/users", template_folder="../templates"
)


@users_bp.route("/")
def users_list():
    return "hola"


@users_bp.route("/<int:id>")
def users_details(id):
    return "hola"


@users_bp.route("/create")
def users_create():
    return "hola"


@users_bp.route("/<int:id>/edit")
def users_edit(id):
    return "hola"


@users_bp.route("/roles")
def roles_list():
    return "hola"


@users_bp.route("/roles/<int:id>")
def roles_details(id):
    return "hola"


@users_bp.route("/roles/create")
def roles_create():
    return "hola"


@users_bp.route("/roles/<int:id>/edit")
def roles_edit(id):
    return "hola"
