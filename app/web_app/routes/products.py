from flask import Blueprint, render_template

products_bp = Blueprint(
    "products", __name__, url_prefix="/products", template_folder="../templates"
)


@products_bp.route("/index")
def product_index():
    return render_template("/products/index.html")


@products_bp.route("/")
def product_list():
    return render_template("/products/products/product_list.html")


@products_bp.route("/<int:id>")
def product_detail(id):
    return render_template("products/products/product_detail.html", id=id)


@products_bp.route("/create", methods=["GET"])
def create_product_view():
    return render_template("products/products/product_create.html")


# ----------------------------------------------------
# ------------------------DEsigns--------------------
@products_bp.route("/designs/<int:id>")
def design_detail(id):
    return render_template("products/products/product_detail.html", id=id)


@products_bp.route("/<int:product_id>/desings")
def design_list(product_id):
    return render_template("/products/designs/design_list.html", product_id=product_id)


@products_bp.route("/<int:product_id>/designs/<int:design_id>")
def product_design_detail(product_id, design_id):
    return render_template(
        "products/designs/design_detail.html",
        design_id=design_id,
        product_id=product_id,
    )


@products_bp.route("/designs/create", methods=["GET"])
def create_design_view():
    return render_template("products/products/product_wizard.html")


@products_bp.route("/<int:product_id>/designs/create", methods=["GET"])
def create_product_design_view(product_id):

    return render_template("products/designs/design_create.html", product_id=product_id)


@products_bp.route(
    "/<int:product_id>/designs/<int:design_id>/images/create", methods=["GET"]
)
def create_design_image(product_id, design_id):

    return render_template(
        "products/designs/_designImages.html",
        product_id=product_id,
        design_id=design_id,
    )


# ----------------------------------------------------
# ------------------------Variants--------------------


@products_bp.route("/<int:product_id>/designs/<int:design_id>/variants")
def variant_list(product_id, designs_id):
    return render_template(
        "/products/variants/variant_list.html",
        product_id=product_id,
        designs_id=designs_id,
    )


@products_bp.route(
    "/<int:product_id>/designs/<int:design_id>/variants/<int:variant_id>"
)
def variant_detail(product_id, design_id, variant_id):
    return render_template(
        "products/variants/variant_detail.html",
        product_id=product_id,
        design_id=design_id,
        variant_id=variant_id,
    )


@products_bp.route(
    "/<int:product_id>/designs/<int:design_id>/variants/create", methods=["GET"]
)
def create_variant_view(product_id, design_id):
    return render_template(
        "products/product_wizard.html", product_id=product_id, design_id=design_id
    )


# -------------------------------------------------------
# ------------------Lines---------------------------
@products_bp.route("/lines/create", methods=["GET"])
def create_line():
    return render_template("products/lines/line_create.html")


@products_bp.route("/lines")
def product_line_list():
    return render_template("/products/lines/line_list.html")


@products_bp.route("/lines/<int:id>")
def product_line_detail(id):
    return render_template("products/lines/line_detail.html", id=id)


# -------------------------------------------------------
# ------------------SubLines---------------------------
@products_bp.route("/sublines/create", methods=["GET"])
def create_subline():
    return render_template("products/sublines/subline_create.html")


@products_bp.route("/sublines")
def product_subline_list():
    return render_template("products/sublines/subline_list.html")


@products_bp.route("/sublines/<int:id>")
def product_subline_detail(id):
    return render_template("products/sublines/subline_detail.html", id=id)


# -------------------------------------------------------
# ------------------Collections--------------------------
@products_bp.route("/collections/create", methods=["GET"])
def create_collection():
    return render_template("products/collections/collection_create.html")


@products_bp.route("/collections")
def product_collection_list():
    return render_template("/products/collections/collection_list.html")


@products_bp.route("/collections/<int:id>")
def product_collection_detail(id):
    return render_template("products/collections/collection_detail.html", id=id)


# ----------------------------------------------------
# ------------------Sizes/tallas


@products_bp.route("/series/create", methods=["GET"])
def create_size():
    return render_template("products/sizes/series_create.html")


@products_bp.route("/series")
def size_list():
    return render_template("/products/sizes/series_list.html")


@products_bp.route("/series/<int:id>")
def size_detail(id):
    return render_template("products/sizes/series_detail.html", id=id)


# ----------------------------------------------------
# ------------------Colores-------------------------------------


@products_bp.route("/colors/create", methods=["GET"])
def create_color():
    return render_template("products/colors/colors_create.html")


@products_bp.route("/colors")
def color_list():
    return render_template("/products/colors/colors_list.html")


@products_bp.route("/colors/<int:id>")
def color_detail(id):
    return render_template("products/colors/colors_detail.html", id=id)
