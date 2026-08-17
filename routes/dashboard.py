from flask import Blueprint, render_template
from flask_login import login_required
from models import Store, ServiceOrder, MaintenanceCost

dashboard_bp = Blueprint('dashboard', __name__)

STATUS_LABELS = {
    'criada': 'Criada', 'em_andamento': 'Em Andamento',
    'aguardando_material': 'Aguardando Material', 'concluida': 'Concluída',
    'cancelada': 'Cancelada',
}


@dashboard_bp.route('/')
@login_required
def index():
    stores = Store.query.all()
    orders = ServiceOrder.query.all()
    costs = MaintenanceCost.query.all()

    os_scheduled = len([o for o in orders if o.status in ('criada', 'em_andamento', 'aguardando_material')])
    os_finished = len([o for o in orders if o.status == 'concluida'])
    finished_pct = round((os_finished / len(orders)) * 100, 1) if orders else 0

    status_counts = {}
    for o in orders:
        status_counts[o.status] = status_counts.get(o.status, 0) + 1
    status_data = [(STATUS_LABELS.get(k, k), v) for k, v in status_counts.items()]

    total_cost = sum(c.amount or 0 for c in costs)
    total_budget = sum(s.annual_budget or 0 for s in stores)
    budget_pct = round((total_cost / total_budget) * 100, 1) if total_budget else 0

    cost_by_store = []
    for s in stores:
        valor = sum(c.amount or 0 for c in costs if c.store_id == s.id)
        if valor > 0:
            cost_by_store.append((s.name, valor))
    cost_by_store.sort(key=lambda x: x[1], reverse=True)

    return render_template(
        'dashboard.html',
        os_scheduled=os_scheduled, os_finished=os_finished, finished_pct=finished_pct,
        total_stores=len(stores), status_data=status_data,
        total_cost=total_cost, total_budget=total_budget, budget_pct=budget_pct,
        cost_by_store=cost_by_store,
    )
