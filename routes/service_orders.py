from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from models import db, ServiceOrder, Store, Supplier
from app import admin_required

service_orders_bp = Blueprint('service_orders', __name__, url_prefix='/ordens-servico')

STATUS_LABELS = {
    'criada': 'Criada', 'em_andamento': 'Em Andamento',
    'aguardando_material': 'Aguardando Material', 'concluida': 'Concluída',
    'cancelada': 'Cancelada',
}
CATEGORY_LABELS = {
    'eletrica': 'Elétrica', 'hidraulica': 'Hidráulica', 'civil': 'Civil',
    'refrigeracao': 'Refrigeração', 'pintura': 'Pintura', 'equipamento': 'Equipamento',
    'limpeza': 'Limpeza', 'seguranca': 'Segurança', 'informatica': 'Informática',
    'personalizada': 'Personalizada', 'outros': 'Outros',
}


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, '%Y-%m-%d').date()


@service_orders_bp.route('/')
@login_required
def index():
    orders = ServiceOrder.query.order_by(ServiceOrder.created_date.desc()).all()
    return render_template('service_orders.html', orders=orders,
                            status_labels=STATUS_LABELS, category_labels=CATEGORY_LABELS)


@service_orders_bp.route('/nova', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    stores = Store.query.order_by(Store.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    if request.method == 'POST':
        count = ServiceOrder.query.count() + 1
        o = ServiceOrder(
            code=f"OS-{count:04d}",
            request_code=request.form.get('request_code'),
            store_id=request.form.get('store_id') or None,
            supplier_id=request.form.get('supplier_id') or None,
            title=request.form['title'],
            description=request.form.get('description'),
            category=request.form.get('category', 'outros'),
            custom_category=request.form.get('custom_category'),
            priority=request.form.get('priority', 'media'),
            estimated_cost=float(request.form.get('estimated_cost') or 0),
            start_date=_parse_date(request.form.get('start_date')),
            end_date=_parse_date(request.form.get('end_date')),
        )
        db.session.add(o)
        db.session.commit()
        flash('Ordem de serviço criada!', 'success')
        return redirect(url_for('service_orders.index'))
    return render_template('service_order_form.html', stores=stores, suppliers=suppliers,
                            category_labels=CATEGORY_LABELS)


@service_orders_bp.route('/<order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_status(order_id):
    o = ServiceOrder.query.get_or_404(order_id)
    o.status = request.form['status']
    if o.status == 'concluida':
        o.completed_date = datetime.utcnow().date()
    db.session.commit()
    flash('Status atualizado!', 'success')
    return redirect(url_for('service_orders.index'))
