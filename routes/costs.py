from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from models import db, MaintenanceCost, Store, Supplier, ServiceOrder
from app import admin_required

costs_bp = Blueprint('costs', __name__, url_prefix='/custos')

COST_TYPE_LABELS = {
    'material': 'Material', 'mao_de_obra': 'Mão de Obra',
    'servico_terceirizado': 'Serviço Terceirizado', 'emergencial': 'Emergencial',
    'outros': 'Outros',
}


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, '%Y-%m-%d').date()


@costs_bp.route('/')
@login_required
def index():
    costs = MaintenanceCost.query.order_by(MaintenanceCost.created_date.desc()).all()
    stores = Store.query.order_by(Store.name).all()

    total_geral = sum(c.amount or 0 for c in costs)
    total_budget = sum(s.annual_budget or 0 for s in stores)

    by_type = {}
    for c in costs:
        by_type[c.cost_type or 'outros'] = by_type.get(c.cost_type or 'outros', 0) + (c.amount or 0)

    by_store = {}
    for c in costs:
        key = c.store.code if c.store else '?'
        by_store[key] = by_store.get(key, 0) + (c.amount or 0)

    return render_template(
        'costs.html', costs=costs, cost_type_labels=COST_TYPE_LABELS,
        total_geral=total_geral, total_budget=total_budget,
        by_type=by_type, by_store=by_store,
    )


@costs_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    stores = Store.query.order_by(Store.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    orders = ServiceOrder.query.order_by(ServiceOrder.code).all()
    if request.method == 'POST':
        c = MaintenanceCost(
            description=request.form['description'],
            store_id=request.form['store_id'],
            service_order_code=request.form.get('service_order_code'),
            request_code=request.form.get('request_code'),
            supplier_id=request.form.get('supplier_id') or None,
            cost_type=request.form.get('cost_type', 'outros'),
            amount=float(request.form.get('amount') or 0),
            date=_parse_date(request.form.get('date')),
            invoice_number=request.form.get('invoice_number'),
            notes=request.form.get('notes'),
        )
        db.session.add(c)
        db.session.commit()
        flash('Custo registrado!', 'success')
        return redirect(url_for('costs.index'))
    return render_template('cost_form.html', stores=stores, suppliers=suppliers, orders=orders,
                            cost_type_labels=COST_TYPE_LABELS)
