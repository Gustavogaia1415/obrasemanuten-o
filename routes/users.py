from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User
from app import admin_required

users_bp = Blueprint('users', __name__, url_prefix='/usuarios')


@users_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.name).all()
    return render_template('users.html', users=users)


@users_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        if User.query.filter_by(email=email).first():
            flash('Já existe um usuário com esse e-mail.', 'error')
            return redirect(url_for('users.create'))

        u = User(
            name=request.form['name'],
            email=email,
            is_admin=(request.form.get('is_admin') == 'on'),
        )
        u.set_password(request.form['password'])
        db.session.add(u)
        db.session.commit()
        flash(f'Usuário criado! Repassa pra pessoa: e-mail {email} e a senha provisória que você definiu.', 'success')
        return redirect(url_for('users.index'))
    return render_template('user_form.html')


@users_bp.route('/<user_id>/redefinir-senha', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    u = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    if new_password:
        u.set_password(new_password)
        db.session.commit()
        flash(f'Senha de {u.name} redefinida. Repassa a nova senha pra pessoa.', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/<user_id>/alternar-acesso', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash('Você não pode desativar seu próprio acesso.', 'error')
        return redirect(url_for('users.index'))
    u.active = not u.active
    db.session.commit()
    flash(f'Acesso de {u.name} {"reativado" if u.active else "desativado"}.', 'success')
    return redirect(url_for('users.index'))
