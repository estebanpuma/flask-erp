from flask import Blueprint, render_template

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@clients_bp.route("/")
def client_list():
    return render_template("/clients/client_list.html")


@clients_bp.route("/create")
def client_create():
    return render_template("/clients/client_create.html")


@clients_bp.route("/<int:id>")
def client_detail(id):
    return render_template("/clients/client_detail.html", id=id)


@clients_bp.route("/<int:id>/edit")
def client_edit(id):
    return render_template("clients/client_edit.html", id=id)
