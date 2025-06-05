from flask import render_template, redirect, url_for, request, flash, session

from ..crm.services import CRMServices


from . import sales_bp


@sales_bp.route('/sales-approve-criteria')
def sales_approve_criteria():
    return render_template('sales/sales_approve_criteria.html')

