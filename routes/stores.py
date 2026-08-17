from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Store
from app import admin_required

stores_bp = Blueprint('stores', __name__, url_prefix='/lojas')


@stores_bp.route('/')
@login_required
def index():
    stores = Store.query.order_by(Store.name).all()
    return render_template('stores.html', stores=stores)


@stores_bp.route('/nova', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        s = Store(
            code=request.form['code'],
            name=request.form['name'],
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            manager=request.form.get('manager'),
            status=request.form.get('status', 'ativa'),
            monthly_budget=float(request.form.get('monthly_budget') or 0),
            annual_budget=float(request.form.get('annual_budget') or 0),
        )
        db.session.add(s)
        db.session.commit()
        flash('Loja cadastrada!', 'success')
        return redirect(url_for('stores.index'))
    return render_template('store_form.html', store=None)


@stores_bp.route('/<store_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(store_id):
    s = Store.query.get_or_404(store_id)
    if request.method == 'POST':
        s.code = request.form['code']
        s.name = request.form['name']
        s.address = request.form.get('address')
        s.city = request.form.get('city')
        s.state = request.form.get('state')
        s.phone = request.form.get('phone')
        s.manager = request.form.get('manager')
        s.status = request.form.get('status', 'ativa')
        s.monthly_budget = float(request.form.get('monthly_budget') or 0)
        s.annual_budget = float(request.form.get('annual_budget') or 0)
        db.session.commit()
        flash('Loja atualizada!', 'success')
        return redirect(url_for('stores.index'))
    return render_template('store_form.html', store=s)


@stores_bp.route('/<store_id>/excluir', methods=['POST'])
@login_required
@admin_required
def delete(store_id):
    s = Store.query.get_or_404(store_id)
    db.session.delete(s)
    db.session.commit()
    flash('Loja removida!', 'success')
    return redirect(url_for('stores.index'))
